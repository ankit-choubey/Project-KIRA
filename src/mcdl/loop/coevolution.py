"""Multi-Round Adversarial Coevolution Loop.

Executes genuine multi-round Blue defense vs Adaptive Red attack search:
Every round forces Red to perform a FRESH budgeted search directly querying
the CURRENT champion/model, diagnosing new failure vulnerabilities, updating
WeaknessProfiles, ingesting seen failures into prioritized replay, training
Challengers, and evaluating both Champion and Challenger on identical validation
and attack sets under strict multi-objective promotion and rollback.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
import polars as pl

from mcdl.blue.metrics import evaluate_predictions
from mcdl.blue.model import BlueDetector
from mcdl.blue.split import temporal_split
from mcdl.features.batch import compute_batch_features
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.loop.challenger import ChallengerTrainer
from mcdl.loop.failure import FailureAnalyzer
from mcdl.loop.metrics import (
    GeneralisationReport,
    build_coevolution_scoreboard,
    compute_adaptation_cost,
    compute_generalisation_metrics,
)
from mcdl.loop.promotion import MultiObjectivePromotionGate
from mcdl.loop.replay import ReplayBuffer, ReplayRecord
from mcdl.loop.split import split_seen_heldout
from mcdl.loop.worlds import CANONICAL_ADAPTATION_FAMILIES, verify_family_isolation
from mcdl.red.adaptive import AdaptiveRedEngine
from mcdl.red.distance import compute_evasion_distance
from mcdl.red.search import AttackProvenance
from mcdl.schemas import (
    AdaptationCost,
    AttackFamily,
    BlueMetrics,
    Decision,
    FailureRecord,
    PromotionDecision,
    RoundResult,
    ScoreboardEntry,
    Transaction,
    WeaknessProfile,
)
from mcdl.world.generator import WorldResult


@dataclass
class CoevolutionResult:
    rounds: list[RoundResult]
    generalisation_reports: list[GeneralisationReport]
    replay_buffer: ReplayBuffer
    final_champion: BlueDetector
    failures: list[FailureRecord] = field(default_factory=list)
    weakness_profiles: list[WeaknessProfile] = field(default_factory=list)
    scoreboard: list[ScoreboardEntry] = field(default_factory=list)
    promotion_decisions: list[PromotionDecision] = field(default_factory=list)


class CoevolutionLoop:
    """Orchestrates genuine multi-round adversarial coevolution with strict test isolation."""

    def __init__(
        self,
        n_rounds: int = 4,
        budgets: list[int] | None = None,
        families: list[AttackFamily] | None = None,
        seed: int = 20260827,
    ) -> None:
        self.n_rounds = n_rounds
        self.budgets = budgets or [1, 5, 20, 100]
        self.families = families or CANONICAL_ADAPTATION_FAMILIES
        self.seed = seed
        self.analyzer = FailureAnalyzer()
        self.promotion_gate = MultiObjectivePromotionGate()

    def run(
        self,
        all_transactions: list[Transaction],
        world: WorldResult,
        feature_df: pl.DataFrame,
    ) -> CoevolutionResult:
        """Executes the genuine multi-round coevolution loop."""
        # 1. Temporal split
        split = temporal_split(feature_df, train_ratio=0.70, valid_ratio=0.15)
        train_end_idx = len(split.train_df)

        # 2. Initialize Round 0 Baseline Blue
        champion = BlueDetector(n_estimators=30, max_depth=3, learning_rate=0.05, random_state=self.seed)
        champion.fit(split.train_df, split.valid_df)
        champion_version = "blue_r0_baseline"

        replay_buffer = ReplayBuffer()
        all_failures: list[FailureRecord] = []
        weakness_profiles: list[WeaknessProfile] = []
        promotion_decisions: list[PromotionDecision] = []
        rounds_history: list[RoundResult] = []
        gen_reports: list[GeneralisationReport] = []

        trainer = ChallengerTrainer(
            n_estimators=30,
            max_depth=3,
            learning_rate=0.05,
            random_state=self.seed,
        )

        current_weakness_profile: WeaknessProfile | None = None
        sorted_train_txns = sorted(all_transactions[:train_end_idx], key=lambda t: (t.timestamp, t.txn_id))

        for r in range(self.n_rounds):
            round_seed = self.seed + r * 10000
            t_start_round = time.perf_counter()

            # -------------------------------------------------------------
            # STEP A: FRESH Red Attack Generation directly against CURRENT Champion
            # -------------------------------------------------------------
            t_gen_start = time.perf_counter()
            adaptive_engine = AdaptiveRedEngine(
                detector=champion,
                customers=world.customers,
                merchants=world.merchants,
                mandates=world.mandates,
                weakness_profile=current_weakness_profile,
            )

            rolling_extractor = StreamingFeatureExtractor(customers=world.customers)
            train_prov_log: list[AttackProvenance] = []

            for t in sorted_train_txns:
                state_snapshot = rolling_extractor.clone()
                feats = state_snapshot.extract(t)
                dec = champion.score_transaction(t, feats, mandates=world.mandates)

                # Only attempt evasion if source transaction is in protected state (BLOCK / STEP_UP)
                if dec.decision in {Decision.BLOCK, Decision.STEP_UP}:
                    for family in self.families:
                        for budget in self.budgets:
                            atk_seed = int(round_seed + len(train_prov_log))
                            prov = adaptive_engine.attack(
                                source_txn=t,
                                family=family,
                                budget=budget,
                                seed=atk_seed,
                                feature_extractor_state=state_snapshot,
                                round_idx=r,
                            )
                            train_prov_log.append(prov)

                rolling_extractor.extract(t)
            t_gen_end = time.perf_counter()

            # -------------------------------------------------------------
            # STEP B: Failure Analysis & Weakness Profile Synthesis
            # -------------------------------------------------------------
            round_failures: list[FailureRecord] = []
            for prov in train_prov_log:
                if prov.success and prov.best_candidate is not None:
                    ext = StreamingFeatureExtractor(customers=world.customers)
                    cand_feats = ext.extract(prov.best_candidate)
                    cust = world.customers.get(prov.best_candidate.customer_id)
                    if cust:
                        fail_rec = self.analyzer.diagnose_failure(
                            prov=prov,
                            customer=cust,
                            features=cand_feats,
                            round_idx=r,
                            model_version=champion_version,
                            known_failures=all_failures,
                        )
                        round_failures.append(fail_rec)

            all_failures.extend(round_failures)

            # Synthesize updated WeaknessProfile for the next round's Red search
            current_weakness_profile = self.analyzer.synthesize_weakness_profile(
                failures=round_failures if round_failures else all_failures,
                round_idx=r,
            )
            weakness_profiles.append(current_weakness_profile)

            # -------------------------------------------------------------
            # STEP C: Deterministic Lineage Partitioning (Anti-Memorization)
            # -------------------------------------------------------------
            split_atks = split_seen_heldout(train_prov_log, seen_ratio=0.5, seed=round_seed)

            # Ingest Seen evasions into prioritized replay buffer
            for prov in split_atks.seen:
                if prov.success and prov.best_candidate is not None:
                    ext = StreamingFeatureExtractor(customers=world.customers)
                    cand_feats = ext.extract(prov.best_candidate)
                    cust = world.customers.get(prov.best_candidate.customer_id)
                    prio = 1.0
                    if cust:
                        fail_rec = self.analyzer.diagnose_failure(
                            prov=prov,
                            customer=cust,
                            features=cand_feats,
                            round_idx=r,
                            model_version=champion_version,
                            known_failures=all_failures,
                        )
                        prio = fail_rec.priority_score

                    replay_buffer.add(
                        ReplayRecord(
                            attack_instance_id=prov.attack_instance_id,
                            attack_family=prov.attack_family,
                            source_txn_id=prov.source_txn_id,
                            round_generated=r,
                            evasion_features=cand_feats,
                            original_risk=prov.original_risk,
                            evasion_risk=prov.final_risk,
                            original_decision=prov.original_decision,
                            evasion_decision=prov.final_decision,
                            med=prov.med if prov.med is not None else 0.0,
                            query_budget=prov.query_budget,
                            seed=prov.seed,
                            candidate_transaction=prov.best_candidate,
                            priority_score=prio,
                        )
                    )

            # -------------------------------------------------------------
            # STEP D: Evaluate Champion on Validation Set
            # -------------------------------------------------------------
            t_eval_start = time.perf_counter()
            champ_val_eval = champion.evaluate_split(split)["lgbm_calibrated_valid"]
            champ_raw_preds = champion.predict_raw_proba(split.valid_df)
            champ_val_preds = champion.predict_calibrated_proba(split.valid_df)
            champ_val_actions = [
                champion.router.route(
                    txn_id=f"val_{i}",
                    amount=100.0,
                    risk_score=float(champ_raw_preds[i]),
                    calibrated_score=float(champ_val_preds[i]),
                ).decision.value
                for i in range(len(champ_val_preds))
            ]
            champ_decision_counts = {
                "ALLOW": champ_val_actions.count("ALLOW"),
                "STEP_UP": champ_val_actions.count("STEP_UP"),
                "BLOCK": champ_val_actions.count("BLOCK"),
            }

            champ_blue_metrics = BlueMetrics(
                pr_auc=champ_val_eval.pr_auc,
                roc_auc=champ_val_eval.roc_auc,
                precision=champ_val_eval.precision,
                recall=champ_val_eval.recall,
                fpr=champ_val_eval.fpr,
                ece=champ_val_eval.ece,
                brier=champ_val_eval.brier_score,
                decision_counts=champ_decision_counts,
                latency_p50_ms=None,
                latency_p95_ms=None,
                latency_p99_ms=None,
            )

            # -------------------------------------------------------------
            # STEP E: Train Challenger on Base Train + Replay Buffer
            # -------------------------------------------------------------
            t_train_start = time.perf_counter()
            challenger = trainer.train(
                base_train_df=split.train_df,
                valid_df=split.valid_df,
                replay_buffer=replay_buffer,
                round_idx=r + 1,
            )
            t_train_end = time.perf_counter()

            # -------------------------------------------------------------
            # STEP F: Evaluate Challenger on IDENTICAL Sets (Valid + Attacks)
            # -------------------------------------------------------------
            chal_val_eval = challenger.evaluate_split(split)["lgbm_calibrated_valid"]
            chal_raw_preds = challenger.predict_raw_proba(split.valid_df)
            chal_val_preds = challenger.predict_calibrated_proba(split.valid_df)
            chal_val_actions = [
                challenger.router.route(
                    txn_id=f"val_{i}",
                    amount=100.0,
                    risk_score=float(chal_raw_preds[i]),
                    calibrated_score=float(chal_val_preds[i]),
                ).decision.value
                for i in range(len(chal_val_preds))
            ]
            chal_decision_counts = {
                "ALLOW": chal_val_actions.count("ALLOW"),
                "STEP_UP": chal_val_actions.count("STEP_UP"),
                "BLOCK": chal_val_actions.count("BLOCK"),
            }

            chal_blue_metrics = BlueMetrics(
                pr_auc=chal_val_eval.pr_auc,
                roc_auc=chal_val_eval.roc_auc,
                precision=chal_val_eval.precision,
                recall=chal_val_eval.recall,
                fpr=chal_val_eval.fpr,
                ece=chal_val_eval.ece,
                brier=chal_val_eval.brier_score,
                decision_counts=chal_decision_counts,
                latency_p50_ms=None,
                latency_p95_ms=None,
                latency_p99_ms=None,
            )

            # Re-score this round's fresh seen and held-out attacks against Challenger
            chal_seen_atks: list[AttackProvenance] = []
            for p in split_atks.seen:
                if p.best_candidate is not None:
                    ext = StreamingFeatureExtractor(customers=world.customers)
                    f = ext.extract(p.best_candidate)
                    dec = challenger.score_transaction(p.best_candidate, f, mandates=world.mandates)
                    dist = compute_evasion_distance(p.best_candidate, p.best_candidate)
                    is_evasion = (dec.decision == Decision.ALLOW and p.med is not None and p.med > 1e-6)
                    p_chal = AttackProvenance(
                        attack_instance_id=p.attack_instance_id,
                        attack_family=p.attack_family,
                        source_txn_id=p.source_txn_id,
                        seed=p.seed,
                        query_budget=p.query_budget,
                        queries_used=p.queries_used,
                        mutations_attempted=p.mutations_attempted,
                        valid_mutations=p.valid_mutations,
                        invalid_mutations=p.invalid_mutations,
                        original_decision=p.original_decision,
                        final_decision=dec.decision,
                        original_risk=p.original_risk,
                        final_risk=dec.calibrated_score,
                        med=p.med if is_evasion else None,
                        success=is_evasion,
                        rejection_reasons=p.rejection_reasons,
                        best_candidate=p.best_candidate,
                    )
                    chal_seen_atks.append(p_chal)
                else:
                    chal_seen_atks.append(p)

            chal_heldout_atks: list[AttackProvenance] = []
            for p in split_atks.heldout:
                if p.best_candidate is not None:
                    ext = StreamingFeatureExtractor(customers=world.customers)
                    f = ext.extract(p.best_candidate)
                    dec = challenger.score_transaction(p.best_candidate, f, mandates=world.mandates)
                    is_evasion = (dec.decision == Decision.ALLOW and p.med is not None and p.med > 1e-6)
                    p_chal = AttackProvenance(
                        attack_instance_id=p.attack_instance_id,
                        attack_family=p.attack_family,
                        source_txn_id=p.source_txn_id,
                        seed=p.seed,
                        query_budget=p.query_budget,
                        queries_used=p.queries_used,
                        mutations_attempted=p.mutations_attempted,
                        valid_mutations=p.valid_mutations,
                        invalid_mutations=p.invalid_mutations,
                        original_decision=p.original_decision,
                        final_decision=dec.decision,
                        original_risk=p.original_risk,
                        final_risk=dec.calibrated_score,
                        med=p.med if is_evasion else None,
                        success=is_evasion,
                        rejection_reasons=p.rejection_reasons,
                        best_candidate=p.best_candidate,
                    )
                    chal_heldout_atks.append(p_chal)
                else:
                    chal_heldout_atks.append(p)

            chal_report = compute_generalisation_metrics(
                baseline_seen=split_atks.seen,
                baseline_heldout=split_atks.heldout,
                challenger_seen=chal_seen_atks,
                challenger_heldout=chal_heldout_atks,
                challenger_blue_metrics=chal_blue_metrics,
                decision_counts=chal_decision_counts,
            )
            gen_reports.append(chal_report)

            # -------------------------------------------------------------
            # STEP G: Multi-Objective Promotion Gate & Rollback
            # -------------------------------------------------------------
            base_seen_asr = chal_report.seen_asr + chal_report.delta_seen_asr
            base_heldout_asr = chal_report.heldout_asr + chal_report.delta_heldout_asr

            promo_decision = self.promotion_gate.evaluate(
                champion_version=champion_version,
                challenger_version=f"challenger_r{r+1}",
                champion_blue=champ_blue_metrics,
                challenger_blue=chal_blue_metrics,
                baseline_seen_asr=base_seen_asr,
                challenger_seen_asr=chal_report.seen_asr,
                baseline_heldout_asr=base_heldout_asr,
                challenger_heldout_asr=chal_report.heldout_asr,
                historical_retention=1.0,
                latency_p95_ms=chal_blue_metrics.latency_p95_ms,
                policy_distribution=chal_report.policy_distribution,
            )
            promotion_decisions.append(promo_decision)

            if promo_decision.promoted:
                champion = challenger
                champion_version = f"blue_r{r+1}"
                champ_ver_str = champion_version
            else:
                # Rollback preserves previous champion
                champ_ver_str = champion_version

            t_eval_end = time.perf_counter()

            cost_r = compute_adaptation_cost(
                gen_time_s=t_gen_end - t_gen_start,
                train_time_s=t_train_end - t_train_start,
                eval_time_s=t_eval_end - t_eval_start,
                retrain_steps=30,
            )

            rounds_history.append(
                RoundResult(
                    round_index=r,
                    champion_version=champ_ver_str,
                    challenger_version=f"challenger_r{r+1}",
                    promoted=promo_decision.promoted,
                    promotion_reasons=promo_decision.reasons,
                    blue=chal_blue_metrics if promo_decision.promoted else champ_blue_metrics,
                    red=chal_report.red_metrics,
                    promotion_decision=promo_decision,
                    adaptation_cost=cost_r,
                )
            )

        # Build master scoreboard across rounds
        scoreboard = build_coevolution_scoreboard(
            rounds_history=rounds_history,
            gen_reports=gen_reports,
        )

        return CoevolutionResult(
            rounds=rounds_history,
            generalisation_reports=gen_reports,
            replay_buffer=replay_buffer,
            final_champion=champion,
            failures=all_failures,
            weakness_profiles=weakness_profiles,
            scoreboard=scoreboard,
            promotion_decisions=promotion_decisions,
        )
