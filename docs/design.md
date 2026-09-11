# Why this derivative exists

Review date: 2026-09-11. Source: [PavedPath Code at 97a319f](https://github.com/Jia-Ethan/pavedpath-code/tree/97a319fcfd3f9b68976690e04f3b511d6171a300). Evidence Path is independently maintained, with attribution preserved.

## What was worth keeping

The original correctly centers the local engineering problem, uses GitHub as evidence rather than a link collection, prioritizes problem fit over popularity, and aims for minimal adaptation with verification. Its references explain evidence ranking and extraction. These are the foundation of Evidence Path.

## Review findings and changes

| Observation in the reviewed source | Consequence | Change |
| --- | --- | --- |
| Workflow, ranking, output requirements, and subagent handling recur across the main file and references | Larger entrypoint and repeated process obligations | A short central workflow, with search, evidence, adaptation and optional reporting references |
| Requires reporting whether subagents were used or skipped, including reasons | Routine answers carry orchestration details unrelated to the user's decision | Delegation stays governed by the host/user; no mandatory subagent trace |
| Encourages high-star discovery while also saying exact evidence wins | Popularity can affect discovery before fit has been established | Hard applicability gates first; popularity is optional context |
| Lists merged PRs among highest-priority evidence; mentions release availability without a concrete chain | A reader could conflate an accepted fix with an installable solution | Explicit package/release inclusion and runtime checks; prerelease/unreleased states |
| No concrete search stopping rule | Easy to continue collecting adjacent evidence after a path is clear | Small shortlist, targeted refinement, then stop or label a hypothesis |
| Some extraction rules are specific to generated browser scripts | A single historical failure becomes a general instruction | Explain verification at the actual generated/runtime boundary |
| Roadmap suggests structured output, offline fixtures and CI | No executable guard for report consistency | Optional report contract, validator, synthetic fixture, and CI |

These are design judgments about the instructions, not measured claims about the original skill's real-world failure rate.

## Size measurement

| Measure | Reviewed PavedPath Code | Evidence Path v1.0.0 |
| --- | ---: | ---: |
| `SKILL.md` lines | 136 | 54 |
| Whitespace-delimited words (`len(text.split())`) | 1,940 | 831 |

This is a 57.2% reduction in entrypoint words. The new repository is larger overall because it includes optional tooling, tests, examples, and public documentation. Those files are not required reading for ordinary skill use. No token or latency benchmark was run.

## Deliberate limits

- The validator validates declared relationships. It cannot prove that a maintainer said something, a package shipped, or a command actually ran.
- The skill is not a search service, autonomous crawler, deployment tool, or blanket authorization to execute repository instructions.
- JSON is optional and intentionally compact. More fields would create maintenance and transcription costs without improving every task.
- Agent behavior depends on the host, model and task. The scenario suite is a reproducible evaluation plan, not an asserted pass rate.

## Validation evidence

Repository structure, local Markdown file targets, YAML metadata, Python syntax, the synthetic report, and report invariants are checked by the included tools. CI repeats those checks across operating systems and Python versions. The bundled skill-creator validator was also run during preparation.

GitHub CLI command field names were checked against the installed CLI; a public repository search plus scoped issue/PR searches were exercised against the original project. Empty scoped search results were treated as empty results, not as proof of a fix. Installation paths were checked against the [official skill documentation](https://learn.chatgpt.com/docs/build-skills); CLI search differences were checked against the [GitHub CLI manual](https://cli.github.com/manual/gh_search_code).

This preparation does not establish end-to-end agent performance. Suggested next evaluations are in [scenarios.md](../evals/scenarios.md).
