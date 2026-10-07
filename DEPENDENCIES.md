# Dependencies

## Required

The skill itself has no Python package dependency. Its core execution uses the host language model and host file tools.

## Optional workflow checker

`scripts/check_workflow.py` requires Python 3.10 or later and uses only the Python standard library. It supports:

- `check-skill PATH`
- `check-project PROJECT`
- `invalidate PROJECT --question q --change algorithm [--apply]`

The checker verifies workflow structure and project-state consistency. Its output does not establish that a mathematical model is valid or that a project has passed an independent review.

## Optional modeling and visualization packages

Install only the packages needed by a specific project. Possible choices include NumPy, SciPy, pandas, scikit-learn, statsmodels, NetworkX, OR-Tools, CVXPY, and Matplotlib. They are not installed as a single bundle and are not required to use the skill.

Some optimization workflows also need a solver backend. Confirm that the selected solver is installed, usable from the chosen library, and covered by an appropriate license before relying on it.

## Optional external resources

Algorithm references included with the skill are the default. External textbooks, modeling assets, and visualization libraries are optional and must be supplied by the user. Local path overrides belong in `.interactive-mm/resource-overrides.json`, with string values under `algorithm_textbooks`, `modeling_assets`, and `viz_library`. Do not commit machine-specific overrides.

No LaTeX installation is required. Full paper chapter writing and compilation are outside the skill's scope. An academic pipeline skill may be used separately, but it is not a dependency.

The project override takes precedence over an optional host-only `resources.local.json` in the installed skill directory. Neither file is part of the published package. Existing local textbook libraries may remain connected this way without copying them into the repository.

Independent review requires both host support for a separate reviewer and authorization to execute that delegation. Otherwise, describe the result as host self-checking rather than independent acceptance.


