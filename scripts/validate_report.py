#!/usr/bin/env python3
"""Validate optional Evidence Path reports offline; never execute their checks.

Uses Python 3.10+ standard library only. Success establishes report consistency,
not source authenticity, release inclusion, test execution, or secret absence.
"""

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


MAX_BYTES = 1_048_576
KINDS = ("code", "test", "docs", "issue", "pr", "release", "package", "repo")


def validate_report(report):
    """Return diagnostic field paths without echoing report content."""
    errors = []

    def obj(value, fields, path):
        if not isinstance(value, dict):
            errors.append(f"{path}: expected an object")
            return {}
        if set(value) - set(fields):
            errors.append(f"{path}: unsupported fields")
        for field in fields:
            if field not in value:
                errors.append(f"{path}.{field}: required")
        return value

    def string(value, path):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path}: expected nonempty text")
            return False
        return True

    def array(value, path):
        if not isinstance(value, list):
            errors.append(f"{path}: expected an array")
            return []
        return value

    def choice(value, options, path):
        if not isinstance(value, str) or value not in options:
            errors.append(f"{path}: invalid choice")

    root = obj(report, ("schema_version", "problem", "mode", "evidence",
                        "decision", "verification", "outcome", "limitations"), "report")
    if type(root.get("schema_version")) is not int or root.get("schema_version") != 1:
        errors.append("report.schema_version: expected integer 1")
    string(root.get("problem"), "report.problem")
    choice(root.get("mode"), ("research", "implementation"), "report.mode")
    choice(root.get("outcome"), ("recommended", "changed", "verified", "blocked"), "report.outcome")

    evidence = {}
    for i, item in enumerate(array(root.get("evidence"), "report.evidence")):
        path = f"report.evidence[{i}]"
        item = obj(item, ("id", "kind", "url", "status", "applicability",
                          "claim", "note", "checked_on"), path)
        ident = item.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident):
            errors.append(f"{path}.id: expected a letter followed by letters, digits, underscores or hyphens")
        elif ident in evidence:
            errors.append(f"{path}.id: duplicate evidence ID")
        else:
            evidence[ident] = item
        choice(item.get("kind"), KINDS, f"{path}.kind")
        choice(item.get("status"), ("inspected", "search-only", "unavailable"), f"{path}.status")
        choice(item.get("applicability"), ("matches", "mismatch", "unknown"), f"{path}.applicability")
        string(item.get("claim"), f"{path}.claim")
        string(item.get("note"), f"{path}.note")
        url = item.get("url")
        if string(url, f"{path}.url"):
            try:
                parsed = urlsplit(url)
                valid_url = (parsed.scheme == "https" and bool(parsed.hostname)
                             and not parsed.username and not parsed.password
                             and not re.search(r"[\s\x00-\x1f\x7f\\]", url))
                _ = parsed.port
            except ValueError:
                valid_url = False
            if not valid_url:
                errors.append(f"{path}.url: expected an HTTPS URL without credentials or whitespace")
        checked_on = item.get("checked_on")
        try:
            if not isinstance(checked_on, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked_on):
                raise ValueError
            date.fromisoformat(checked_on)
        except ValueError:
            errors.append(f"{path}.checked_on: expected a valid YYYY-MM-DD date")

    def references(value, path):
        selected = []
        seen = set()
        for i, ident in enumerate(array(value, path)):
            loc = f"{path}[{i}]"
            if not isinstance(ident, str) or ident not in evidence:
                errors.append(f"{loc}: unknown evidence ID")
            elif ident in seen:
                errors.append(f"{loc}: duplicate evidence reference")
            else:
                seen.add(ident)
                selected.append(evidence[ident])
        return selected

    decision = obj(root.get("decision"), ("summary", "basis", "evidence_ids", "availability"), "report.decision")
    string(decision.get("summary"), "report.decision.summary")
    choice(decision.get("basis"), ("upstream", "local", "hypothesis"), "report.decision.basis")
    selected = references(decision.get("evidence_ids"), "report.decision.evidence_ids")
    if decision.get("basis") == "upstream":
        if not selected:
            errors.append("report.decision.evidence_ids: upstream basis requires evidence")
        if any(item.get("status") != "inspected" or item.get("applicability") != "matches" for item in selected):
            errors.append("report.decision.evidence_ids: upstream basis requires inspected, applicable evidence")

    availability = obj(decision.get("availability"), ("status", "version", "evidence_ids"), "report.decision.availability")
    choice(availability.get("status"), ("released", "prerelease", "unreleased", "unknown", "not-applicable"), "report.decision.availability.status")
    release_evidence = references(availability.get("evidence_ids"), "report.decision.availability.evidence_ids")
    if availability.get("status") in ("released", "prerelease"):
        string(availability.get("version"), "report.decision.availability.version")
        if not any(item.get("kind") in ("release", "package")
                   and item.get("status") == "inspected"
                   and item.get("applicability") == "matches" for item in release_evidence):
            errors.append("report.decision.availability: published status requires inspected, applicable release or package evidence")
    elif availability.get("version") is not None:
        errors.append("report.decision.availability.version: use null unless publication is established")

    checks = []
    for i, check in enumerate(array(root.get("verification"), "report.verification")):
        path = f"report.verification[{i}]"
        check = obj(check, ("check", "status", "detail"), path)
        string(check.get("check"), f"{path}.check")
        string(check.get("detail"), f"{path}.detail")
        choice(check.get("status"), ("passed", "failed", "not-run", "blocked"), f"{path}.status")
        checks.append(check)
    if not checks:
        errors.append("report.verification: include an executed check or an explicit next check")
    if root.get("outcome") in ("changed", "verified") and root.get("mode") != "implementation":
        errors.append("report.outcome: changed or verified requires implementation mode")
    if root.get("outcome") == "verified":
        if not checks or any(check.get("status") != "passed" for check in checks):
            errors.append("report.outcome: verified requires all listed checks to have passed")
        if decision.get("basis") == "hypothesis":
            errors.append("report.decision.basis: a verified outcome must describe established local or upstream evidence")

    limitations = array(root.get("limitations"), "report.limitations")
    for i, limitation in enumerate(limitations):
        string(limitation, f"report.limitations[{i}]")
    if root.get("outcome") == "blocked" and not limitations:
        errors.append("report.limitations: explain the blocked outcome")
    return errors


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("non-finite JSON number")


def load_report(path):
    """Bound input size and reject ambiguous JSON. No network or writes."""
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("report exceeds size limit")
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="UTF-8 JSON report, at most 1 MiB")
    args = parser.parse_args(argv)
    try:
        errors = validate_report(load_report(args.report))
    except (OSError, ValueError, RecursionError):
        print("Unable to read report: use a readable UTF-8 JSON file with unique keys, finite numbers, and size at most 1 MiB.", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Report is consistent. Source truth and actual verification still require review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
