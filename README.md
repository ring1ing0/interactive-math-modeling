# Interactive Math Modeling

An explicitly invoked Codex skill for evidence-driven mathematical modeling. It guides a project from whole-problem structure through unit-level decisions, review, visualization, implementation, and final checks while preserving decisions and evidence in project files.

## What it does

- Builds a shared whole-problem foundation, then works through each question and unit in order.
- Checks the modeling and writing scope at each step so assumptions, evidence, and deliverables stay aligned.
- Uses a default per-unit decision cycle: **D1** for problem framing and modeling choices, **D2** for the algorithm decision, followed by acceptance checks for each question.
- Keeps major reviews, chart planning, code contracts, and result freeze at the appropriate question-level gates.
- After all questions are frozen, can provide a rough award-potential range with a confidence level, evidence, deductions, and improvement suggestions. This is an evidence-based estimate, not a precise probability or guarantee. When there is no manuscript, the evidence basis is modeling artifacts; manuscript quality and formatting are explicitly unassessed.

The skill can complete the modeling workflow without a finished paper. It does not draft or compile full manuscript chapters.

## Install

Clone the repository into a Codex skills directory:

```sh
git clone https://github.com/ring1ing0/interactive-math-modeling.git ~/.codex/skills/interactive-math-modeling
```

Alternatively, download or clone this directory into `$CODEX_HOME/skills/interactive-math-modeling` when `CODEX_HOME` is set. Restart or refresh the host so it discovers the skill, then invoke it explicitly with `$interactive-math-modeling` or ask to start this workflow.

## Validate

Python 3.10 or later is needed only for the optional workflow checker. From this directory, run:

```sh
python scripts/check_workflow.py check-skill .
python scripts/check_workflow.py check-project PATH
python scripts/check_workflow.py invalidate PATH --question q --change algorithm
```

Add `--apply` to `invalidate` to write the invalidation. Review the proposed change first; the checker does not replace substantive modeling review.

## Resources and local configuration

The bundled algorithm-selection guide and catalog are the default references. Optional external textbooks, modeling assets, and visualization libraries can be configured locally in `.interactive-mm/resource-overrides.json` using the keys `algorithm_textbooks`, `modeling_assets`, and `viz_library` (each value is a path string). Keep that local override file out of the repository.

External textbooks are optional and are not included. The repository contains workflow materials and indexes, not textbook source text.

## Limits

The core workflow uses the host language model and its file tools. Independent review requires a host that can delegate to a separate reviewer and is authorized to execute that delegation. Without both capabilities, the skill must describe the review as host self-checking, not independent acceptance. Optional numerical and optimization libraries and solver backends are project-specific. Check solver availability and license terms separately before relying on them.

The workflow does not promise an award, a particular score, or a precise probability. A potential range and confidence level summarize the available evidence and should be read with the stated deductions and limitations.

## Contents

- `SKILL.md`: entry point and workflow rules
- `references/`: workflow, evidence, algorithm, visualization, and resource guidance
- `templates/`: project records and decision artifacts
- `agents/`: host integration metadata
- `scripts/check_workflow.py`: optional structural and state checks
- `tests/`: checker-focused validation material
