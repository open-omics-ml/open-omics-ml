# Open Omics ML Pipeline Guide

This guide defines the recommended computational tools and environments for Open Omics ML reanalyses. Standardising tools across the cohort makes results comparable and simplifies troubleshooting.

Where the original paper uses a specific tool, you should use the same tool in Part I. In Part II, where you are applying fixes, use the standard tools defined here.

---

## General principles

- **Reproducibility first.** Your analysis must be rerunnable by someone else on a different machine. This means pinned package versions, documented environments, and no hardcoded paths.
- **Notebooks for exploration, scripts for production.** Use Jupyter or R Markdown notebooks for exploratory analysis. Extract final analysis steps into standalone scripts.
- **Separate data access from analysis.** Data download/access scripts live in `data/`. Analysis scripts live in `notebooks/` or `scripts/`.
- **Document everything that isn't obvious.** A comment explaining *why* is more valuable than one explaining *what*.

---

## Language

Open Omics ML reanalyses can be conducted in **Python**, **R**, or both. Use the language that best matches the original paper and your own skills.

If the original paper used R and you are more comfortable in Python (or vice versa), discuss with your supervisor before deviating — consistency with the original aids reproduction.

---

## Environment management

### Python

Use **conda** for environment management.

Create your environment:
```bash
conda create -n open-omics-ml-[yourrepo] python=3.11
conda activate open-omics-ml-[yourrepo]
```

Export your environment:
```bash
conda env export > environment/environment.yml
```

Your `environment.yml` must be committed and kept up to date. Every package you use must be in it.

### R

Use **renv** for environment management.

Initialise renv in your project:
```r
renv::init()
```

After installing packages:
```r
renv::snapshot()
```

Commit `environment/renv.lock`. Do not commit the `renv/library/` directory.

---

## Core ML libraries

### Python

| Task | Recommended library | Notes |
|------|-------------------|-------|
| General ML | scikit-learn | Use pipelines for all preprocessing + modelling |
| Imbalanced data | imbalanced-learn | Always use inside pipeline, not before split |
| Deep learning | PyTorch or TensorFlow/Keras | Only where justified by sample size |
| Data handling | pandas, numpy | Standard |
| Omics data | pydeseq2, anndata, scanpy | For RNA-seq and single-cell |

### R

| Task | Recommended library | Notes |
|------|-------------------|-------|
| General ML | caret or tidymodels | tidymodels preferred for new analyses |
| Classification | glmnet, ranger, xgboost | |
| Preprocessing | recipes (tidymodels) | Handles leakage-safe preprocessing |
| RNA-seq | DESeq2, edgeR, limma | |
| Methylation | minfi, ChAMP | |
| Batch correction | ComBat (sva package) | |
| Single-cell | Seurat, Bioconductor | |

---

## Leakage-safe pipeline construction

This is the most important technical requirement. All preprocessing must occur inside a pipeline that is fit on training data only.

### Python example (scikit-learn)

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Define pipeline — preprocessing is INSIDE the pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=50)),  # Only if appropriate
    ('classifier', LogisticRegression(C=1.0, penalty='l2'))
])

# Cross-validation — pipeline is refit from scratch on each fold
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring='roc_auc')

# Final evaluation on held-out test set — fit once on full training set
pipeline.fit(X_train, y_train)
test_score = pipeline.score(X_test, y_test)
```

### R example (tidymodels)

```r
library(tidymodels)

# Define recipe (preprocessing) — fit on training data only
recipe <- recipe(outcome ~ ., data = train_data) |>
  step_normalize(all_predictors()) |>
  step_pca(all_predictors(), num_comp = 50)

# Define model
model <- logistic_reg(penalty = 0.01, mixture = 1) |>
  set_engine("glmnet")

# Bundle into workflow
workflow <- workflow() |>
  add_recipe(recipe) |>
  add_model(model)

# Cross-validation
folds <- vfold_cv(train_data, v = 5, strata = outcome)
cv_results <- fit_resamples(workflow, folds)

# Final fit and test set evaluation
final_fit <- last_fit(workflow, split)
collect_metrics(final_fit)
```

---

## Feature selection

Feature selection must occur **inside** the cross-validation loop, not before it.

### Python

```python
from sklearn.feature_selection import SelectKBest, f_classif

pipeline = Pipeline([
    ('feature_selection', SelectKBest(f_classif, k=100)),  # Inside pipeline
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])
```

### R (tidymodels)

```r
recipe <- recipe(outcome ~ ., data = train_data) |>
  step_select_vip(all_predictors(), outcome = "outcome", top_p = 100)
  # Or use step_corr, step_nzv for unsupervised selection
```

---

## Performance metrics

Report the following as a minimum for all classification tasks:

| Metric | When to use | Function |
|--------|------------|---------|
| AUC-ROC | All binary classification | `sklearn.metrics.roc_auc_score` / `yardstick::roc_auc` |
| AUPRC | Imbalanced datasets | `sklearn.metrics.average_precision_score` / `yardstick::pr_auc` |
| MCC | Imbalanced datasets | `sklearn.metrics.matthews_corrcoef` / `yardstick::mcc` |
| F1 (macro) | Multi-class | `sklearn.metrics.f1_score(average='macro')` |
| Confusion matrix | All | Always report |

For regression tasks:

| Metric | Function |
|--------|---------|
| RMSE | `sklearn.metrics.root_mean_squared_error` / `yardstick::rmse` |
| R² | `sklearn.metrics.r2_score` / `yardstick::rsq` |
| Residual plots | Always plot |

Always report 95% confidence intervals. Use bootstrapping:

```python
from sklearn.utils import resample
import numpy as np

def bootstrap_ci(y_true, y_pred, metric_fn, n_bootstrap=1000, ci=0.95):
    scores = []
    for _ in range(n_bootstrap):
        idx = resample(range(len(y_true)))
        scores.append(metric_fn(y_true[idx], y_pred[idx]))
    lower = np.percentile(scores, (1 - ci) / 2 * 100)
    upper = np.percentile(scores, (1 + ci) / 2 * 100)
    return np.mean(scores), lower, upper
```

---

## Group-aware splitting

For datasets with non-independent samples:

### Python

```python
from sklearn.model_selection import GroupKFold

cv = GroupKFold(n_splits=5)
scores = cross_val_score(pipeline, X, y, groups=sample_groups, cv=cv)
```

### R

```r
folds <- group_vfold_cv(data, group = individual_id, v = 5)
```

---

## Batch correction

Where batch correction is required (Pitfall 5 fix), apply it within the training fold only.

```python
# Pseudocode — batch correction within CV
from sklearn.base import BaseEstimator, TransformerMixin

class ComBatCorrector(BaseEstimator, TransformerMixin):
    """Wrapper to apply ComBat inside sklearn pipeline"""
    def fit(self, X, y=None, batch=None):
        # Fit ComBat parameters on training data
        ...
    def transform(self, X, batch=None):
        # Apply fitted parameters to new data
        ...
```

In R, use `sva::ComBat()` inside the recipe or workflow, ensuring parameters are estimated on training data only.

---

## HPC usage

[To be completed based on UCL Myriad configuration]

Key points:
- Request appropriate memory for large omics datasets
- Use array jobs for cross-validation folds where computationally intensive
- Store large intermediate files in scratch space, not the repo

---

## Omics-specific notes

### RNA-seq
- Normalise within training set only (TMM, DESeq2 size factors)
- Do not use raw counts as input to ML without normalisation
- For differential expression as feature selection, apply inside CV fold

### DNA methylation arrays
- Normalise within training set (functional normalisation, BMIQ)
- Cell type deconvolution should use training data only
- For 450k/EPIC arrays, filter probes on training data only (cross-reactive, SNP probes are fixed and can be filtered before splitting)

### Proteomics
- Imputation of missing values must occur inside CV fold
- Normalisation must occur inside CV fold

### Single-cell
- [To be completed]

### Multi-omics
- Each omics layer must have preprocessing applied within fold separately before integration
- Late integration (train separate models per omics, combine predictions) is generally safer than early integration for avoiding leakage

---

## Random seeds

Always set random seeds for reproducibility. Document the seed used.

```python
import numpy as np
import random

SEED = 42  # Document this
np.random.seed(SEED)
random.seed(SEED)
```

```r
set.seed(42)  # Document this
```

Note: setting a seed does not guarantee identical results across different package versions or operating systems. Document your environment fully.
