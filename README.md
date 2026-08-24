# Open Omics ML

*This is a first draft of an idea. Text mostly written by Claude. Details may be inaccurate*

**What can modern machine learning tell us about omics biology?**

Open Omics ML is a community project that applies current best-practice ML methods to published omics datasets, building on the biological questions that motivated the original studies. We follow the tradition of the [ReproHack community](https://www.reprohack.org/) in treating reanalysis as a positive scientific activity — valuable for authors, participants, and the field.

This project is pre-registered on OSF [DOI: to be added] and all materials are released under CC-BY-SA 4.0.

## The scientific question

Machine learning has transformed omics research and methods best practices — proper train/test separation, confounder correction, appropriate performance metrics — have evolved rapidly. We ask: **when we apply new models and workflows to the same datasets, what more can we learn?**

## Who this is for

Open Omics ML is designed for a variety of participants:

**Students** conducting reanalyses as undergraduate or postgraduate research projects. This is a genuine learning experience in applied ML and open science, with real scientific outputs and co-authorship opportunities.

**New lab members and collaborators** getting up to speed with a dataset, method, or analysis approach. Reanalysing a published study is an excellent onboarding activity.

**Researchers seeking feedback** who want community input on an analysis approach before committing to a full study.

## What we do

Each contributing analyst selects a published omics ML study with publicly available data, then:

1. **Reproduces** the original analysis as closely as possible
2. **Assesses** the analysis against a defined checklist of methodological considerations drawn from the omics ML literature
3. **Reanalyses** using current best-practice methods, asking what the data show when analysed with new methods
4. **Reports** findings in a standardised format that feeds into a field-wide summary

Results are aggregated into a living dashboard. Together, reanalyses form the basis of a co-authored meta-analysis of what omics datasets reveal.

## What reanalysis is — and is not

Following the ReproHack community, we hold that reanalysis is "beneficial scientific activity in itself, with useful outcomes for authors and valuable learning experiences for participants and the research community as a whole."

Reanalysis here is a scientific contribution, not an audit. The studies we build on asked important biological questions and used novel and innovative approaches. We recognise the importance of the work and celebrate it by trying to generate more value from the original papers. This is laid out in our [Code of Conduct](CODE_OF_CONDUCT.md), which sets expectations of all participants.

## Guiding principles

- **The biology first.** The scientific question is what omics data can tell us about biology when combined with robust ML.
- **Open science throughout.** Pre-registered methodology, public code, CC-BY-SA licence, open contributions.
- **Learning experience.** This is designed to be a positive, skill-building experience for all participants.
- **Community-owned.** Contributions are welcome — reanalyses, pipeline improvements, framework suggestions.

## Pre-registration

This project is pre-registered on the Open Science Framework prior to any reanalyses being conducted. The registration covers the framework methodology, pitfall checklist, research questions, inclusion/exclusion criteria, and meta-analysis plan.

OSF registration: [DOI to be added on registration]

## Project structure

```
open-omics-ml/
├── README.md
├── CODE_OF_CONDUCT.md
├── docs/
│   ├── setup-guide.md           # How to set up the org (maintainers)
│   ├── student-guide.md         # How to conduct a reanalysis
│   ├── pitfall-reference.md     # Methodological considerations and fixes
│   ├── pipeline-guide.md        # Recommended tools and environments
│   └── contributor-guide.md     # For external contributors
├── templates/
│   ├── repo-readme-template.md
│   └── ISSUE_TEMPLATE/
│       ├── audit-report.yml
│       └── study-proposal.yml
├── scripts/
│   ├── validate_audit_report.py
│   └── build_dashboard_data.py
└── dashboard/
    └── index.html
```

## Current reanalyses

<!-- Auto-populated from dashboard -->

| Repo | Study | Omics type | Status |
|------|-------|------------|--------|
| | | | |

## Contributing

Contributions are welcome in two forms:

**Paper reanalyses** — propose and conduct a reanalysis following the framework. See [docs/contributor-guide.md](docs/contributor-guide.md).

**Pipeline and framework improvements** — open an issue with the label `pipeline-suggestion` or `framework-suggestion`. Contributors are credited in publications.

## Licence

All materials are released under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). By contributing you agree to release your work under the same licence.

## Citation

> [Citation to be added on publication]

## Precedents and related work

This project follows the [ReproHack](https://www.reprohack.org/) model of community reanalysis as positive scientific practice, and is informed by the reproducibility literature in computational biology (Trisovic et al. 2022; Heil et al. 2021) and the omics ML pitfalls literature (Whalen et al. 2022; Teschendorff 2019).

## Contact

[To be added]

---

*Developed at the UCL Division of Biosciences. We welcome collaborators and contributions from the wider community.*
