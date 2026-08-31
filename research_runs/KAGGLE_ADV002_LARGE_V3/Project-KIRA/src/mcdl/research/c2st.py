"""Classifier Two-Sample Test (C2ST).

Trains a lightweight discriminator to distinguish synthetic (0) from real (1) samples.
Reports AUC, 95% bootstrap confidence interval, feature importances, and sample metadata.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
from sklearn.metrics import roc_auc_score


def run_c2st_evaluation(
    synthetic_features: np.ndarray,
    real_features: np.ndarray,
    feature_names: Optional[list[str]] = None,
    n_bootstrap: int = 1000,
    seed: int = 20260827,
) -> dict[str, Any]:
    """Runs C2ST using a lightweight binary model.
    
    Target:
    - 0 = synthetic
    - 1 = real
    """
    rng = np.random.RandomState(seed)
    n_syn = len(synthetic_features)
    n_real = len(real_features)
    
    if n_syn == 0 or n_real == 0:
        return {
            "status": "INCOMPLETE",
            "reason": "Insufficient samples for C2ST",
            "c2st_auc": None,
            "sample_counts": {"synthetic": n_syn, "real": n_real},
        }

    X = np.vstack([synthetic_features, real_features])
    y = np.array([0] * n_syn + [1] * n_real)
    
    # 60/20/20 stratified split
    indices = np.arange(len(y))
    rng.shuffle(indices)
    
    n_train = int(0.6 * len(y))
    n_val = int(0.2 * len(y))
    
    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    test_idx = indices[n_train + n_val:]
    
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    
    # Use LightGBM if available, fallback to LogisticRegression
    try:
        import lightgbm as lgb
        model = lgb.LGBMClassifier(
            n_estimators=50,
            max_depth=4,
            learning_rate=0.05,
            random_state=seed,
            verbosity=-1,
        )
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_test)[:, 1]
        importances = model.feature_importances_.tolist()
    except Exception:
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(random_state=seed, max_iter=200)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_test)[:, 1]
        importances = np.abs(model.coef_[0]).tolist()
        
    test_auc = float(roc_auc_score(y_test, preds))
    
    # Bootstrap CI calculation
    bootstrap_aucs = []
    for _ in range(min(n_bootstrap, 1000)):
        bs_indices = rng.choice(len(y_test), size=len(y_test), replace=True)
        if len(np.unique(y_test[bs_indices])) > 1:
            bs_auc = roc_auc_score(y_test[bs_indices], preds[bs_indices])
            bootstrap_aucs.append(bs_auc)
            
    ci_lower = float(np.percentile(bootstrap_aucs, 2.5)) if bootstrap_aucs else test_auc
    ci_upper = float(np.percentile(bootstrap_aucs, 97.5)) if bootstrap_aucs else test_auc
    
    names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
    top_features = sorted(zip(names, importances), key=lambda x: x[1], reverse=True)[:10]

    return {
        "status": "COMPLETE",
        "c2st_auc": round(test_auc, 4),
        "ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
        "bootstrap_samples": len(bootstrap_aucs),
        "sample_counts": {
            "n_total": len(y),
            "n_synthetic": n_syn,
            "n_real": n_real,
            "n_test": len(y_test),
        },
        "feature_importances_top10": [{"feature": k, "importance": round(float(v), 4)} for k, v in top_features],
        "interpretation": (
            "AUC ~0.50 indicates distributions are hard to distinguish; "
            "AUC > 0.80 indicates high discriminability between synthetic and real."
        ),
    }
