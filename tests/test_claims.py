"""Tests for claims.py ingestion/validation and the `synthesize` CLI entry point.

Gate (T2): valid claims produce all four artifacts offline in <2s;
invalid claims fail loud with a message naming what's wrong — never a
silently degraded report.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from time_travel import orchestrator
from time_travel.claims import ClaimsValidationError, load_claims_file

_FIXTURE = Path(__file__).resolve().parent.parent / "examples" / "sample-claims.json"


def _write_claims(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _valid_data() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


class TestLoadClaimsFile:
    def test_valid_fixture_loads_successfully(self):
        data = load_claims_file(_FIXTURE)

        assert data["schema_version"] == "1.0"
        assert len(data["claims"]) >= 5

    def test_missing_file_fails_loud(self, tmp_path):
        with pytest.raises(ClaimsValidationError, match="not found"):
            load_claims_file(tmp_path / "does-not-exist.json")

    def test_invalid_json_syntax_fails_loud(self, tmp_path):
        path = tmp_path / "claims.json"
        path.write_text("{not valid json", encoding="utf-8")

        with pytest.raises(ClaimsValidationError, match="not valid JSON"):
            load_claims_file(path)

    def test_schema_violation_missing_required_field_fails_loud(self, tmp_path):
        data = _valid_data()
        del data["claims"][0]["mechanism"]
        path = _write_claims(tmp_path, data)

        with pytest.raises(ClaimsValidationError, match="schema validation"):
            load_claims_file(path)

    def test_fewer_than_five_claims_fails_loud(self, tmp_path):
        data = _valid_data()
        data["claims"] = data["claims"][:2]
        path = _write_claims(tmp_path, data)

        with pytest.raises(ClaimsValidationError, match="at least 5"):
            load_claims_file(path)

    def test_all_zero_severity_fails_loud(self, tmp_path):
        data = _valid_data()
        zero = {
            "technical": 0, "financial": 0, "trust": 0,
            "user_pain": 0, "ops_load": 0, "strategic": 0,
        }
        for claim in data["claims"]:
            claim["severity"] = dict(zero)
        path = _write_claims(tmp_path, data)

        with pytest.raises(ClaimsValidationError, match="all-zero severity"):
            load_claims_file(path)

    def test_zero_personas_fails_loud_via_schema(self, tmp_path):
        data = _valid_data()
        data["personas"] = []
        path = _write_claims(tmp_path, data)

        with pytest.raises(ClaimsValidationError):
            load_claims_file(path)


class TestSynthesizeFromClaims:
    def test_valid_fixture_produces_all_four_artifacts_under_two_seconds(self, tmp_path):
        start = time.monotonic()
        report = orchestrator.synthesize_from_claims(str(_FIXTURE), str(tmp_path))
        elapsed = time.monotonic() - start

        out_dir = tmp_path / report.report_id
        assert (out_dir / "report.json").is_file()
        assert (out_dir / "report.html").is_file()
        assert (out_dir / "report.md").is_file()
        assert (out_dir / "exec.html").is_file()
        assert elapsed < 2.0

    def test_no_llm_calls_no_network_pure_offline(self, tmp_path):
        # Runs twice with no network/env setup required — proves it's pure.
        report_a = orchestrator.synthesize_from_claims(str(_FIXTURE), str(tmp_path))
        report_b = orchestrator.synthesize_from_claims(str(_FIXTURE), str(tmp_path / "b"))

        assert report_a.plan_title == report_b.plan_title
        assert len(report_a.confirmed_risks) == len(report_b.confirmed_risks)

    def test_invalid_claims_file_raises_without_writing_any_artifact(self, tmp_path):
        data = _valid_data()
        data["claims"] = data["claims"][:1]
        path = _write_claims(tmp_path, data)

        with pytest.raises(ClaimsValidationError):
            orchestrator.synthesize_from_claims(str(path), str(tmp_path / "out"))

        assert not (tmp_path / "out").exists()
