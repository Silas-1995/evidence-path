# Evaluate a path, not a popularity score

Read this for candidate selection, conflicting reports, or release/version uncertainty.

## Applicability gates

First reject or hold candidates that cannot meet a hard requirement: supported runtime, package version, required interface, deployment target, offline operation, data/auth model, or a relevant license condition. Record unknowns instead of treating them as a pass. A high star count cannot compensate for a failed gate.

Among viable candidates, prefer the strongest direct evidence, then the lowest adaptation and maintenance cost. A small official example can be stronger than a large adjacent project. Recent pushes may be automated; inspect the relevant code and maintenance surface when that matters.

## Evidence strength

| Evidence | Supports | Does not establish by itself |
| --- | --- | --- |
| Matching source and tests at a known revision | Behavior under specified conditions | That the code is in an installable release |
| Relevant release notes plus package/tag inspection | A fix is present in a published artifact | Compatibility with the user's full environment |
| Maintainer analysis or merged PR with relevant diff | Cause or intended fix | Release availability or local success |
| Matching report with reproducible workaround | A path worth testing | General applicability or supported long-term use |
| Search snippet, stars, unresolved discussion | A discovery lead | A confirmed fix |

Use plain conclusions: **locally verified**, **upstream-supported but untested locally**, or **hypothesis**. These labels describe different kinds of knowledge, not numerical probabilities. Attach uncertainty to the specific claim that lacks evidence.

## Release chain

For a recommended version change, establish:

`local resolved version → relevant behavior/fix → release source/artifact → installable package version → local check`

Read the fix's relevant code and tests. Check whether it targeted the user's release line. Confirm the specific package's published version and runtime requirements through the project's official release surface or package registry. When practical, inspect source in that artifact. Do not infer inclusion from merge time, a greater version number, a branch name, or a generic “latest release” entry. Note prereleases explicitly. If only an unreleased fix exists, present that limitation and evaluate a local patch or supported workaround within scope.

For a stable source link, use the observed commit revision and actual path; add line numbers only after reading those lines. Record the inspection date for mutable docs, issue states, activity, demo availability, and metadata. Cite observations narrowly. “This test handles X” is different from “this library handles every X.”

## Compact working notes

For consequential evidence, keep enough context to reconstruct the decision:

- Claim and direct source; revision/version and inspection date when relevant.
- Actual matching conditions, plus mismatches and unknowns.
- What can be reused; what must change locally.
- Verification that would distinguish this explanation from alternatives.

The notes need not become a file or a full table in a simple answer. The optional [report format](report-format.md) is for structured handoff.

## Contradictions and duplicates

Follow each claim to its original evidence. Several issues linking one PR represent one proposed fix, not independent confirmations. Prefer direct behavior and exact environment matches over recency alone. Check whether apparently conflicting results use different platforms, dependency resolutions, feature flags, or APIs. If a conflict remains, show the two explanations and the smallest check that would discriminate between them. Do not manufacture consensus.
