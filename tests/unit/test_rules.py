"""Each protocol rule is transparent and testable on its own, on hand-built records."""

from __future__ import annotations

from helpers import packet
from triallab.clinical import rules as r
from triallab.clinical.rules import RULES, evaluate_rules, order, parse_when


def codes(findings) -> set[tuple[str, str, str]]:
    return {f.key() for f in findings}


def run(rule, p):
    return codes(rule(p.protocol, p.record))


def test_compliant_record_fires_no_rule() -> None:
    p = packet()
    assert evaluate_rules(p.protocol, p.record) == []
    assert len(RULES) == 8


def test_threshold_rule_fires_only_outside_inclusive_limits() -> None:
    assert run(r.rule_eligibility_thresholds, packet(record__assessments__0__value=45)) == set()  # exactly at the limit
    assert run(r.rule_eligibility_thresholds, packet(record__assessments__0__value=44)) == {
        ("eligibility", "issue", "criterion_not_met")
    }
    assert run(r.rule_eligibility_thresholds, packet(record__assessments__1__value=2.6)) == {
        ("eligibility", "issue", "criterion_not_met")
    }


def test_threshold_rule_converts_only_listed_units() -> None:
    converted_fail = packet(record__assessments__1__value=120, record__assessments__1__unit="U/L")  # 3.0 x ULN
    assert run(r.rule_eligibility_thresholds, converted_fail) == {("eligibility", "issue", "criterion_not_met")}
    converted_ok = packet(record__assessments__1__value=80, record__assessments__1__unit="U/L")  # 2.0 x ULN
    assert evaluate_rules(converted_ok.protocol, converted_ok.record) == []


def test_not_enrolled_means_no_eligibility_finding() -> None:
    p = packet(record__assessments__0__value=10)
    p.record.events = [e for e in p.record.events if e.type != "enrollment"]
    assert evaluate_rules(p.protocol, p.record) == []


def test_missing_tests_rule_covers_absent_results_and_unusable_units() -> None:
    absent = packet()
    absent.record.assessments = absent.record.assessments[:1]
    assert run(r.rule_missing_eligibility_tests, absent) == {("eligibility", "missing", "required_assessment_missing")}
    for unit in (None, "ukat/L"):
        assert run(r.rule_missing_eligibility_tests, packet(record__assessments__1__unit=unit)) == {
            ("eligibility", "missing", "result_unusable")
        }
    assert run(r.rule_missing_eligibility_tests, packet(record__assessments__1__value=None)) == {
        ("eligibility", "missing", "result_unusable")
    }


def test_timing_rule_checks_window_and_post_enrollment_results() -> None:
    edge = packet(record__assessments__0__collected_date="2024-02-11")  # exactly 28 days before enrollment
    assert run(r.rule_screening_enrollment_timing, edge) == set()
    late = packet(record__assessments__0__collected_date="2024-02-10")  # 29 days
    assert run(r.rule_screening_enrollment_timing, late) == {("eligibility", "issue", "assessment_outside_window")}
    after = packet(record__assessments__0__collected_date="2024-03-11")
    assert run(r.rule_screening_enrollment_timing, after) == {("eligibility", "issue", "assessment_after_enrollment")}


def test_latest_result_before_enrollment_governs() -> None:
    p = packet(record__assessments__0__value=30)  # fails
    p.record.assessments.append(
        p.record.assessments[0].model_copy(update={"ref": "ASM-3", "value": 62, "collected_date": "2024-03-04"})
    )
    assert evaluate_rules(p.protocol, p.record) == []


def test_consent_completion_never_treats_missing_documents_as_an_issue() -> None:
    none = packet()
    none.record.consents = []
    assert run(r.rule_consent_completion, none) == {("consent", "missing", "consent_record_missing")}
    pending = packet(record__consents__0__verification_status="pending")
    assert run(r.rule_consent_completion, pending) == {("consent", "missing", "consent_unverified")}
    off_file = packet(record__consents__0__document_on_file=False)
    assert run(r.rule_consent_completion, off_file) == {("consent", "missing", "consent_unverified")}
    unsigned = packet(record__consents__0__investigator_signed=None)
    assert run(r.rule_consent_completion, unsigned) == {("consent", "issue", "consent_signature_incomplete")}


def test_consent_version_rule_uses_the_version_in_effect_on_the_signing_date() -> None:
    p = packet()
    p.protocol.consent_versions.append(
        p.protocol.consent_versions[0].model_copy(
            update={"ref": "ICFV-2", "version": "2.0", "site_effective_date": "2024-03-01"}
        )
    )
    assert run(r.rule_consent_version_applicability, p) == {("consent", "issue", "consent_version_not_current")}
    p.record.consents[0].icf_version = "2.0"  # signed on the first day the new version applies
    assert run(r.rule_consent_version_applicability, p) == set()
    p.record.consents[0].participant_signed = "2024-02-29T09:00+01:00"  # the day before: old version was right
    p.record.consents[0].icf_version = "1.0"
    assert run(r.rule_consent_version_applicability, p) == set()


def test_consent_timing_rule_orders_instants_across_utc_offsets() -> None:
    after = packet(record__consents__0__participant_signed="2024-03-01T10:30+01:00")
    assert run(r.rule_consent_timing, after) == {("consent", "issue", "consent_after_procedure")}
    # Clock digits say 08:30 < 10:00, but 08:30-05:00 is 13:30 UTC and the procedure was 09:00 UTC.
    offset = packet(record__consents__0__participant_signed="2024-03-01T08:30-05:00")
    assert run(r.rule_consent_timing, offset) == {("consent", "issue", "consent_after_procedure")}
    same_day = packet(record__consents__0__participant_signed="2024-03-01")
    assert run(r.rule_consent_timing, same_day) == {("consent", "missing", "consent_order_undetermined")}
    day_before = packet(record__consents__0__participant_signed="2024-02-29")
    assert run(r.rule_consent_timing, day_before) == set()


def test_reconsent_rule_needs_a_later_event_and_a_required_version() -> None:
    p = packet()
    p.protocol.consent_versions.append(
        p.protocol.consent_versions[0].model_copy(
            update={"ref": "ICFV-2", "version": "2.0", "site_effective_date": "2024-03-05", "reconsent_required": True}
        )
    )
    assert run(r.rule_reconsent_evidence, p) == {("consent", "missing", "reconsent_record_missing")}
    p.record.consents.append(
        p.record.consents[0].model_copy(
            update={"ref": "CNS-2", "icf_version": "2.0", "participant_signed": "2024-03-10T09:00+01:00"}
        )
    )
    assert run(r.rule_reconsent_evidence, p) == set()
    p.protocol.consent_versions[1].reconsent_required = False
    p.record.consents.pop()
    assert run(r.rule_reconsent_evidence, p) == set()


def test_inconsistent_documentation_rule_finds_conflicts_in_both_domains() -> None:
    p = packet()
    p.record.assessments.append(p.record.assessments[0].model_copy(update={"ref": "ASM-3", "value": 30}))
    assert run(r.rule_inconsistent_documentation, p) == {("eligibility", "conflict", "conflicting_results")}
    assert run(r.rule_eligibility_thresholds, p) == set()  # a contradiction is not reported as a documented issue
    q = packet()
    q.record.consents.append(
        q.record.consents[0].model_copy(update={"ref": "CNS-2", "participant_signed": "2024-03-01T12:00+01:00"})
    )
    assert run(r.rule_inconsistent_documentation, q) == {("consent", "conflict", "consent_timestamp_conflict")}
    assert run(r.rule_consent_timing, q) == set()


def test_order_helper() -> None:
    assert order(parse_when("2024-03-01T09:00+01:00"), parse_when("2024-03-01T09:00+01:00")) == "before"
    assert order(parse_when("2024-03-01"), parse_when("2024-03-01T09:00+01:00")) == "undetermined"
    assert order(parse_when("2024-03-02"), parse_when("2024-03-01T23:00+01:00")) == "after"
