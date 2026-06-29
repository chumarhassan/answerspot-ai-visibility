"""Tests that the public free-audit input validation rejects junk (§8)."""
import pytest
from pydantic import ValidationError

from schemas import AuditRequest


def test_valid_audit_request():
    req = AuditRequest(name="  Acme Roofing ", category="roofer", city="Austin")
    assert req.name == "Acme Roofing"  # trimmed


def test_empty_name_rejected():
    with pytest.raises(ValidationError):
        AuditRequest(name="   ", category="roofer", city="Austin")


def test_control_chars_rejected():
    with pytest.raises(ValidationError):
        AuditRequest(name="Acme\x00Roofing", category="roofer", city="Austin")


def test_overlong_name_rejected():
    with pytest.raises(ValidationError):
        AuditRequest(name="x" * 201, category="roofer", city="Austin")


def test_missing_field_rejected():
    with pytest.raises(ValidationError):
        AuditRequest(name="Acme", category="roofer")  # type: ignore[call-arg]
