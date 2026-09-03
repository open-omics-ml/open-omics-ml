# Open Omics ML — Methodological Considerations Reference

This document defines the nine methodological considerations reviewed in every Open Omics ML reanalysis. They are framed as considerations rather than failures — each represents an aspect of ML methodology that has evolved rapidly in the omics literature, and where applying current best practice may produce different or stronger biological results.

For each consideration you will find: a precise definition, guidance on how to identify it from a paper's methods section or code, a severity rubric (indicating how likely it is to affect results), and the standard approach applied in Part II reanalyses.

## Scope

This framework covers the **machine learning** component of omics studies — from the point where a processed data matrix is passed to a model through to performance evaluation and reporting. Upstream bioinformatics processing (alignment, quantification, QC filtering, normalisation pipelines) is **out of scope**.

This boundary reflects the scope of the ML considerations literature on which this framework is based, and ensures that findings are comparable across analysts and omics types regardless of domain-specific processing expertise. Analysts should note any obvious upstream concerns in their repo README, but are not expected to evaluate or reproduce upstream processing steps.

---

This list is synthesised primarily from Whalen et al. (2022, *Nature Reviews Genetics*) and Teschendorff (2019, *Nature Materials*), the two canonical references for ML pitfalls in omics data science.

---

## How to use this document

For each consideration, record one of four verdicts in your assessment report:

- **Present** — you have clear evidence this consideration applies to the original analysis
- **Absent** — you have clear evidence it does not apply
- **Unclear** — the methods are not described in sufficient detail to determine
- **Not applicable** — the consideration is not relevant to this study design

"Unclear" is a valid and important finding — it indicates a reporting gap regardless of whether the consideration applies. Note what information would resolve the uncertainty.

---

## Consideration 1: No held-out test set

**Definition**
Model performance is reported using only cross-validation or in-sample metrics. There is no independent test set that was completely withheld from all stages of model development, including hyperparameter tuning and model selection.

**How to identify**
- Methods describe only cross-validation with no mention of a held-out set
- The same data partition is used for both model selection and final performance reporting
- Performance is reported as cross-validation accuracy/AUC without a separate test set result
- Code shows the same dataset used throughout with no held-out split

**Severity**
- *High:* Final reported performance comes from training data or CV on full dataset; no independent estimate exists
- *Medium:* A held-out set exists but was used iteratively (e.g. for threshold tuning)
- *Low:* Minor deviation from ideal but an approximate held-out set exists

**Standard approach (Part II)**
Set aside [X]% of data as a held-out test set before any analysis. All preprocessing, feature selection, model training, and hyperparameter tuning occurs on training data only. Final performance is reported once on the held-out set.

*Proportion to hold out: 20% is standard; for small datasets (<100 samples) consider nested cross-validation instead.*

---

## Consideration 2: Preprocessing leakage

**Definition**
Data transformation steps whose parameters are estimated from data — including normalisation, scaling, PCA, imputation, and batch correction — are applied to the full dataset before the train/test split is made. This allows information from the test set to influence the training process.

**How to identify**
- Methods describe normalisation or scaling applied to the full dataset, then splitting
- PCA or other dimensionality reduction performed before splitting, with components used as features
- Imputation of missing values performed on the full dataset
- Code shows preprocessing applied to the combined dataset before `train_test_split` or equivalent
- Batch correction (e.g. ComBat) applied to all samples together before modelling

**Severity**
- *High:* PCA or supervised dimensionality reduction on full dataset used as model input
- *Medium:* Global normalisation applied before splitting
- *Low:* Only centering/scaling applied; minimal information transfer

**Standard approach (Part II)**
All preprocessing steps are wrapped in a pipeline (scikit-learn `Pipeline`, R `recipes`, or equivalent). The pipeline is fit on training data only during each cross-validation fold and applied to held-out data without refitting. PCA components are derived from training data only.

---

## Consideration 3: Feature selection leakage

**Definition**
Features are filtered, ranked, or selected using the full dataset — including the test set — before cross-validation folds are created. This is the most common form of leakage in omics ML because of the high-dimensional nature of omics data and the temptation to reduce features first.

**How to identify**
- Differential expression, correlation with outcome, or variance filtering performed on the full dataset before modelling
- Feature importance from a preliminary model trained on all data used to select features for the main model
- Methods describe a two-stage process: "we first selected the top N features, then trained a classifier" without specifying that selection was within CV
- Code shows feature filtering before the CV loop rather than inside it

**Severity**
- *High:* Supervised feature selection (correlated with outcome) on full dataset — this is a direct form of outcome leakage
- *Medium:* Unsupervised feature selection (variance, missingness) on full dataset — less severe but still leaks distributional information
- *Low:* Feature selection threshold is very conservative and unlikely to affect results meaningfully

**Standard approach (Part II)**
Feature selection is performed inside each cross-validation fold, applied only to the training portion of that fold. In scikit-learn this means placing the feature selector inside the `Pipeline` before the estimator. In R, use `recipes` with `step_select` inside a `workflow`. Report the number of features selected per fold.

---

## Consideration 4: Non-independence of samples

**Definition**
Related samples — multiple timepoints from the same individual, technical replicates, paired samples, family members, or samples from the same batch — are split randomly across training and test sets. This means the model may be evaluated on data it has effectively seen, inflating performance.

**How to identify**
- Dataset includes longitudinal measurements but splitting is not stratified by individual
- Paired case/control samples from the same patient appear on both sides of the split
- Technical replicates of the same sample are present
- Family-based datasets with related individuals split randomly
- Methods describe random splitting without acknowledging sample relationships

**Severity**
- *High:* Multiple samples per individual, high relatedness, or paired design with random split
- *Medium:* Batch or cohort structure not accounted for in splitting
- *Low:* Distant relatedness (e.g. population structure) with otherwise independent samples

**Standard approach (Part II)**
Use group-aware splitting: `GroupKFold` in scikit-learn, or equivalent in R, using individual ID, family ID, or batch as the grouping variable. All samples from the same group appear in the same fold. For paired designs, keep pairs together.

---

## Consideration 5: Confounding variables

**Definition**
A variable correlated with both the biological outcome and the omics features — such as batch, sequencing depth, sex, age, cell type composition, or population structure — is not accounted for. The model may learn to predict the confounder rather than the biological signal of interest.

**How to identify**
- No mention of batch correction or confounder adjustment in methods
- Samples from different conditions processed at different times or in different labs without correction
- Cell type composition not accounted for in bulk omics studies comparing disease vs control
- Population structure not corrected for in genomics studies
- Model performs suspiciously well; performance drops on external validation

**Severity**
- *High:* Known batch or technical confound perfectly or near-perfectly correlated with the outcome
- *Medium:* Confounder is correlated with outcome but not perfectly; some signal may be genuine
- *Low:* Potential confounders exist but are unlikely to dominate the signal

**Standard approach (Part II)**
Identify potential confounders from study design. Apply appropriate correction:
- Batch effects: ComBat, limma removeBatchEffect, or harmonisation methods
- Cell type: deconvolution (CIBERSORT, MuSiC, etc.) or reference-based correction
- Population structure: principal components as covariates
- After correction, verify the confounder is no longer predictable from features before modelling

---

## Consideration 6: Class imbalance mishandling

**Definition**
Oversampling or undersampling is applied to the full dataset before splitting, leaking synthetic or resampled data into the test set. Or performance is reported using accuracy on an imbalanced dataset, masking poor performance on the minority class.

**How to identify**
- SMOTE or other oversampling described before train/test splitting
- Accuracy reported as the primary metric for datasets with imbalanced classes (e.g. >3:1 ratio)
- Class balance not reported in the paper
- Random undersampling described on the full dataset

**Severity**
- *High:* Oversampling before splitting (direct data leakage) combined with imbalanced dataset
- *Medium:* Inappropriate metric (accuracy) masking poor minority class performance
- *Low:* Mild imbalance with accuracy reported; minority class performance may still be meaningful

**Standard approach (Part II)**
Apply resampling inside the training fold only — never to the test set. In scikit-learn, use `imbalanced-learn` pipelines. Report AUPRC (area under precision-recall curve) or Matthews Correlation Coefficient (MCC) as primary metrics. Report class distribution explicitly.

---

## Consideration 7: Distributional shift

**Definition**
Training and test data come from different populations, conditions, laboratories, or time periods without acknowledgement, meaning the reported performance does not reflect the model's ability to generalise to the intended use case.

**How to identify**
- Data combined from multiple cohorts or sources without accounting for source in the split
- Model trained on one population (e.g. European ancestry) and tested on the same
- No external validation on an independent cohort
- Generalisation claims in the abstract that are not supported by the validation strategy

**Severity**
- *High:* Significant distributional difference between intended application and test set; claims of generalisability not supported
- *Medium:* Some distributional differences present; conclusions may hold within the training distribution
- *Low:* Minor differences; unlikely to affect main conclusions

**Standard approach (Part II)**
Where an independent external dataset exists, use it for validation. Document the source of all samples explicitly. Qualify generalisation claims to match the actual validation strategy. If no external dataset is available, note this as a limitation rather than a fix.

---

## Consideration 8: Inappropriate performance metrics

**Definition**
Performance metrics are chosen that inflate apparent performance or are inappropriate for the task — including accuracy on imbalanced classes, AUC without calibration for clinical claims, R² without reporting residuals, or metrics reported on training data.

**How to identify**
- Accuracy reported as the main metric without reporting class distribution
- AUC only, without precision-recall metrics, for imbalanced datasets
- Pearson correlation reported for a regression task without scatter plots or residual analysis
- Claims of clinical utility based on AUC alone without calibration
- Metrics reported without confidence intervals or statistical testing

**Severity**
- *High:* Metric choice fundamentally misrepresents model performance (e.g. 95% accuracy on 95:5 imbalanced dataset)
- *Medium:* Metric is defensible but incomplete; a more appropriate metric would paint a different picture
- *Low:* Minor issue; main conclusions would likely hold with better metrics

**Standard approach (Part II)**
Select metrics appropriate to the task upfront:
- Binary classification, balanced: AUC-ROC + accuracy
- Binary classification, imbalanced: AUPRC + MCC
- Multi-class: macro-averaged F1 + confusion matrix
- Regression: RMSE + R² + residual plots
Report 95% confidence intervals via bootstrapping. For clinical claims, report calibration.

---

## Consideration 9: High dimensionality overfitting

**Definition**
The number of features vastly exceeds the number of samples (p >> n), which is characteristic of omics data, and the modelling approach does not account for this — using unregularised models, no dimensionality reduction, or no correction for multiple testing.

**How to identify**
- Sample size in the tens or low hundreds with thousands of features and no regularisation
- Complex models (deep learning, random forest with many trees) applied to small omics datasets without justification
- No mention of regularisation, dimensionality reduction, or feature selection
- Suspiciously high performance on a small dataset

**Severity**
- *High:* Unregularised complex model on small high-dimensional dataset; performance likely does not generalise
- *Medium:* Some regularisation applied but insufficient for the dimensionality
- *Low:* Model complexity is broadly appropriate; minor risk

**Standard approach (Part II)**
Use regularised models appropriate to the sample size:
- Linear models: lasso (L1), ridge (L2), or elastic net
- Tree-based: limit depth, require minimum samples per leaf
- Deep learning: not recommended for n < [500] without strong justification
Perform dimensionality reduction (PCA, UMAP) for exploration only — not as a preprocessing step that leaks (see Pitfall 2). Report learning curves to demonstrate that performance plateaus with training set size.

---

## Severity summary table

| Pitfall | High severity | Medium severity | Low severity |
|---------|--------------|-----------------|--------------|
| 1. No held-out test set | No independent estimate exists | Test set reused for tuning | Minor deviation |
| 2. Preprocessing leakage | Supervised DR on full data | Global normalisation before split | Centering/scaling only |
| 3. Feature selection leakage | Supervised selection on full data | Unsupervised selection on full data | Conservative threshold |
| 4. Non-independence | Multiple samples per individual | Batch structure ignored | Distant relatedness |
| 5. Confounding | Confounder perfectly correlated with outcome | Partial correlation | Unlikely to dominate |
| 6. Class imbalance | Oversampling before split | Wrong metric only | Mild imbalance |
| 7. Distributional shift | Major shift; generalisation claims unsupported | Some differences | Minor differences |
| 8. Inappropriate metrics | Metric fundamentally misrepresents performance | Incomplete metric set | Minor issue |
| 9. High dimensionality | Unregularised complex model, small n | Partial regularisation | Broadly appropriate |

---

## References

Whalen, S., Schreiber, J., Noble, W.S. & Pollard, K.S. Navigating the pitfalls of applying machine learning in genomics. *Nat Rev Genet* 23, 169–181 (2022).

Teschendorff, A.E. Avoiding common pitfalls in machine learning omic data science. *Nat Mater* 18, 422–427 (2019).
