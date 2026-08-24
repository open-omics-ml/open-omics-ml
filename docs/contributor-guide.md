# Open Omics ML Contributor Guide

Open Omics ML welcomes contributions from groups beyond the founding UCL cohort. This guide explains how to participate.

## Licence

All materials in this project are released under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). By contributing — whether as a reanalyst, pipeline contributor, or in any other capacity — you agree to release your contributions under the same licence. This applies to students and external contributors alike.

## Pre-registration

This project is pre-registered on OSF prior to any reanalyses being conducted. The registration covers the methodology, pitfall checklist, research questions, and analysis plan. OSF DOI: [to be added]. All reanalyses conducted within this framework are covered by the project-level registration.

## How to contribute

Contributions are welcome in two forms:

**1. Paper reanalyses** — conduct a reanalysis of a published omics ML paper following the Open Omics ML framework. See below for how to propose one.

**2. Pipeline improvements** — suggest improvements to the notebook toolkit, pitfall definitions, or reporting framework. Open an issue in the central repo with the label `pipeline-suggestion` or `framework-suggestion`. All suggestions are reviewed and, if accepted, contributors are acknowledged in the project documentation and any resulting publications.

## What Open Omics ML is

Open Omics ML asks what modern machine learning can tell us about omics biology when applied with current best practices. We build on published studies that asked important biological questions, extending them with updated methods.

We follow the [ReproHack community](https://www.reprohack.org/) in treating reanalysis as "beneficial scientific activity in itself, with useful outcomes for authors and valuable learning experiences for participants and the research community as a whole." This project is not a watchdog or a criticism forum. It is an open scientific community.

This project is pre-registered on OSF [DOI: to be added], meaning all methodology was fixed before any reanalyses were conducted.

## Who this is for

Open Omics ML welcomes three kinds of contributors:

**Student reanalysts** — undergraduate and postgraduate students conducting reanalyses as projects, with co-authorship on resulting publications.

**Onboarding contributors** — researchers using the framework to get up to speed with a dataset or analysis approach as part of joining a lab or project.

**Pre-publication contributors** — researchers who want structured community feedback on their analysis approach before committing to a full study. The framework provides a rigorous, open way to stress-test methods.

We also welcome contributions to the framework itself — pipeline improvements, pitfall definition refinements, and documentation suggestions.

## How to contribute

### 1. Check for duplicates

Before starting, check the [studies dashboard](../dashboard/index.html) and open issues across the org to make sure the paper you have in mind has not already been claimed.

### 2. Open a proposal issue

Open an issue in the central `open-omics-ml` repo using the **Study Proposal** template. Include:
- Full citation and DOI of the paper you want to reanalyse
- Confirmation that data is publicly available (with link)
- Brief statement of which pitfalls you expect to find and why
- Your group/institution

A maintainer will confirm the paper is not already in progress and create a repo for you within two weeks.

### 3. Conduct the reanalysis

Follow the [student guide](student-guide.md) and [pipeline guide](pipeline-guide.md). External contributors are held to the same standards as internal contributors.

### 4. Submit your audit report

Open an audit report issue in your repo using the standard template. Tag a maintainer for review.

### 5. Review process

External contributions go through a light review by a Open Omics ML maintainer before being included in the dashboard. We check that:
- The reporting framework has been followed
- Evidence for pitfall verdicts is specific and documented
- The framing is constructive
- The code is present and runnable

## Attribution

External contributors are credited in the dashboard and in any resulting publications. Your institution will be listed alongside your study entry.

## Questions

Open an issue in the central `open-omics-ml` repo with the label `question`.

---

## Code of conduct

Open Omics ML operates under the principle that scientific progress is collective. We expect all contributors to engage with prior work — and with each other — respectfully and constructively.

Specifically:
- Pitfall findings are about methods, not the competence or integrity of original authors
- Disagreements about verdicts should be resolved through evidence and discussion
- Contributions that name-call, speculate about motives, or go beyond what the data support will not be accepted

This is a field resource, not a watchdog. We hold ourselves to the same standards we apply to others.
