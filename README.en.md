# Evidence Path

**From open-source evidence to an implementation that fits your project.**

[简体中文](README.md) · [Skill entrypoint](SKILL.md) · [Design review](docs/design.md) · [MIT](LICENSE)

Evidence Path helps coding agents investigate engineering bugs, integration blockers, and library choices. It establishes local versions and constraints, inspects upstream code and release evidence, then recommends or implements a small applicable change according to the user's request.

Independently maintained derivative of [PavedPath Code by Jia-Ethan](https://github.com/Jia-Ethan/pavedpath-code). Original MIT attribution is preserved in [LICENSE](LICENSE); the reviewed revision and changes are documented in [NOTICE](NOTICE.md).

## Changes from the original

- A 54-line entrypoint with detailed guidance loaded only when relevant.
- Search stopping criteria and tool fallbacks without mandatory research logs.
- Explicit distinction between closed issues, merged fixes, published packages, and local verification.
- Runtime, API, deployment and reuse constraints checked before popularity.
- Research-only and implementation scope remain distinct.
- An optional offline report validator detects inconsistent evidence and verification declarations.

The entrypoint contains about 57% fewer whitespace-delimited words than the reviewed original. This measures document size, not model tokens, runtime, or task success. See the [design review](docs/design.md).

## Install

Clone the whole repository into your runtime's active skills directory under `evidence-path`. No service or credentials are bundled. Use an available GitHub connector, `gh`, or browsing tools for research. Python 3.10+ is needed only for the optional report validator; repository maintenance also uses PyYAML.

The current Codex documentation lists `~/.agents/skills` for personal skills. Respect the active path in an existing environment and avoid duplicate installations. [Official skill documentation](https://learn.chatgpt.com/docs/build-skills)

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Silas-1995/evidence-path.git "$HOME/.agents/skills/evidence-path"
```

Windows PowerShell:

```powershell
$skillRoot = Join-Path $HOME '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
git clone https://github.com/Silas-1995/evidence-path.git (Join-Path $skillRoot 'evidence-path')
```

Inspect local changes before updating with `git pull --ff-only` in the installed directory. To pin a clean installation, use `git checkout v1.0.0`; switch back to `main` before following branch updates. Other runtimes must support this directory format and their own skill discovery mechanism. Cross-runtime compatibility is not claimed as tested.

## Use

```text
Use $evidence-path to investigate this build error after a dependency upgrade.
Check the resolved versions, inspect an applicable upstream fix, make the local change, and run the relevant checks.
```

```text
Use $evidence-path to compare libraries for local PDF table extraction on Python 3.11.
Research only. Explain compatibility, license, adaptation cost, and how we could verify the recommendation.
```

```text
Use $evidence-path to check whether this merged PR actually shipped in a version we can install.
```

The skill supports implicit discovery and explicit invocation. It preserves the user's language and chosen stack. Routine edits with an evident local answer skip research; offline requests stay local.

## Optional report validation

Most answers should remain concise prose. For structured handoff, use the [format](references/report-format.md) and [synthetic example](examples/report.json):

```sh
python scripts/validate_report.py examples/report.json
```

The validator checks declared consistency, does not use the network or execute checks, and cannot establish factual truth or absence of secrets. Example findings and URLs are synthetic.

## Development

```sh
python -m pip install -r requirements-dev.txt
python scripts/check_repo.py
python -m unittest discover -s tests -v
```

[CI](https://github.com/Silas-1995/evidence-path/actions/workflows/validate.yml) checks metadata, local documentation links, examples, and report invariants on Windows and Linux. [Behavioral scenarios](evals/scenarios.md) support manual or separately authorized agent evaluation; they are not automated behavior benchmarks.

MIT licensed. See [LICENSE](LICENSE) and [NOTICE](NOTICE.md).
