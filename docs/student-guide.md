# Open Omics ML — Student Guide

Welcome to Open Omics ML. This guide walks you through conducting a reanalysis from paper selection to final report submission. Read it in full before you start.

## What you are doing and why

You are applying current best-practice machine learning methods to a published omics dataset, asking what the data can tell us with more rigorous methodology. This is a genuine scientific contribution — not an audit of someone else's work.

Following the [ReproHack community](https://www.reprohack.org/), we hold that reanalysis is "beneficial scientific activity in itself, with useful outcomes for authors and valuable learning experiences for participants." Your reanalysis:

- Advances the biological question the original paper asked
- Produces real scientific outputs that contribute to a co-authored meta-analysis
- Gives you hands-on experience with applied ML in a real omics context
- Is a portfolio piece demonstrating open, reproducible science

The studies you build on asked important biological questions and advanced the field. ML best practices in omics have evolved rapidly — your job is to extend prior work with updated methods, not to sit in judgement of it. Read the [Code of Conduct](../CODE_OF_CONDUCT.md) before you start.

## Overview

Your reanalysis has two parts:

**Part I — Reproduce and assess.** You reproduce the original analysis as closely as possible, then systematically assess it against a defined checklist of methodological pitfalls. This is the core deliverable and is sufficient for a complete project.

**Part II — Reanalyse.** If the original results are reproducible but pitfalls are present, you reanalyse using more robust methods and report whether the main conclusion holds. Part II is triggered when Part I is successfully completed and pitfalls of medium or high severity are found.

---

## Scope of this framework

This framework assesses the **machine learning** component of omics studies — specifically, how processed data matrices are used to train and evaluate models. It does not cover upstream bioinformatics processing (alignment, quantification, QC, normalisation pipelines).

This boundary is intentional:

- Evaluating upstream processing decisions (choice of aligner, normalisation strategy, QC thresholds) requires deep domain expertise that varies substantially by omics type, and is beyond what can be standardised across a student cohort
- The pitfall literature this framework is based on (Whalen et al. 2022, Teschendorff 2019) is focused on the ML step, not the processing step
- Keeping scope tight ensures findings are comparable across studies and students

You should **note** obvious upstream concerns in your repo README (e.g. normalisation method is unclear, batch correction not mentioned) but you are not expected to evaluate or rerun upstream processing.

---

## Step 1: Paper selection

Your paper must meet the following criteria:

**Required**
- Applies supervised machine learning to omics data (transcriptomics, epigenomics, proteomics, metabolomics, genomics, or multi-omics)
- The main dataset is publicly available (GEO, ArrayExpress, TCGA, Zenodo, or similar)
- The main analysis is computationally reproducible in principle — methods are described in enough detail to attempt reproduction
- Published in a peer-reviewed journal [or: preprint on bioRxiv/medRxiv — confirm with supervisor]

**Preferred**
- Data is manageable in size (processable on a standard laptop or university HPC within reasonable time)
- Code is available (even if you won't use it directly, it aids interpretation)
- The ML task is classification or regression — clustering studies are harder to assess against this framework

**Not suitable**
- Purely methods papers (benchmarks, new tool development) — these have different standards
- Papers where data access requires application or ethics approval you don't have
- Papers you are personally connected to

If you are unsure whether your paper qualifies, open an issue in the central `open-omics-ml` repo using the paper eligibility template before proceeding.

> **Supervisor checkpoint 1:** Your paper selection must be approved by your supervisor before you proceed to pre-registration or any analysis. Open a study proposal issue and wait for the `supervisor-approved` label before continuing.

---

## Step 2: **REMOVED**

## Step 3: Set up your repo

1. You will be added as a member of the Open Omics ML GitHub organisation
2. A repo will be created for your study, named `[first-author]-[year]-[keyword]` (e.g. `smith-2021-methylation`)
3. Clone this repo and use it for all your work
4. Copy the repo README template from `templates/repo-readme-template.md` and fill it in

Your repo should contain:
```
smith-2021-methylation/
├── README.md              # Filled from template
├── data/                  # Data access scripts only — not raw data
├── notebooks/             # Your analysis notebooks
├── scripts/               # Any standalone scripts
├── environment/           # Conda environment file or renv.lock
└── results/               # Figures, tables, outputs
```

Commit regularly. Your commit history is part of your submission.

---

## Step 4: Data access

- Download the data using scripts you write and commit to `data/` — do not commit the raw data itself
- Document exactly where you accessed the data, the date, and any processing applied
- If data is not available exactly as described in the paper, document the discrepancy

---

## Step 5: Part I — Reproduction

### 4a. Set up your environment

Create a reproducible computational environment before you write any analysis code.

- **Python:** Create a conda environment and export to `environment/environment.yml`
- **R:** Use `renv` and commit `environment/renv.lock`
- Document your operating system and key software versions in your README

### 4b. Reproduce the original analysis

Reproduce the main analysis as described in the paper. Your goal is to get as close as possible to the reported results using the same methods, tools, and data.

Guidance:
- Work from the methods section, not from any available code (initially) — this tests reproducibility of the methods description
- If code is available and you get stuck, you may consult it but document when and why
- Record every deviation from the described methods, however small, and explain whether it was forced (e.g. data not available) or a judgement call

### 4c. Compare results

Record the original reported metric(s) and your reproduced metric(s) side by side. Apply the reproduction verdict:

| Verdict | Criteria |
|---------|----------|
| **Reproduced** | Your result is consistent with the reported value given the uncertainty in the original (consider confidence intervals if reported, magnitude of the metric, and whether the main conclusion holds) |
| **Partially reproduced** | Results differ but direction and approximate magnitude are consistent; the main conclusion is broadly supported |
| **Not reproduced** | Results differ substantially or the main conclusion does not hold |

There is no fixed numerical threshold for these verdicts — the appropriate tolerance depends on the metric, the sample size, and what the original paper reported. A difference that is trivial for AUC near 0.5 may be meaningful near 0.95. Use your judgement and justify it explicitly. If the original paper reports confidence intervals, use them as your guide.

If not reproduced, diagnose why before proceeding. Common causes:
- Ambiguous methods — document what you assumed
- Missing data — document what is missing
- Software version differences — document versions used
- Possible error in original — note this carefully and factually

---

## Step 6: Methods assessment

Work through each of the nine pitfalls in the [pitfall reference document](pitfall-reference.md). For each:

1. Read the definition and identification guidance
2. Examine the methods section, supplementary materials, and code (if available)
3. Record your verdict: **Present / Absent / Unclear / Not applicable**
4. Write a brief justification citing specific evidence (quote from methods, line of code, figure number)
5. If present, assess severity: **High / Medium / Low**
6. Note whether this pitfall plausibly affects the main conclusion

Be precise. "Unclear" means you genuinely cannot determine the answer from available information — it is not a default. If in doubt, explain what information would resolve the uncertainty.

---

## Step 7: Submit your assessment report

Open an issue in your repo using the **Assessment Report** issue template. Fill in every section. This is your primary submission document and feeds into the project dashboard.

The issue template mirrors the reporting framework sections. Do not skip sections — if a section is not applicable, say so explicitly.

Along with the issue, commit your Part I notebook to your repo. The notebook must include the commit hash of the central template it was based on in the configuration cell at the top.

> **Supervisor checkpoint 2:** Your supervisor will review your assessment report and Part I notebook before you proceed to Part II. Wait for the `supervisor-approved` label on your issue before continuing.

---

## Step 8: Part II — Reanalysis (if triggered)

Part II is triggered when:
- Part I is complete and your assessment report has been reviewed
- At least one pitfall of **high** or **medium** severity is present
- The original result was **reproduced** or **partially reproduced** (if not reproduced, the cause must first be understood)

### 7a. Select which pitfalls to address

You do not need to fix all pitfalls. Prioritise by:
1. Severity (high first)
2. Whether fixing it is feasible with available data and tools
3. Whether it plausibly affects the main conclusion

Document which pitfalls you are addressing and which you are not, and why.

### 7b. Apply fixes

Apply the standard fixes defined in the pitfall reference document. Use the same pipeline standardisation as Part I where possible — change only what is necessary to address the pitfall.

Key principle: **change one thing at a time.** If you fix multiple pitfalls simultaneously, you cannot attribute changes in performance to specific fixes.

Where possible, fix pitfalls sequentially and record performance after each fix.

### 7c. Report Part II results

- Report new performance metrics alongside original and Part I reproduced metrics
- State clearly whether the main conclusion holds, partially holds, or does not hold after fixing
- Interpret the biological significance of any change — does a drop in performance invalidate the finding, or is the finding robust?

---

## Submission checklist

Before opening your final assessment report issue:

- [ ] Repo README is complete
- [ ] Data access scripts are committed and documented
- [ ] Conda environment file is committed (`environment/environment.yml` or `renv.lock`)
- [ ] Part I notebook committed with template commit hash in config cell
- [ ] Part II notebook committed with template commit hash in config cell (if applicable)
- [ ] Runtime log committed (conda versions + notebook repo hash)
- [ ] All nine pitfalls have a verdict with justification
- [ ] Reproduction verdict is recorded with metrics and contextual justification
- [ ] Deviations from pre-registered plan are documented
- [ ] Part II analysis committed (if applicable)
- [ ] All results are in `results/`
- [ ] Language throughout is constructive and non-accusatory
- [ ] Commit history is clean and interpretable

---

## What makes a good reanalysis

**Good:**
- Precise, evidence-based pitfall verdicts with specific citations
- Honest about what you could and couldn't reproduce and why
- Clear distinction between "this is a methodological opportunity" and "this conclusion does not hold"
- Constructive framing throughout — the original authors asked important questions and advanced the field; you are building on their work

**Avoid:**
- Vague verdicts without evidence ("the methods seem unclear")
- Overclaiming — a pitfall being present does not automatically invalidate the finding
- Underclaiming — severity ratings should be honest
- Any language that sounds accusatory or implies researcher error or misconduct

**Suggested phrasings:**

Instead of: *"The authors failed to use a held-out test set"*
Write: *"Performance was evaluated using cross-validation without a separate held-out test set, which is common in the literature but means the reported metric may overestimate generalisation performance."*

Instead of: *"This paper got the feature selection wrong"*
Write: *"Feature selection appears to have been applied before cross-validation splitting, which is a recognised pitfall that can inflate performance estimates (Whalen et al. 2022). Applying feature selection within each fold would provide a more conservative estimate."*

Instead of: *"The conclusion is wrong"*
Write: *"After applying a more conservative evaluation strategy, the performance estimate was lower than originally reported. The direction of the finding was maintained / was not maintained, suggesting the biological signal may be / may not be robust to stricter methodology."*

The test for any sentence: could it appear in a collaborative methods paper co-authored with the original authors? If not, revise it.

---

## Getting help

- Post questions as issues in your repo (tag your supervisor)
- For framework questions, open an issue in the central `open-omics-ml` repo
- For pipeline/tool questions, see [pipeline-guide.md](pipeline-guide.md)

---

## Key references

Whalen et al. (2022) Navigating the pitfalls of applying machine learning in genomics. *Nat Rev Genet* 23, 169–181.

Teschendorff (2019) Avoiding common pitfalls in machine learning omic data science. *Nat Mater* 18, 422–427.
