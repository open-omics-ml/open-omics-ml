"""
Open Omics ML report validator.

Parses a report issue body and checks that all required fields are completed.
Writes the result as a markdown comment and sets a GitHub Actions output.

The FIELDS table below is the single source of truth. It defines both:
  - what the validator looks for, and
  - the markdown template students draft in.

Run `python validate_report.py --emit-template` to print the drafting template.
Because both come from the same table, the headings cannot drift apart.
"""

import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# FIELD TABLE — single source of truth
#
# id        : key used internally
# heading   : the exact "### " heading in the issue body
# section   : grouping, used in error messages and the template
# required  : True | False | "part2"  ("part2" = required only if Part II ran)
# min_length: minimum characters, if any
# options   : permitted values, if constrained
# hint      : placeholder text shown in the generated template
# ─────────────────────────────────────────────────────────────────────────────

VERDICT_OPTIONS = ["Present", "Absent", "Unclear", "Not applicable"]

FIELDS = [
    # ── Section 1 — the original study ──────────────────────────────────────
    dict(id="citation", heading="Full citation", section="Section 1",
         required=True, hint="Author(s), year, title, journal, DOI"),
    dict(id="data_source", heading="Data source", section="Section 1",
         required=True, hint="GEO accession, Zenodo DOI, repository URL"),
    dict(id="omics_type", heading="Omics type", section="Section 1",
         required=True, hint="e.g. Bulk RNA-seq"),
    dict(id="ml_task", heading="ML task", section="Section 1",
         required=True, hint="e.g. Binary classification of tumour vs normal"),
    dict(id="sample_size", heading="Sample size", section="Section 1",
         required=True, hint="n = ..., with group breakdown if relevant"),
    dict(id="n_features", heading="Number of features", section="Section 1",
         required=True, hint="Features entering the model"),
    dict(id="main_claim", heading="Main claim", section="Section 1",
         required=True, min_length=50,
         hint="The central claim, stated as the original authors would state it"),
    dict(id="code_available", heading="Code available", section="Section 1",
         required=True, options=["Yes", "Partial", "No"]),

    # ── Section 2 — reproducing the original analysis ───────────────────────
    dict(id="language_tools", heading="Language and tools", section="Section 2",
         required=True, hint="e.g. Python 3.11, scikit-learn 1.4"),
    dict(id="deviations", heading="Deviations from original methods", section="Section 2",
         required=True, min_length=30,
         hint="Anything you had to do differently, and why"),
    dict(id="reproduction_metrics", heading="Reported vs reproduced metrics", section="Section 2",
         required=True, min_length=50,
         hint="Side by side, with the metric named"),
    dict(id="reproduction_verdict", heading="Reproduction verdict", section="Section 2",
         required=True, options=[
             "Reproduced — results consistent, conclusion holds",
             "Partially reproduced — direction consistent, magnitude differs",
             "Not reproduced — results differ substantially or conclusion does not hold",
         ]),

    # ── Section 3 — methodological considerations (added below) ─────────────

    # ── Section 4 — extended reanalysis ─────────────────────────────────────
    dict(id="part2_triggered", heading="Part II triggered", section="Section 4",
         required=True, options=["Yes", "No"]),
    dict(id="part2_considerations_addressed", heading="Part II considerations addressed",
         section="Section 4", required="part2",
         hint="Which considerations the reanalysis addresses"),
    dict(id="part2_fixes_applied", heading="Part II changes applied", section="Section 4",
         required="part2", hint="What you changed and why"),
    dict(id="part2_metrics", heading="Part II metrics", section="Section 4",
         required="part2", hint="Original vs reanalysed, side by side"),
    dict(id="part2_conclusion_verdict", heading="Part II conclusion verdict",
         section="Section 4", required="part2"),
    dict(id="part2_interpretation", heading="Part II interpretation", section="Section 4",
         required="part2", hint="What this adds to the original finding"),

    # ── Section 5 — summary ─────────────────────────────────────────────────
    dict(id="summary_paragraph", heading="Summary paragraph", section="Section 5",
         required=True, min_length=100,
         hint="One paragraph a reader could take away without reading the rest"),
    dict(id="max_severity", heading="Highest severity consideration", section="Section 5",
         required=True, options=["High", "Medium", "Low", "None"]),
    dict(id="overall_conclusion_change", heading="Overall conclusion change", section="Section 5",
         required=True, options=[
             "Conclusion robust — holds after reanalysis",
             "Conclusion qualified — holds with reduced effect size",
             "Conclusion revised — does not hold after reanalysis",
             "Cannot determine — Part II not conducted",
             "Cannot determine — reproduction not achieved",
         ]),
]

# ─────────────────────────────────────────────────────────────────────────────
# Section 3 — one verdict / evidence / severity triplet per consideration.
# Edit CONSIDERATIONS to rename them; headings and validation follow.
# ─────────────────────────────────────────────────────────────────────────────

CONSIDERATIONS = {
    1: "No held-out test set",
    2: "Feature selection before splitting",
    3: "Preprocessing before splitting",
    4: "Duplicate or related samples across splits",
    5: "Batch effects confounded with outcome",
    6: "Class imbalance not accounted for",
    7: "Hyperparameters tuned on the test set",
    8: "Metric inappropriate for the task",
    9: "No comparison against a simple baseline",
}

_section3 = []
for _n, _name in CONSIDERATIONS.items():
    _section3.append(dict(
        id=f"p{_n}_verdict", heading=f"Consideration {_n} verdict", section="Section 3",
        required=True, options=VERDICT_OPTIONS, note=_name))
    _section3.append(dict(
        id=f"p{_n}_evidence", heading=f"Consideration {_n} evidence", section="Section 3",
        required=True, min_length=20,
        hint="Quote or point to the part of the paper this rests on"))
    _section3.append(dict(
        id=f"p{_n}_severity", heading=f"Consideration {_n} severity", section="Section 3",
        required=False, options=["High", "Medium", "Low"],
        hint="Required if the verdict is Present"))

# Splice Section 3 in before Section 4
_s4_start = next(i for i, f in enumerate(FIELDS) if f["section"] == "Section 4")
FIELDS = FIELDS[:_s4_start] + _section3 + FIELDS[_s4_start:]

# Derived lookups — never hand-maintained
HEADING_TO_ID = {f["heading"]: f["id"] for f in FIELDS}
BY_ID = {f["id"]: f for f in FIELDS}

EMPTY_VALUES = {"", "_no response_", "none", "n/a", "tbd", "..."}


# ─────────────────────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_issue_body(body: str) -> tuple[dict, list[str]]:
    """
    Split an issue body on '### ' headings and map each to a known field id.

    Returns (fields, unmatched_headings). Headings that are not in the field
    table are reported rather than silently dropped — a reworded heading
    otherwise looks identical to an empty field.
    """
    fields = {}
    unmatched = []

    blocks = re.split(r'(?m)^### ', body)
    if not body.lstrip().startswith('### '):
        blocks = blocks[1:]  # anything before the first heading is preamble

    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split('\n')
        heading = lines[0].strip()

        # Value is everything up to the next heading of any level
        value_lines = []
        for line in lines[1:]:
            if line.lstrip().startswith('#'):
                break
            if line.strip() or value_lines:
                value_lines.append(line)
        # Drop template hints so they are never mistaken for answers
        value = re.sub(r'<!--.*?-->', '', '\n'.join(value_lines), flags=re.S).strip()

        field_id = HEADING_TO_ID.get(heading)
        if field_id is None:
            unmatched.append(heading)
            continue
        fields[field_id] = value

    return fields, unmatched


def _is_empty(value: str) -> bool:
    return value.strip().lower() in EMPTY_VALUES


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def _check_one(field: dict, value: str, errors: list[str]):
    """Check a single populated field against its constraints."""
    name, section = field["heading"], field["section"]

    if "min_length" in field and len(value) < field["min_length"]:
        errors.append(
            f"**{section}:** '{name}' looks brief "
            f"({len(value)} characters, expected at least {field['min_length']}). "
            f"Please expand."
        )
        return

    if "options" in field:
        if not any(opt.lower() in value.lower() for opt in field["options"]):
            errors.append(
                f"**{section}:** '{name}' has an unexpected value: '{value[:80]}'. "
                f"Expected one of: {', '.join(field['options'])}"
            )


def validate(body: str) -> tuple[bool, list[str], list[str]]:
    """Validate a report issue body. Returns (passed, errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not body or len(body.strip()) < 100:
        return False, ["Issue body is empty or very short — was the report template used?"], []

    fields, unmatched = parse_issue_body(body)

    for heading in unmatched:
        warnings.append(
            f"Unrecognised heading: '{heading}'. It does not match the template, "
            f"so anything under it was not read."
        )

    if not fields:
        errors.append(
            "No template headings were found. Paste the full report template, "
            "keeping every '### ' heading exactly as written."
        )
        return False, errors, warnings

    part2_ran = "yes" in fields.get("part2_triggered", "").strip().lower()

    for field in FIELDS:
        value = fields.get(field["id"], "")
        required = field["required"]

        if required == "part2" and not part2_ran:
            continue

        if _is_empty(value):
            if required:
                errors.append(f"**{field['section']}:** '{field['heading']}' is empty or missing")
            continue

        _check_one(field, value, errors)

    # Severity is expected wherever a consideration is marked Present
    for n in CONSIDERATIONS:
        verdict = fields.get(f"p{n}_verdict", "")
        severity = fields.get(f"p{n}_severity", "")
        if "present" in verdict.lower() and _is_empty(severity):
            warnings.append(
                f"Consideration {n} is marked Present but no severity is recorded."
            )

    return len(errors) == 0, errors, warnings


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

def build_comment(passed: bool, errors: list[str], warnings: list[str]) -> str:
    lines = []
    if passed:
        lines += [
            "## ✅ Report complete",
            "",
            "Every required field is filled in. This report is ready for review.",
        ]
    else:
        lines += [
            "## Report needs a few additions",
            "",
            f"{len(errors)} field(s) still need attention. Edit the issue and "
            f"this check will run again.",
            "",
            "### To complete",
        ]
        lines += [f"- {e}" for e in errors]

    if warnings:
        lines += ["", "### Worth checking", ""]
        lines += [f"- {w}" for w in warnings]

    lines += [
        "",
        "_Automated completeness check. It confirms the fields are filled in; "
        "it does not assess the analysis itself._",
    ]
    return '\n'.join(lines)


def write_output(passed: bool, errors: list[str], warnings: list[str]):
    with open('validation_result.md', 'w') as f:
        f.write(build_comment(passed, errors, warnings))

    with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"passed={'true' if passed else 'false'}\n")
        f.write(f"error_count={len(errors)}\n")

    print(f"Validation {'PASSED' if passed else 'INCOMPLETE'}")
    for e in errors:
        print(f"  error:   {e}")
    for w in warnings:
        print(f"  warning: {w}")


# ─────────────────────────────────────────────────────────────────────────────
# Template generation — keeps the drafting template in step with the table
# ─────────────────────────────────────────────────────────────────────────────

def emit_template() -> str:
    lines = [
        "<!-- Open Omics ML report template.",
        "     Draft this file in your project repo, then paste the whole thing",
        "     into a new issue on the central repo when it is ready.",
        "     Keep every '### ' heading exactly as written. -->",
        "",
    ]
    current_section = None
    current_note = None

    for field in FIELDS:
        if field["section"] != current_section:
            current_section = field["section"]
            lines += ["", f"## {current_section}", ""]

        note = field.get("note")
        if note and note != current_note:
            current_note = note
            lines += [f"<!-- {note} -->", ""]

        lines.append(f"### {field['heading']}")
        lines.append("")
        if "options" in field:
            lines.append(f"<!-- one of: {' | '.join(field['options'])} -->")
        elif field.get("hint"):
            lines.append(f"<!-- {field['hint']} -->")
        if field["required"] == "part2":
            lines.append("<!-- only if Part II was carried out -->")
        lines.append("")

    return '\n'.join(lines).strip() + '\n'


if __name__ == "__main__":
    if "--emit-template" in sys.argv:
        print(emit_template())
    else:
        body = os.environ.get("ISSUE_BODY", "")
        passed, errors, warnings = validate(body)
        write_output(passed, errors, warnings)
