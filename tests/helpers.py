"""Small hand-built protocol and record for rule tests. Independent of the generator."""

from __future__ import annotations

from typing import Any

from triallab.schema import CasePacket


def packet(**changes: Any) -> CasePacket:
    """A compliant case: eGFR >= 45 and ALT <= 2.5 x ULN, 28-day window, one consent version."""
    raw: dict[str, Any] = {
        "protocol": {
            "study_id": "STUDY-TEST",
            "versions": [{"version": "1.0", "effective_date": "2024-01-01"}],
            "criteria": [
                {"ref": "CRIT-01", "kind": "inclusion", "text": "eGFR of at least 45", "parameter": "egfr",
                 "unit": "mL/min/1.73m2", "eligible_if": {"minimum": 45}, "applies_from_version": "1.0"},
                {"ref": "CRIT-02", "kind": "exclusion", "text": "ALT greater than 2.5 x ULN", "parameter": "alt",
                 "unit": "x ULN", "eligible_if": {"maximum": 2.5}, "applies_from_version": "1.0"},
            ],
            "accepted_units": {"alt": [{"unit": "U/L", "factor": 0.025}]},
            "screening_window_days": 28,
            "retest_policy": "latest result governs",
            "consent_policy": "consent before any procedure",
            "consent_versions": [
                {"ref": "ICFV-1", "version": "1.0", "irb_approval_date": "2023-12-01", "site_effective_date": "2023-12-15"}
            ],
        },
        "record": {
            "participant_id": "P-000001",
            "site_id": "SITE-01",
            "assessments": [
                {"ref": "ASM-1", "parameter": "egfr", "value": 60, "unit": "mL/min/1.73m2", "collected_date": "2024-03-01"},
                {"ref": "ASM-2", "parameter": "alt", "value": 1.2, "unit": "x ULN", "collected_date": "2024-03-01"},
            ],
            "consents": [
                {"ref": "CNS-1", "icf_version": "1.0", "participant_signed": "2024-03-01T09:00+01:00",
                 "investigator_signed": "2024-03-01T09:10+01:00", "document_on_file": True,
                 "verification_status": "verified"}
            ],
            "events": [
                {"ref": "EVT-1", "type": "study_procedure", "occurred": "2024-03-01T10:00+01:00", "description": "Screening"},
                {"ref": "EVT-2", "type": "enrollment", "occurred": "2024-03-10T10:00+01:00", "description": "Enrolled"},
            ],
            "notes": [],
        },
    }  # fmt: skip
    for path, value in changes.items():
        node: Any = raw
        parts = path.split("__")
        for part in parts[:-1]:
            node = node[int(part)] if part.isdigit() else node[part]
        last = parts[-1]
        if isinstance(node, list):
            node[int(last)] = value
        else:
            node[last] = value
    return CasePacket.model_validate(raw)
