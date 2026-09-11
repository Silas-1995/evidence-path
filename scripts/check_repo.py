#!/usr/bin/env python3
"""Check this distribution's metadata, Python syntax and local Markdown links."""

import ast
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml

from validate_report import load_report, validate_report


ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".venv", "__pycache__", "work", "dist"}


def main():
    errors = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
    if not match:
        errors.append("SKILL.md: missing YAML frontmatter")
        frontmatter = {}
    else:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            errors.append("SKILL.md: frontmatter must be a mapping")
            frontmatter = {}
    if frontmatter.get("name") != "evidence-path":
        errors.append("SKILL.md: name must match distribution name evidence-path")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        errors.append("SKILL.md: description must contain 1–1024 characters")
    if set(frontmatter) - {"name", "description", "license", "metadata", "allowed-tools", "compatibility"}:
        errors.append("SKILL.md: unsupported frontmatter")
    metadata = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        errors.append("agents/openai.yaml: expected a mapping")
        metadata = {}
    interface = metadata.get("interface", {})
    if not isinstance(interface, dict):
        errors.append("agents/openai.yaml: interface must be a mapping")
        interface = {}
    short = interface.get("short_description", "")
    if not isinstance(short, str) or not 25 <= len(short) <= 64:
        errors.append("agents/openai.yaml: short_description must contain 25–64 characters")
    prompt = interface.get("default_prompt", "")
    if not isinstance(prompt, str) or "$evidence-path" not in prompt:
        errors.append("agents/openai.yaml: default_prompt must mention $evidence-path")
    if metadata.get("policy") != {"allow_implicit_invocation": True}:
        errors.append("agents/openai.yaml: preserve normal implicit invocation")

    link_count = 0
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if not path.is_file() or IGNORED.intersection(relative.parts):
            continue
        if path.suffix not in {".md", ".py", ".yaml", ".yml", ".json", ".txt"}:
            continue
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            ast.parse(content, filename=str(relative))
        if path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(content)
        if path.suffix != ".md":
            continue
        if "[TODO:" in content:
            errors.append(f"{relative}: unfinished scaffold")
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", content):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            link_count += 1
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f"{relative}: unresolved or escaping local link")

    for path in (ROOT / "examples").glob("*.json"):
        errors.extend(validate_report(load_report(path)))
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Copyright (c) 2026 Jia-Ethan" not in license_text:
        errors.append("LICENSE: missing upstream copyright")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Distribution valid; {link_count} local Markdown file links checked. External URLs and anchors are not checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
