"""
Open Omics ML dashboard data builder.

Reads all closed audit-report issues across the Open Omics ML org,
parses them, and writes a summary JSON that the dashboard reads.

Run via GitHub Actions on a schedule or when issues are closed.
"""

import os
import json
import re
from datetime import datetime

# Requires PyGithub: pip install PyGithub
from github import Github

PITFALL_NAMES = {
    "p1": "No held-out test set",
    "p2": "Preprocessing leakage",
    "p3": "Feature selection leakage",
    "p4": "Non-independence of samples",
    "p5": "Confounding variables",
    "p6": "Class imbalance mishandling",
    "p7": "Distributional shift",
    "p8": "Inappropriate performance metrics",
    "p9": "High dimensionality overfitting",
}

OMICS_TYPES = [
    "Transcriptomics (bulk RNA-seq)",
    "Transcriptomics (microarray)",
    "Single-cell RNA-seq",
    "DNA methylation (array)",
    "DNA methylation (WGBS/RRBS)",
    "Genomics / SNP / WGS",
    "Proteomics",
    "Metabolomics",
    "ATAC-seq / chromatin accessibility",
    "Multi-omics",
    "Other",
]


def parse_issue_body(body: str) -> dict:
    """Parse audit report issue body into structured fields."""
    fields = {}
    blocks = re.split(r'\n### ', body)
    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split('\n')
        if not lines:
            continue
        label = lines[0].strip().lstrip('#').strip()
        value_lines = []
        for line in lines[1:]:
            if line.strip() or value_lines:
                value_lines.append(line)
        value = '\n'.join(value_lines).strip()
        field_id = (label.lower()
                    .replace(' ', '_')
                    .replace('(', '')
                    .replace(')', '')
                    .replace('?', '')
                    .replace('/', '_'))
        fields[field_id] = value
    return fields


def extract_pitfall_summary(fields: dict) -> dict:
    """Extract pitfall verdicts and severities from parsed fields."""
    pitfalls = {}
    for key, name in PITFALL_NAMES.items():
        verdict = fields.get(f"{key}_verdict", "").strip()
        severity = fields.get(f"{key}_severity", "").strip()
        affects = fields.get(f"{key}_affects_conclusion", "").strip()
        pitfalls[key] = {
            "name": name,
            "verdict": verdict if verdict else "Not recorded",
            "severity": severity if severity else "N/A",
            "affects_conclusion": affects if affects else "Not recorded",
        }
    return pitfalls


def process_issue(issue) -> dict | None:
    """Process a single GitHub issue into a structured record."""
    if not issue.body:
        return None

    fields = parse_issue_body(issue.body)

    # Skip if this doesn't look like a completed audit report
    if not fields.get("citation") and not fields.get("main_claim"):
        return None

    record = {
        "issue_url": issue.html_url,
        "issue_number": issue.number,
        "repo": issue.repository.name if hasattr(issue, 'repository') else "unknown",
        "submitted_by": issue.user.login,
        "submitted_at": issue.created_at.isoformat(),
        # Section 1
        "citation": fields.get("citation", ""),
        "omics_type": fields.get("omics_type", ""),
        "ml_task": fields.get("ml_task", ""),
        "sample_size": fields.get("sample_size", ""),
        "n_features": fields.get("n_features", ""),
        "main_claim": fields.get("main_claim", ""),
        # Section 2
        "reproduction_verdict": fields.get("reproduction_verdict", ""),
        # Section 3
        "pitfalls": extract_pitfall_summary(fields),
        # Section 4
        "part2_triggered": fields.get("part2_triggered", ""),
        "part2_conclusion_verdict": fields.get("part2_conclusion_verdict", ""),
        # Section 5
        "summary_paragraph": fields.get("summary_paragraph", ""),
        "max_severity": fields.get("max_severity", ""),
        "overall_conclusion_change": fields.get("overall_conclusion_change", ""),
    }

    return record


def build_summary_stats(records: list[dict]) -> dict:
    """Compute summary statistics across all records for the dashboard."""
    if not records:
        return {}

    n = len(records)

    # Pitfall prevalence
    pitfall_counts = {key: 0 for key in PITFALL_NAMES}
    for record in records:
        for key in PITFALL_NAMES:
            verdict = record["pitfalls"].get(key, {}).get("verdict", "")
            if "present" in verdict.lower():
                pitfall_counts[key] += 1

    # Reproduction verdicts
    reproduction_counts = {}
    for record in records:
        v = record.get("reproduction_verdict", "Not recorded")
        # Simplify to short label
        if "not reproduced" in v.lower():
            label = "Not reproduced"
        elif "partially" in v.lower():
            label = "Partially reproduced"
        elif "reproduced" in v.lower():
            label = "Reproduced"
        else:
            label = "Not recorded"
        reproduction_counts[label] = reproduction_counts.get(label, 0) + 1

    # Conclusion changes
    conclusion_counts = {}
    for record in records:
        v = record.get("overall_conclusion_change", "")
        if "robust" in v.lower():
            label = "Robust"
        elif "qualified" in v.lower():
            label = "Qualified"
        elif "revised" in v.lower():
            label = "Revised"
        elif "cannot determine" in v.lower():
            label = "Cannot determine"
        else:
            label = "Not recorded"
        conclusion_counts[label] = conclusion_counts.get(label, 0) + 1

    # Omics type breakdown
    omics_counts = {}
    for record in records:
        ot = record.get("omics_type", "Not recorded")
        omics_counts[ot] = omics_counts.get(ot, 0) + 1

    # Severity distribution
    severity_counts = {"High": 0, "Medium": 0, "Low": 0, "None": 0}
    for record in records:
        s = record.get("max_severity", "")
        if s in severity_counts:
            severity_counts[s] += 1

    return {
        "total_studies": n,
        "generated_at": datetime.utcnow().isoformat(),
        "pitfall_prevalence": {
            key: {
                "name": PITFALL_NAMES[key],
                "count": pitfall_counts[key],
                "percent": round(pitfall_counts[key] / n * 100, 1),
            }
            for key in PITFALL_NAMES
        },
        "reproduction_verdicts": reproduction_counts,
        "conclusion_changes": conclusion_counts,
        "omics_types": omics_counts,
        "severity_distribution": severity_counts,
    }


def main():
    token = os.environ.get("GITHUB_TOKEN")
    org_name = os.environ.get("ORG_NAME", "open-omics-ml")  # Update with actual org name
    output_path = os.environ.get("OUTPUT_PATH", "dashboard/data.json")

    g = Github(token)
    org = g.get_organization(org_name)

    records = []

    for repo in org.get_repos():
        # Skip the central repo and non-study repos
        if repo.name in ["open-omics-ml", ".github"]:
            continue

        print(f"Processing repo: {repo.name}")

        for issue in repo.get_issues(state="closed", labels=["audit-report", "validation-passed"]):
            record = process_issue(issue)
            if record:
                record["repo"] = repo.name
                records.append(record)
                print(f"  Parsed issue #{issue.number}: {issue.title[:60]}")

    summary = build_summary_stats(records)

    output = {
        "summary": summary,
        "studies": records,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. {len(records)} studies processed.")
    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
