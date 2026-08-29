"""Multi-Round Adversarial Coevolution Loop.

Executes 4 rounds of Blue defense vs Red attack search, replay hardening,
and honest seen vs held-out generalization measurement without test contamination.
"""

from __future__ import annotations

from dataclasses import dataclass
import polars as pl

from mcdl.blue.metrics import evaluate_predictions
from mcdl.blue.model import BlueDetector
from mcdl.blue.split import temporal_split
from mcdl.features.batch import compute_batch_features
from mcdl.features.stream import StreamingFeatureExtractor
from mcdl.loop.challenger import ChallengerTrainer, evaluate_promotion
from mcdl.loop.metrics import GeneralisationReport, compute_generalisation_metrics
from mcdl.loop.replay import ReplayBuffer, ReplayRecord
from mcdl.loop.split import split_seen_heldout
from mcdl.red.evaluator import CANONICAL_FAMILIES, evaluate_red_attacks
from mcdl.red.search import AttackProvenance, RedSearchEngine
from mcdl.schemas import AttackFamily, BlueMetrics, Decision, RoundResult, Transaction
from mcdl.world.generator import WorldResult


@dataclass
class CoevolutionResult:
    rounds: list[RoundResult]
    generalisation_reports: list[GeneralisationReport]
    replay_buffer: ReplayBuffer
    final_champion: BlueDetector


class CoevolutionLoop:
    """Orchestrates 4-round adversarial coevolution experiment with strict test isolation."""

    def __init__(
        self,
        n_rounds: int = 4,
        budgets: list[int] | None = None,
        families: list[AttackFamily] | None = None,
        seed: int = 20260827,
    ) -> None:
        self.n_rounds = n_rounds
        self.budgets = budgets or [1, 5, 20, 100]
        self.families = families or CANONICAL_FAMILIES
        self.seed = seed

    def run(
        self,
        all_transactions: list[Transaction],
        world: WorldResult,
        feature_df: pl.DataFrame,
    ) -> CoevolutionResult:
        """Executes the full 4-round coevolution loop."""
        # 1. Temporal split
        split = temporal_split(feature_df, train_ratio=0.70, valid_ratio=0.15)
        train_end_idx = len(split.train_df)
        test_start_idx = len(split.train_df) + len(split.valid_df)

        # 2. Initialize Round 0 Baseline Blue
        champion = BlueDetector(n_estimators=30, max_depth=3, learning_rate=0.05, random_state=self.seed)
        champion.fit(split.train_df, split.valid_df)

        replay_buffer = ReplayBuffer()
        rounds_history: list[RoundResult] = []
        gen_reports: list[GeneralisationReport] = []

        trainer = ChallengerTrainer(
            n_estimators=30,
            max_depth=3,
            learning_rate=0.05,
            random_state=self.seed,
        )

        for r in range(self.n_rounds):
            round_seed = self.seed + r * 1000

            # 3. Hardening pool: Red attacks blocked fraud in TRAIN split only
            # This ensures replay records NEVER contain test transactions
            red_metrics_train, train_prov_log = evaluate_red_attacks(
                all_transactions=all_transactions[:train_end_idx],
                test_start_idx=0,
                detector=champion,
                customers=world.customers,
                merchants=world.merchants,
                mandates=world.mandates,
                budgets=self.budgets,
                families=self.families,
                seed=round_seed,
            )

            # Partition train evasions into Seen (for hardening) vs Held-out (for generalization)
            split_atks = split_seen_heldout(train_prov_log, seen_ratio=0.5, seed=round_seed)

            # 4. Ingest Seen evasions into replay buffer
            for prov in split_atks.seen:
                if prov.success and prov.best_candidate is not None:
                    ext = StreamingFeatureExtractor(customers=world.customers)
                    cand_feats = ext.extract(prov.best_candidate)
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
                        )
                    )

            # 5. Evaluate Champion on Validation set for Blue Metrics
            val_eval = champion.evaluate_split(split)["lgbm_calibrated_valid"]
            raw_preds = champion.predict_raw_proba(split.valid_df)
            val_preds = champion.predict_calibrated_proba(split.valid_df)
            val_actions = [
                champion.router.route(
                    txn_id=f"val_{i}",
                    amount=100.0,
                    risk_score=float(raw_preds[i]),
                    calibrated_score=float(val_preds[i]),
                ).decision.value
                for i in range(len(val_preds))
            ]
            decision_counts = {
                "ALLOW": val_actions.count("ALLOW"),
                "STEP_UP": val_actions.count("STEP_UP"),
                "BLOCK": val_actions.count("BLOCK"),
            }

            blue_metrics = BlueMetrics(
                pr_auc=val_eval.pr_auc,
                roc_auc=val_eval.roc_auc,
                precision=val_eval.precision,
                recall=val_eval.recall,
                fpr=val_eval.fpr,
                ece=val_eval.ece,
                brier=val_eval.brier_score,
                decision_counts=decision_counts,
            )

            if r == 0:
                report_r0 = compute_generalisation_metrics(
                    baseline_seen=split_atks.seen,
                    baseline_heldout=split_atks.heldout,
                    challenger_seen=split_atks.seen,
                    challenger_heldout=split_atks.heldout,
                    challenger_blue_metrics=blue_metrics,
                    decision_counts=decision_counts,
                )
                gen_reports.append(report_r0)

                rounds_history.append(
                    RoundResult(
                        round_index=0,
                        champion_version="blue_r0_baseline",
                        challenger_version=None,
                        promoted=True,
                        promotion_reasons=["INITIAL_BASELINE_MODEL"],
                        blue=blue_metrics,
                        red=report_r0.red_metrics,
                    )
                )
            else:
                # Rounds 1..3: Train Challenger on Base Train + Replay Buffer
                challenger = trainer.train(
                    base_train_df=split.train_df,
                    valid_df=split.valid_df,
                    replay_buffer=replay_buffer,
                    round_idx=r,
                )

                # Re-score seen and heldout attacks against Challenger
                chal_seen_atks = []
                for p in split_atks.seen:
                    if p.best_candidate is not None:
                        ext = StreamingFeatureExtractor(customers=world.customers)
                        f = ext.extract(p.best_candidate)
                        dec = challenger.score_transaction(p.best_candidate, f, mandates=world.mandates)
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
                            med=p.med,
                            success=(dec.decision == Decision.ALLOW),
                            rejection_reasons=p.rejection_reasons,
                            best_candidate=p.best_candidate,
                        )
                        chal_seen_atks.append(p_chal)

                chal_heldout_atks = []
                for p in split_atks.heldout:
                    if p.best_candidate is not None:
                        ext = StreamingFeatureExtractor(customers=world.customers)
                        f = ext.extract(p.best_candidate)
                        dec = challenger.score_transaction(p.best_candidate, f, mandates=world.mandates)
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
                            med=p.med,
                            success=(dec.decision == Decision.ALLOW),
                            rejection_reasons=p.rejection_reasons,
                            best_candidate=p.best_candidate,
                        )
                        chal_heldout_atks.append(p_chal)

                chal_report = compute_generalisation_metrics(
                    baseline_seen=split_atks.seen,
                    baseline_heldout=split_atks.heldout,
                    challenger_seen=chal_seen_atks,
                    challenger_heldout=chal_heldout_atks,
                    challenger_blue_metrics=blue_metrics,
                    decision_counts=decision_counts,
                )
                gen_reports.append(chal_report)

                # Evaluate promotion
                base_seen_asr = gen_reports[0].seen_asr
                base_heldout_asr = gen_reports[0].heldout_asr
                allow_rate = chal_report.policy_distribution.get("ALLOW", 0.95)

                promoted, reasons = evaluate_promotion(
                    baseline_seen_asr=base_seen_asr,
                    challenger_seen_asr=chal_report.seen_asr,
                    baseline_heldout_asr=base_heldout_asr,
                    challenger_heldout_asr=chal_report.heldout_asr,
                    fpr=blue_metrics.fpr or 0.0,
                    allow_rate=allow_rate,
                    pr_auc=blue_metrics.pr_auc or 1.0,
                )

                if promoted:
                    champion = challenger

                rounds_history.append(
                    RoundResult(
                        round_index=r,
                        champion_version=f"blue_r{r}",
                        challenger_version=f"challenger_r{r}",
                        promoted=promoted,
                        promotion_reasons=reasons,
                        blue=blue_metrics,
                        red=chal_report.red_metrics,
                    )
                )

        return CoevolutionResult(
            rounds=rounds_history,
            generalisation_reports=gen_reports,
            replay_buffer=replay_buffer,
            final_champion=champion,
        )
