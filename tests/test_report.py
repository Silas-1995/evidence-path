"""Report invariants: evidence, release availability, and honest verification."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_report import MAX_BYTES, load_report, validate_report  # noqa: E402


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((ROOT / "examples/report.json").read_text(encoding="utf-8"))

    def assert_invalid(self, field):
        errors = validate_report(self.report)
        self.assertTrue(any(field in error for error in errors), errors)

    def test_synthetic_research_report(self):
        self.assertEqual(validate_report(self.report), [])

    def test_offline_local_report_needs_no_upstream(self):
        self.report["evidence"] = []
        self.report["decision"].update(basis="local", evidence_ids=[])
        self.report["decision"]["availability"] = dict(status="not-applicable", version=None, evidence_ids=[])
        self.assertEqual(validate_report(self.report), [])

    def test_local_implementation_can_be_verified(self):
        self.test_offline_local_report_needs_no_upstream()
        self.report.update(mode="implementation", outcome="verified")
        self.report["verification"][0].update(status="passed", detail="Both cases observed in the isolated test fixture.")
        self.assertEqual(validate_report(self.report), [])

    def test_search_snippet_cannot_support_upstream_basis(self):
        for state in ("search-only", "unavailable"):
            with self.subTest(state=state):
                self.report["evidence"][0]["status"] = state
                self.assert_invalid("decision.evidence_ids")

    def test_unknown_or_mismatching_evidence_is_not_support(self):
        for state in ("unknown", "mismatch"):
            with self.subTest(state=state):
                self.report["evidence"][0]["applicability"] = state
                self.assert_invalid("decision.evidence_ids")

    def test_rejected_candidate_can_be_kept_without_supporting_choice(self):
        candidate = deepcopy(self.report["evidence"][0])
        candidate.update(id="Rejected", applicability="mismatch")
        self.report["evidence"].append(candidate)
        self.assertEqual(validate_report(self.report), [])

    def test_merged_pr_is_not_publication_proof(self):
        self.report["decision"]["availability"]["evidence_ids"] = ["E1"]
        self.assert_invalid("availability")

    def test_uninspected_release_is_not_publication_proof(self):
        self.report["evidence"][1]["status"] = "search-only"
        self.assert_invalid("availability")

    def test_unreleased_fix_can_be_recommended_as_a_patch(self):
        self.report["decision"]["availability"] = dict(status="unreleased", version=None, evidence_ids=["E1"])
        self.assertEqual(validate_report(self.report), [])

    def test_prerelease_is_distinct_and_requires_proof(self):
        self.report["decision"]["availability"].update(status="prerelease", version="2.4.1-rc1")
        self.assertEqual(validate_report(self.report), [])
        self.report["decision"]["availability"]["evidence_ids"] = []
        self.assert_invalid("availability")

    def test_published_version_required(self):
        self.report["decision"]["availability"]["version"] = None
        self.assert_invalid("availability.version")

    def test_unrun_failed_and_blocked_checks_prevent_verified(self):
        self.report.update(mode="implementation", outcome="verified")
        for state in ("not-run", "failed", "blocked"):
            with self.subTest(state=state):
                self.report["verification"][0]["status"] = state
                self.assert_invalid("report.outcome")

    def test_research_cannot_claim_implementation(self):
        for state in ("changed", "verified"):
            with self.subTest(state=state):
                self.report["outcome"] = state
                self.assert_invalid("report.outcome")

    def test_verified_needs_at_least_one_check(self):
        self.report.update(mode="implementation", outcome="verified", verification=[])
        self.assert_invalid("verification")

    def test_research_includes_a_next_check(self):
        self.report["verification"] = []
        self.assert_invalid("verification")

    def test_blocked_requires_an_explanation(self):
        self.report.update(outcome="blocked", limitations=[])
        self.assert_invalid("limitations")

    def test_dangling_and_duplicate_ids(self):
        self.report["decision"]["evidence_ids"] = ["Missing"]
        self.assert_invalid("decision.evidence_ids")
        self.report["decision"]["evidence_ids"] = ["E1", "E1"]
        self.assert_invalid("decision.evidence_ids")
        self.report["decision"]["evidence_ids"] = ["E1"]
        self.report["evidence"].append(deepcopy(self.report["evidence"][0]))
        self.assert_invalid(".id")

    def test_malformed_types_produce_diagnostics_not_tracebacks(self):
        for value in (None, [], True, 1, "text"):
            with self.subTest(root=value):
                self.assertTrue(validate_report(value))
        for field in self.report:
            for value in (None, [], {}, True):
                report = deepcopy(self.report)
                report[field] = value
                with self.subTest(field=field, type=type(value).__name__):
                    self.assertIsInstance(validate_report(report), list)

    def test_unknown_fields_do_not_disappear(self):
        self.report["decison"] = {}
        self.assert_invalid("unsupported fields")

    def test_invalid_dates_and_urls(self):
        self.report["evidence"][0]["checked_on"] = "2026-02-30"
        self.assert_invalid("checked_on")
        for url in ("https://user:secret@example.com", "file:///tmp/report", "https://[broken", "https://example.com:bad", "https://example.com/a\nb"):
            with self.subTest(url_kind=url.split(":")[0]):
                self.report["evidence"][0]["url"] = url
                self.assert_invalid(".url")

    def test_nested_invalid_types(self):
        for section in ("evidence", "verification"):
            for value in (None, [], {}, True):
                report = deepcopy(self.report)
                report[section] = [value]
                self.assertTrue(validate_report(report))
        self.report["decision"]["evidence_ids"] = [{}]
        self.assert_invalid("evidence_ids")

    def test_loader_rejects_ambiguous_and_oversized_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            for text in ('{"x":1,"x":2}', '{"x":NaN}', ' ' * (MAX_BYTES + 1)):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_report(path)

    def test_cli_never_echoes_input_or_runs_check(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            report_path = folder / "report.json"
            marker = folder / "must-not-exist"
            self.report["verification"][0]["check"] = f"touch {marker}"
            report_path.write_text(json.dumps(self.report), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_report.py"), str(report_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists())
            self.report["evidence"][0]["id"] = "DO_NOT_ECHO_THIS_CONTENT!"
            report_path.write_text(json.dumps(self.report), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_report.py"), str(report_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("DO_NOT_ECHO_THIS_CONTENT", result.stdout + result.stderr)
            report_path.write_text('{"DO_NOT_ECHO_THIS_CONTENT":', encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_report.py"), str(report_path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("DO_NOT_ECHO_THIS_CONTENT", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
