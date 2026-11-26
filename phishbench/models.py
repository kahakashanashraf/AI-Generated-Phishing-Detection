"""Classical detectors (D1–D3) and the linear paired-consistency objective (M2) for Study 2 (pre-registration §4–§5).

The TF-IDF vectoriser is identical to N05, so Study 1 and Study 2 features are comparable.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.optimize import minimize
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import GroupKFold
from sklearn.naive_bayes import ComplementNB
from sklearn.svm import LinearSVC

TFIDF_KW = dict(ngram_range=(1, 2), min_df=2, max_df=0.98, sublinear_tf=True, max_features=120000,
                strip_accents="unicode")


def make_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(**TFIDF_KW)


def balanced_weights(y, base=None) -> np.ndarray:
    """class_weight='balanced' expressed as sample weights, multiplied by any base (per-parent) weights."""
    y = np.asarray(y)
    w = np.ones(len(y)) if base is None else np.asarray(base, dtype=float).copy()
    n = len(y)
    for c in (0, 1):
        m = y == c
        if m.any():
            w[m] *= n / (2.0 * m.sum())   # identical to sklearn: n_samples / (n_classes * count_c)
    return w


def fit_d1_lr(X, y, w, C: float, seed: int):
    return LogisticRegression(max_iter=3000, C=C, random_state=seed).fit(X, y, sample_weight=balanced_weights(y, w))


def fit_d2_svm(X, y, w, seed: int):
    """N05's calibrated LinearSVC. Balanced class weights enter through the sample weights."""
    clf = CalibratedClassifierCV(LinearSVC(random_state=seed, max_iter=10000), method="sigmoid", cv=3)
    return clf.fit(X, y, sample_weight=balanced_weights(y, w))


def fit_d3_cnb(X, y, w, alpha: float):
    return ComplementNB(alpha=alpha).fit(X, y, sample_weight=balanced_weights(y, w))


def grouped_cv_select(make_and_fit, grid, X, y, w, groups, seed: int, folds: int = 5):
    """Choose a hyperparameter by mean average precision over GroupKFold on TRAINING data only."""
    scores = {}
    gkf = GroupKFold(n_splits=folds)
    for g in grid:
        aps = []
        for tr, te in gkf.split(X, y, groups):
            m = make_and_fit(X[tr], y[tr], None if w is None else w[tr], g)
            aps.append(average_precision_score(y[te], m.predict_proba(X[te])[:, 1]))
        scores[g] = float(np.mean(aps))
    best = max(grid, key=lambda g: (scores[g], -grid.index(g)))
    return best, scores


class ConsistencyLinear:
    """Squared-hinge linear classifier with a paired-consistency penalty (M2 for D2).

    It minimises
        mean_i w_i * max(0, 1 - y~_i f(x_i))^2 + alpha/2 ||beta||^2 + lam * mean_k (f(x_parent_k) - f(x_rewrite_k))^2
    where f(x) = x.beta + b and y~ is in {-1, +1}, using L-BFGS. alpha = 1/(C*n) matches LinearSVC(C) scaling.
    A sigmoid (Platt) map is fitted afterwards on the validation set. Being monotone, it does not change any
    decision at a validation-selected threshold.
    """

    def __init__(self, lam: float = 0.2, C: float = 1.0, max_iter: int = 500):
        self.lam, self.C, self.max_iter = lam, C, max_iter

    def fit(self, X, y, w, P, R):
        """X: training matrix; P, R: matrices of paired parent and rewrite rows (same number of rows)."""
        X = sparse.csr_matrix(X)
        n, d = X.shape
        yt = np.where(np.asarray(y) == 1, 1.0, -1.0)
        sw = balanced_weights(y, w)
        sw = sw / sw.mean()
        D = sparse.csr_matrix(P) - sparse.csr_matrix(R) if P is not None and P.shape[0] else None
        m = D.shape[0] if D is not None else 0
        alpha = 1.0 / (self.C * n)

        def fg(theta):
            beta, b = theta[:d], theta[d]
            f = X @ beta + b
            margin = 1 - yt * f
            act = margin > 0
            loss = np.sum(sw[act] * margin[act] ** 2) / n
            g_f = np.zeros(n)
            g_f[act] = -2 * sw[act] * margin[act] * yt[act] / n
            g_beta = X.T @ g_f + alpha * beta
            g_b = g_f.sum()
            loss += 0.5 * alpha * beta @ beta
            if m:
                dd = D @ beta
                loss += self.lam * np.mean(dd ** 2)
                g_beta = g_beta + D.T @ (2 * self.lam * dd / m)
            return loss, np.r_[g_beta, g_b]

        res = minimize(fg, np.zeros(d + 1), jac=True, method="L-BFGS-B",
                       options={"maxiter": self.max_iter, "gtol": 1e-6})
        self.coef_, self.intercept_ = res.x[:d], res.x[d]
        self.converged_, self.n_iter_ = bool(res.success), int(res.nit)
        self.platt_ = (1.0, 0.0)
        return self

    def decision_function(self, X):
        return sparse.csr_matrix(X) @ self.coef_ + self.intercept_

    def calibrate(self, Xv, yv):
        lr = LogisticRegression(C=1e6, max_iter=1000).fit(self.decision_function(Xv).reshape(-1, 1), yv)
        self.platt_ = (float(lr.coef_[0, 0]), float(lr.intercept_[0]))
        return self

    def predict_proba(self, X):
        a, c = self.platt_
        p = 1.0 / (1.0 + np.exp(-(a * self.decision_function(X) + c)))
        return np.c_[1 - p, p]
