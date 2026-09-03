# [Author Year] — [Brief study title]

**Open Omics ML reanalysis** | [Your name] | [Date started]

---

## Study being reanalysed

**Citation:** [Full citation]
**DOI:** [DOI]
**Original data:** [GEO/ArrayExpress/other accession and URL]

**In one sentence:** [What does the original paper claim?]

---

## Repository structure

```
.
├── README.md
├── data/
│   └── download.sh          # Script to reproduce data download
├── notebooks/
│   ├── 01_reproduction.ipynb    # Part I: reproduction attempt
│   ├── 02_assessment.ipynb           # Supporting analysis for assessment
│   └── 03_reanalysis.ipynb      # Part II: reanalysis (if triggered)
├── scripts/                     # Standalone scripts extracted from notebooks
├── results/
│   ├── figures/
│   └── tables/
└── environment/
    ├── environment.yml          # Python (conda) — OR —
    └── renv.lock                # R (renv)
```

---

## Computational environment

**Language:** [Python X.X / R X.X / both]
**Key packages:** [List main packages and versions]
**OS:** [Your operating system]

To reproduce this environment:

```bash
# Python
conda env create -f environment/environment.yml
conda activate open-omics-ml-[repo-name]

# R
Rscript -e "renv::restore()"
```

---

## Data access

```bash
# Run from the repo root
bash data/download.sh
```

Data accessed: [Date]
Source: [URL / accession]
Notes: [Any discrepancies between available data and what the paper describes]

---

## Reproduction summary

| Metric | Reported | Reproduced | Difference |
|--------|----------|------------|------------|
| [e.g. AUC] | [value] | [value] | [value] |

**Verdict:** [Reproduced / Partially reproduced / Not reproduced]

---

## Assessment summary

| Pitfall | Verdict | Severity |
|---------|---------|----------|
| P1: No held-out test set | [Present/Absent/Unclear/N/A] | [High/Medium/Low/N/A] |
| P2: Preprocessing leakage | | |
| P3: Feature selection leakage | | |
| P4: Non-independence | | |
| P5: Confounding | | |
| P6: Class imbalance | | |
| P7: Distributional shift | | |
| P8: Inappropriate metrics | | |
| P9: High-dim overfitting | | |

Full assessment report: [Link to issue]

---

## Reanalysis summary (Part II)

[Complete if Part II was conducted, otherwise state "Part II not triggered" and reason]

| Metric | Original | Reproduced | Reanalysis |
|--------|----------|------------|------------|
| | | | |

**Conclusion after reanalysis:** [Robust / Qualified / Revised]

---

## References

[Original paper citation]

Whalen et al. (2022) Navigating the pitfalls of applying machine learning in genomics. *Nat Rev Genet* 23, 169–181.

Teschendorff (2019) Avoiding common pitfalls in machine learning omic data science. *Nat Mater* 18, 422–427.
