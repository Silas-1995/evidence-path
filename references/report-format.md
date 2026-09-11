# Optional structured handoff, version 1

Use JSON only when requested or useful for a downstream handoff. Normal answers can stay in prose. Start with [the synthetic example](../examples/report.json); replace all fixture facts and URLs with actual observations. Save real reports in the user's intended work area, not this installed skill or a public repository by default.

Run from the skill directory:

```sh
python scripts/validate_report.py /path/to/report.json
```

Requires Python 3.10+; no extra packages, network access, file writes, or command execution. Exit codes: `0` consistent, `1` contract errors, `2` unreadable/invalid input or CLI usage. Diagnostics identify fields and never print their supplied values. The input limit is 1 MiB.

## Contract

All fields below are required. Unsupported fields are rejected to catch typos. Strings must be nonempty unless a `null` is explicitly allowed. Empty evidence and limitations arrays are valid when honest.

| Field | Values and meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `problem` | Concrete goal, relevant versions/environment and constraints |
| `mode` | `research` or `implementation`, from user scope |
| `evidence` | Array of evidence records below, including rejected or unavailable leads if useful |
| `decision.summary` | Chosen path and local adaptation |
| `decision.basis` | `upstream`, `local`, or `hypothesis` |
| `decision.evidence_ids` | Unique IDs supporting this choice; for `upstream`, all must be inspected and applicable |
| `decision.availability.status` | `released`, `prerelease`, `unreleased`, `unknown`, or `not-applicable` |
| `decision.availability.version` | Published package version for `released`/`prerelease`; otherwise `null` |
| `decision.availability.evidence_ids` | Evidence of the chosen publication status; released/prerelease requires an inspected, applicable `release` or `package` source |
| `verification` | At least one check record; include planned checks as `not-run` |
| `outcome` | `recommended`, `changed`, `verified`, or `blocked` |
| `limitations` | Array of material gaps; required to be nonempty for a blocked outcome |

Each evidence record has `id`, `kind`, `url`, `status`, `applicability`, `claim`, `note`, and `checked_on`:

- `id`: unique identifier beginning with a letter, followed by letters, digits, underscores, or hyphens.
- `kind`: `code`, `test`, `docs`, `issue`, `pr`, `release`, `package`, or `repo`.
- `url`: direct HTTPS source URL without embedded user/password credentials. Use actual revision links where appropriate. Query parameters are allowed but must be reviewed for secrets.
- `status`: `inspected`, `search-only`, or `unavailable`. Describe only what was actually inspected.
- `applicability`: `matches`, `mismatch`, or `unknown`; this is an explicit judgment, not something the script infers.
- `claim`: precise claim supported by the source.
- `note`: matching versions/conditions, contradictions, or missing evidence.
- `checked_on`: inspection or access-attempt date, `YYYY-MM-DD`.

Each check has `check` (command or manual procedure), `status` (`passed`, `failed`, `not-run`, or `blocked`), and `detail` (observed result or reason it did not run). Describe the current validation state; summarize superseded failures in `detail` if relevant. A `verified` outcome requires implementation mode, all listed checks passed, and a local or upstream basis. `changed` means work was applied without claiming complete verification.

## What validation does not prove

The script rejects dangling evidence IDs, unsupported confidence claims in declared fields, a PR used as the sole publication proof, and an unrun check paired with a verified outcome. It cannot establish whether URLs exist, a claim is true, a package contains a fix, a check was really run, a demo works, a license is suitable, or a report is free of sensitive data. It does not understand contradictions hidden in prose. A human or agent must still inspect the sources and verify the behavior.
