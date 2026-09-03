"""
Open Omics ML report validator.

Parses a GitHub issue body (from the assessment-report template) and checks
that all required fields are completed. Writes a validation result
as a markdown comment and sets a GitHub Actions output.
"""

import os
import re
import json

# ─────────────────────────────────────────────────────────────────────────────
# REQUIRED FIELDS
# Each entry is (field_id, human_readable_name, section)
# These must be present and non-empty in the issue body
# ─────────────────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    # Section 1
    ("citation", "Full citation", "Section 1"),
    ("data_source", "Data source", "Section 1"),
    ("omics_type", "Omics type", "Section 1"),
    ("ml_task", "ML task", "Section 1"),
    ("sample_size", "Sample size", "Section 1"),
    ("n_features", "Number of features", "Section 1"),
    ("main_claim", "Main claim", "Section 1"),
    ("code_available", "Code available", "Section 1"),
    # Section 2
    ("language_tools", "Language and tools", "Section 2"),
    ("deviations", "Deviations from original methods", "Section 2"),
    ("reproduction_metrics", "Reported vs reproduced metrics", "Section 2"),
    ("reproduction_verdict", "Reproduction verdict", "Section 2"),
    # Section 3 — all pitfall verdicts and evidence
    ("p1_verdict", "Pitfall 1 verdict", "Section 3"),
    ("p1_evidence", "Pitfall 1 evidence", "Section 3"),
    ("p2_verdict", "Pitfall 2 verdict", "Section 3"),
    ("p2_evidence", "Pitfall 2 evidence", "Section 3"),
    ("p3_verdict", "Pitfall 3 verdict", "Section 3"),
    ("p3_evidence", "Pitfall 3 evidence", "Section 3"),
    ("p4_verdict", "Pitfall 4 verdict", "Section 3"),
    ("p4_evidence", "Pitfall 4 evidence", "Section 3"),
    ("p5_verdict", "Pitfall 5 verdict", "Section 3"),
    ("p5_evidence", "Pitfall 5 evidence", "Section 3"),
    ("p6_verdict", "Pitfall 6 verdict", "Section 3"),
    ("p6_evidence", "Pitfall 6 evidence", "Section 3"),
    ("p7_verdict", "Pitfall 7 verdict", "Section 3"),
    ("p7_evidence", "Pitfall 7 evidence", "Section 3"),
    ("p8_verdict", "Pitfall 8 verdict", "Section 3"),
    ("p8_evidence", "Pitfall 8 evidence", "Section 3"),
    ("p9_verdict", "Pitfall 9 verdict", "Section 3"),
    ("p9_evidence", "Pitfall 9 evidence", "Section 3"),
    # Section 4
    ("part2_triggered", "Part II triggered", "Section 4"),
    # Section 5
    ("summary_paragraph", "Summary paragraph", "Section 5"),
    ("max_severity", "Highest severity pitfall", "Section 5"),
    ("overall_conclusion_change", "Overall conclusion change", "Section 5"),
]

# Fields that must not be placeholder/too short
MIN_LENGTH = {
    "main_claim": 50,
    "deviations": 30,
    "reproduction_metrics": 50,
    "p1_evidence": 20,
    "p2_evidence": 20,
    "p3_evidence": 20,
    "p4_evidence": 20,
    "p5_evidence": 20,
    "p6_evidence": 20,
    "p7_evidence": 20,
    "p8_evidence": 20,
    "p9_evidence": 20,
    "summary_paragraph": 100,
}

# Valid options for dropdown fields
VALID_OPTIONS = {
    "reproduction_verdict": [
        "Reproduced (within 5%, conclusion holds)",
        "Partially reproduced (direction consistent, >5% difference)",
        "Not reproduced (substantial difference or conclusion does not hold)",
    ],
    "p1_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p2_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p3_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p4_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p5_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p6_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p7_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p8_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "p9_verdict": ["Present", "Absent", "Unclear", "Not applicable"],
    "max_severity": ["High", "Medium", "Low", "None"],
    "overall_conclusion_change": [
        "Conclusion robust — holds after reanalysis",
        "Conclusion qualified — holds with reduced effect size",
        "Conclusion revised — does not hold after reanalysis",
        "Cannot determine — Part II not conducted",
        "Cannot determine — reproduction failed",
    ],
}


def parse_issue_body(body: str) -> dict:
    """
    Parse a GitHub issue body created from the assessment-report.yml template.
    The template renders as sections with ### headings and field values below.
    Returns a dict of field_id -> value.
    """
    fields = {}

    # GitHub issue forms render as:
    # ### Field Label
    #
    # Field value
    #
    # ### Next Field Label
    # ...

    # Split into blocks by ### headings
    blocks = re.split(r'\n### ', body)

    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split('\n')
        if not lines:
            continue
        # First line is the field label
        label = lines[0].strip().lstrip('#').strip()
        # Rest is the value (skip blank lines at start)
        value_lines = []
        for line in lines[1:]:
            if line.strip() or value_lines:  # skip leading blanks
                value_lines.append(line)
        value = '\n'.join(value_lines).strip()

        # Map label to field id (simple normalisation)
        field_id = label.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('?', '').replace('/', '_')
        fields[field_id] = value

    return fields


def validate(body: str) -> tuple[bool, list[str], list[str]]:
    """
    Validate a report issue body.
    Returns (passed, errors, warnings).
    """
    errors = []
    warnings = []

    if not body or len(body.strip()) < 100:
        errors.append("Issue body is empty or too short — did you use the assessment report template?")
        return False, errors, warnings

    fields = parse_issue_body(body)

    # Check required fields are present and non-empty
    for field_id, name, section in REQUIRED_FIELDS:
        value = fields.get(field_id, "").strip()
        if not value or value in ["_No response_", "None", ""]:
            errors.append(f"**{section}:** '{name}' is empty or missing")
        elif field_id in MIN_LENGTH and len(value) < MIN_LENGTH[field_id]:
            errors.append(
                f"**{section}:** '{name}' appears too brief "
                f"(minimum {MIN_LENGTH[field_id]} characters). "
                f"Please provide more detail."
            )
        elif field_id in VALID_OPTIONS:
            # Check the value matches one of the valid options
            valid = VALID_OPTIONS[field_id]
            if not any(opt.lower() in value.lower() for opt in valid):
                errors.append(
                    f"**{section}:** '{name}' has an unexpected value: '{value[:80]}'. "
                    f"Expected one of: {', '.join(valid)}"
                )

    # Check that severity is provided for any pitfall marked Present
    for i in range(1, 10):
        verdict_key = f"p{i}_verdict"
        severity_key = f"p{i}_severity"
        verdict = fields.get(verdict_key, "").strip()
        severity = fields.get(severity_key, "").strip()

        if "present" in verdict.lower() and not severity:
            warnings.append(
                f"Pitfall {i} is marked Present but no severity is recorded. "
                f"Please add a severity rating."
            )

    # Check Part II fields if Part II is triggered
    part2 = fields.get("part2_triggered", "").strip().lower()
    if "yes" in part2:
        for field_id in ["part2_pitfalls_addressed", "part2_fixes_applied",
                         "part2_metrics", "part2_conclusion_verdict", "part2_interpretation"]:
            value = fields.get(field_id, "").strip()
            if not value or value in ["_No response_", ""]:
                errors.append(
                    f"**Section 4:** Part II is marked as triggered but '{field_id}' is empty."
                )

    passed = len(errors) == 0
    return passed, errors, warnings


def write_output(passed: bool, errors: list[str], warnings: list[str]):
    """Write validation result as markdown and set GitHub Actions output."""

    # Write markdown comment
    lines = []
    if passed:
        lines.append("## ✅ report validation passed")
        lines.append("")
        lines.append(
            "All required fields are complete. Your supervisor has been notified. "
            "You can now request a review."
        )
    else:
        lines.append("## ❌ report needs revision")
        lines.append("")
        lines.append(
            f"Found **{len(errors)} error(s)** that must be fixed before this report can be accepted."
        )
        lines.append("")
        lines.append("### Errors")
        for error in errors:
            lines.append(f"- {error}")

    if warnings:
        lines.append("")
        lines.append("### Warnings")
        lines.append("These are not blocking but should be addressed:")
        for warning in warnings:
            lines.append(f"- {warning}")

    lines.append("")
    lines.append(
        "_This is an automated check. It verifies that all fields are complete "
        "but does not assess the quality of your analysis. "
        "Your supervisor will review the content._"
    )

    comment = '\n'.join(lines)

    with open('validation_result.md', 'w') as f:
        f.write(comment)

    # Set GitHub Actions output
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"passed={'true' if passed else 'false'}\n")
        f.write(f"error_count={len(errors)}\n")

    print(f"Validation {'PASSED' if passed else 'FAILED'}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    body = os.environ.get("ISSUE_BODY", "")
    passed, errors, warnings = validate(body)
    write_output(passed, errors, warnings)
