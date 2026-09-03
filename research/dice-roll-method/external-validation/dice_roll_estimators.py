"""Dice Roll Method estimators, ported verbatim from dice_roll_method_v2.ipynb.

Cells 14 (cliffs_delta, bca_ci), 19 (mbb_se, fit_curves), 21 (G-study/D-study),
27 (psi, drift battery). Pre-registered adaptations only (PREREGISTRATION.md §4):
the outcome column is a parameter, the transform is a parameter (identity for
Likert/axis/accuracy outcomes, log(x+0.5) for counts), and the GEE family in the
drift test is a parameter (Gaussian for scores, binomial for accuracy, NB for
counts). Nothing else differs from the notebook.
"""

import numpy as np
import pandas as pd
import scipy.stats as sps
import statsmodels.formula.api as smf
from scipy.optimize import curve_fit
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.cov_struct import Independence
from statsmodels.genmod import families

ALPHA = 0.05


# ---------------------------------------------------------------- cell 14
def cliffs_delta(x, y):
    """Cliff's delta = P(X>Y) - P(X<Y). Uses rank-sum formula (O(n log n))."""
    x, y = np.asarray(x), np.asarray(y)
    nx, ny = len(x), len(y)
    combined = np.concatenate([x, y])
    ranks = sps.rankdata(combined)
    rx = ranks[:nx].sum()
    u = rx - nx * (nx + 1) / 2
    return 2 * u / (nx * ny) - 1


def bca_ci(stat_fn, x, y, reps=1000, alpha=0.05, seed=42):
    """Bias-corrected accelerated bootstrap CI for two-sample statistics."""
    rng = np.random.default_rng(seed)
    x, y = np.asarray(x), np.asarray(y)
    theta_hat = stat_fn(x, y)
    boots = np.array([stat_fn(rng.choice(x, len(x), replace=True),
                              rng.choice(y, len(y), replace=True)) for _ in range(reps)])
    z0 = sps.norm.ppf(max(min((boots < theta_hat).mean(), 1 - 1e-9), 1e-9))
    jk = []
    for i in range(len(x)):
        xi = np.delete(x, i); jk.append(stat_fn(xi, y))
    for i in range(len(y)):
        yi = np.delete(y, i); jk.append(stat_fn(x, yi))
    jk = np.array(jk); jk_mean = jk.mean()
    num = ((jk_mean - jk) ** 3).sum()
    den = 6 * (((jk_mean - jk) ** 2).sum()) ** 1.5
    acc = num / den if den > 0 else 0
    z_alpha = sps.norm.ppf(alpha / 2); z_1malpha = sps.norm.ppf(1 - alpha / 2)
    q_lo = sps.norm.cdf(z0 + (z0 + z_alpha) / (1 - acc * (z0 + z_alpha)))
    q_hi = sps.norm.cdf(z0 + (z0 + z_1malpha) / (1 - acc * (z0 + z_1malpha)))
    return theta_hat, np.quantile(boots, q_lo), np.quantile(boots, q_hi)


# ---------------------------------------------------------------- cell 19
def mbb_se(x, n_sub, block=2, reps=1000, seed=0):
    """Moving-block bootstrap SE of the mean for subsample size n_sub."""
    rng = np.random.default_rng(seed)
    means = []
    nblocks = max(1, n_sub // block)
    for _ in range(reps):
        starts = rng.integers(0, len(x) - block + 1, size=nblocks)
        sample = np.concatenate([x[s:s + block] for s in starts])[:n_sub]
        means.append(sample.mean())
    return np.std(means, ddof=1)


def fit_curves(ns, ses):
    """Fit log / power-law / Michaelis-Menten / linear to SE(n), compare via AIC."""
    curves = {}
    ns = np.asarray(ns, float); ses = np.asarray(ses, float)

    def neg_ll(pred):
        resid = ses - pred; sigma = resid.std()
        if sigma == 0:
            return np.inf
        return 0.5 * len(ses) * np.log(2 * np.pi * sigma ** 2) + (resid ** 2).sum() / (2 * sigma ** 2)

    def aic(pred, k):
        return 2 * k + 2 * neg_ll(pred)

    try:
        (a, b), _ = curve_fit(lambda n, a, b: a * np.log(n) + b, ns, ses, maxfev=5000)
        curves["log"] = aic(a * np.log(ns) + b, 2)
    except Exception:
        curves["log"] = np.inf
    try:
        (a, g, b), _ = curve_fit(lambda n, a, g, b: a * n ** (-g) + b, ns, ses, p0=[1, 0.5, 0], maxfev=5000)
        curves["power"] = aic(a * ns ** (-g) + b, 3)
    except Exception:
        curves["power"] = np.inf
    try:
        (a, K, b), _ = curve_fit(lambda n, a, K, b: a * n / (K + n) + b, ns, ses, p0=[1, 5, 0], maxfev=5000)
        curves["mm"] = aic(a * ns / (K + ns) + b, 3)
    except Exception:
        curves["mm"] = np.inf
    try:
        (a, b), _ = curve_fit(lambda n, a, b: a * n + b, ns, ses, maxfev=5000)
        curves["linear"] = aic(a * ns + b, 2)
    except Exception:
        curves["linear"] = np.inf
    return curves


def power_exponent(ns, ses):
    """Fitted exponent g of a*n^(-g)+b on a mean SE curve (EV3b)."""
    (a, g, b), _ = curve_fit(lambda n, a, g, b: a * np.asarray(n, float) ** (-g) + b,
                             ns, ses, p0=[1, 0.5, 0], maxfev=10000)
    return g


# ---------------------------------------------------------------- cell 21
def gstudy(df, unit_col, model_col, y_col, transform=None):
    """Gaussian mixed-model G-study decomposition (notebook cell 21).

    transform: None (identity, pre-registered for Likert/axis/accuracy) or
    'log_count' (log(x+0.5), the notebook's count transform).
    Returns (sigma_p, model_var, sigma_resid).
    """
    d = df.copy()
    y = d[y_col].astype(float)
    d["_y"] = np.log(y + 0.5) if transform == "log_count" else y
    md_main = smf.mixedlm("_y ~ 1", d, groups=d[unit_col]).fit(reml=True)
    sigma_p = float(md_main.cov_re.iloc[0, 0])
    sigma_resid = float(md_main.scale)
    d["_resid"] = md_main.resid
    model_var = float(d.groupby(model_col)["_resid"].var().mean())
    return sigma_p, model_var, sigma_resid


def dstudy_G(sigma_p, model_var, sigma_resid, n_I, n_M):
    """D-study generalizability coefficient (notebook cell 21 formula)."""
    return sigma_p / (sigma_p + sigma_resid / n_I + model_var / n_M)


def single_facet_components(df, unit_col, y_col):
    """Single-facet (unit x iteration) components for one persona/model (EV2)."""
    md = smf.mixedlm(f"{y_col} ~ 1", df, groups=df[unit_col]).fit(reml=True)
    return float(md.cov_re.iloc[0, 0]), float(md.scale)


def empirical_G(df, unit_col, iter_col, y_col, n, splits=200, seed=2026):
    """Model-free empirical reliability of an n-iteration mean (EV2 step 3).

    Correlation across units between mean scores of two disjoint random
    n-iteration subsets, averaged over `splits` random splits.
    """
    rng = np.random.default_rng(seed)
    iters = np.sort(df[iter_col].unique())
    if 2 * n > len(iters):
        raise ValueError(f"2n={2*n} exceeds {len(iters)} iterations")
    wide = df.pivot_table(index=unit_col, columns=iter_col, values=y_col)
    wide = wide[iters]
    rs = []
    for _ in range(splits):
        perm = rng.permutation(len(iters))
        a = wide.iloc[:, perm[:n]].mean(axis=1)
        b = wide.iloc[:, perm[n:2 * n]].mean(axis=1)
        r = np.corrcoef(a, b)[0, 1]
        if np.isfinite(r):
            rs.append(r)
    return float(np.mean(rs))


# ---------------------------------------------------------------- cell 27
def psi(x1, x2, bins=10):
    """Population Stability Index between two samples."""
    lo = min(x1.min(), x2.min()); hi = max(x1.max(), x2.max())
    edges = np.linspace(lo, hi + 1e-6, bins + 1)
    h1, _ = np.histogram(x1, bins=edges); h2, _ = np.histogram(x2, bins=edges)
    p1 = (h1 + 0.5) / h1.sum(); p2 = (h2 + 0.5) / h2.sum()
    return float(((p1 - p2) * np.log(p1 / p2)).sum())


def drift_tests(df, unit_col, model_col, iter_col, y_col, family="gaussian"):
    """Half-split KS + PSI + GEE window drift battery (notebook cell 27).

    family: 'gaussian' (scores), 'binomial' (accuracy), 'nb' (counts) per
    PREREGISTRATION.md §4. Flag rule unchanged: KS p < ALPHA/3, or PSI > 0.2,
    or window p < ALPHA/3.
    """
    fam = {"gaussian": families.Gaussian(),
           "binomial": families.Binomial(),
           "nb": families.NegativeBinomial(alpha=1.0)}[family]
    out = []
    for (pid, m), sub in df.groupby([unit_col, model_col]):
        sub = sub.sort_values(iter_col)
        half = len(sub) // 2
        if half < 2:
            continue
        a = sub.iloc[:half][y_col].values.astype(float)
        b = sub.iloc[half:][y_col].values.astype(float)
        ks_stat, ks_p = sps.ks_2samp(a, b)
        psi_val = psi(a, b, bins=5)
        wsub = sub.copy()
        wsub["window"] = ["early"] * half + ["late"] * (len(sub) - half)
        wsub["_y"] = wsub[y_col].astype(float)
        try:
            r = GEE.from_formula("_y ~ window", groups=wsub[unit_col], data=wsub,
                                 family=fam, cov_struct=Independence()).fit(maxiter=50)
            nb_p = r.pvalues.get("window[T.late]", 1.0)
        except Exception:
            nb_p = 1.0
        out.append(dict(unit=pid, model=m, ks_p=ks_p, psi=psi_val, window_p=nb_p,
                        flag=(ks_p < ALPHA / 3) or (psi_val > 0.2) or (nb_p < ALPHA / 3)))
    return pd.DataFrame(out)
