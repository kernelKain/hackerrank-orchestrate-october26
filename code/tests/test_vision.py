"""Screen readings stay out of the audit until a resource id and identifier are both present."""

from __future__ import annotations

from datetime import datetime, timezone

from erasecase.contracts import EvidenceFile
from erasecase.vision import observations_from_screen

UTC = timezone.utc


def _entry() -> EvidenceFile:
    return EvidenceFile(
        file_id="evidence_04",
        file_path="evidence/images/account_admin_console_20260926.png",
        origin="account_admin_portal",
        captured_at=datetime(2026, 9, 26, 11, tzinfo=UTC),
    )


def test_screen_without_a_resource_id_is_abstained() -> None:
    assert observations_from_screen(_entry(), {"nothing_identifiable": True, "records": []}) == ()


def test_screen_record_requires_a_patterned_identifier() -> None:
    observations = observations_from_screen(
        _entry(),
        {
            "nothing_identifiable": False,
            "records": [
                {
                    "resource_id": "account_5762",
                    "email": "haruka.s1838@zoho.com",
                    "phone": "+81 90 7610 2507",
                    "user_id": "user_11",
                    "email_hash": "",
                    "posture": "present",
                },
                {
                    "resource_id": "ORD-20265762",
                    "email": "haruka.s1838@zoho.com",
                    "phone": "",
                    "user_id": "",
                    "email_hash": "",
                    "posture": "present",
                },
                {
                    "resource_id": "account_1",
                    "email": "",
                    "phone": "",
                    "user_id": "",
                    "email_hash": "",
                    "posture": "present",
                },
            ],
        },
    )
    assert [item.resource_id for item in observations] == ["account_5762"]
    assert observations[0].facts["email"] == "haruka.s1838@zoho.com"
    assert observations[0].system_id == "account_service"


def test_absent_screen_keeps_the_identifier_as_a_link() -> None:
    observations = observations_from_screen(
        _entry(),
        {
            "nothing_identifiable": False,
            "records": [
                {
                    "resource_id": "account_001",
                    "email": "amina.elmasri@gmail.com",
                    "phone": "",
                    "user_id": "",
                    "email_hash": "",
                    "posture": "absent",
                }
            ],
        },
    )
    assert observations[0].facts["link_email"] == "amina.elmasri@gmail.com"
    assert "email" not in observations[0].facts
    assert observations[0].facts["rows"] == 0
