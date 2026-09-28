import io
from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.models import Employee
from accounts.services import AccountDraft, create_account
from achievements.evidence import validate_proof_url
from achievements.models import Achievement, AchievementCategory, Evidence
from achievements.services import (
    AchievementDraft as Draft,
    count_approved,
    decide_achievement,
    submit_achievement,
    void_achievement,
)
from django.core.exceptions import ValidationError

User = get_user_model()


def _png_bytes(color=(20, 40, 60)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(buf, format="PNG")
    return buf.getvalue()


@override_settings(
    ROOT_URLCONF="config.urls",
    PRIVATE_MEDIA_ROOT=None,  # set in setUp
)
class AchievementWorkflowTests(TestCase):
    def setUp(self):
        self._media = Path(self._get_temp_dir()) if hasattr(self, "_get_temp_dir") else None
        from django.conf import settings
        import tempfile

        self._tmpdir = tempfile.mkdtemp()
        settings.PRIVATE_MEDIA_ROOT = self._tmpdir

        AchievementCategory.objects.get_or_create(
            code="video_published", defaults={"label": "Vidéo publiée"}
        )
        AchievementCategory.objects.get_or_create(
            code="positive_review", defaults={"label": "Avis client positif"}
        )
        self.cat_video = AchievementCategory.objects.get(code="video_published")

        self.manager = create_account(
            None,
            AccountDraft(
                username="mgr_a",
                password="pass-mgr-a",
                display_name="Gérant A",
                is_manager=True,
            ),
        )
        self.manager_b = create_account(
            self.manager,
            AccountDraft(
                username="mgr_b",
                password="pass-mgr-b",
                display_name="Gérant B",
                is_manager=True,
            ),
        )
        self.employee_user = create_account(
            self.manager,
            AccountDraft(
                username="emp_a",
                password="pass-emp-a",
                display_name="Employé A",
                is_manager=False,
            ),
        )
        self.employee = self.employee_user.employee_profile
        self.employee_b_user = create_account(
            self.manager,
            AccountDraft(
                username="emp_b",
                password="pass-emp-b",
                display_name="Employé B",
                is_manager=False,
            ),
        )
        self.employee_b = self.employee_b_user.employee_profile
        self.client = Client()

    def test_ac02_count_by_occurrence_not_approval_date(self):
        ach = submit_achievement(
            actor=self.employee_user,
            draft=Draft(
                employee=self.employee,
                category=self.cat_video,
                occurred_on=date(2026, 9, 10),
                proof_urls=["https://example.com/video"],
                idempotency_token="tok-ac02",
            ),
        )
        self.assertEqual(ach.state, Achievement.State.PENDING)
        self.assertEqual(count_approved(employee=self.employee, date_from=date(2026, 9, 1), date_to=date(2026, 9, 30)), {})

        decide_achievement(
            actor=self.manager,
            achievement=ach,
            approve=True,
            expected_revision=1,
            note="",
        )
        sept = count_approved(
            employee=self.employee, date_from=date(2026, 9, 1), date_to=date(2026, 9, 30)
        )
        octo = count_approved(
            employee=self.employee, date_from=date(2026, 10, 1), date_to=date(2026, 10, 31)
        )
        self.assertEqual(sept.get("video_published"), 1)
        self.assertEqual(octo.get("video_published"), None)

    def test_ac03_manager_on_behalf_approved_idempotent_void(self):
        draft = Draft(
            employee=self.employee_b,
            category=self.cat_video,
            occurred_on=date(2026, 9, 12),
            proof_urls=["https://example.com/shared"],
            idempotency_token="tok-ac03",
        )
        first = submit_achievement(actor=self.manager, draft=draft)
        second = submit_achievement(actor=self.manager, draft=draft)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.state, Achievement.State.APPROVED)
        self.assertEqual(first.created_by_id, self.manager.pk)
        self.assertEqual(first.employee_id, self.employee_b.pk)
        self.assertEqual(
            count_approved(employee=self.employee_b, date_from=None, date_to=None).get("video_published"),
            1,
        )

        void_achievement(
            actor=self.manager,
            achievement=first,
            expected_revision=first.revision,
            reason="Erreur de bénéficiaire",
        )
        first.refresh_from_db()
        self.assertEqual(first.state, Achievement.State.VOIDED)
        self.assertEqual(
            count_approved(employee=self.employee_b, date_from=None, date_to=None),
            {},
        )

        # Manager self-submission stays pending
        manager_emp = self.manager.employee_profile
        self_sub = submit_achievement(
            actor=self.manager,
            draft=Draft(
                employee=manager_emp,
                category=self.cat_video,
                occurred_on=date(2026, 9, 13),
                proof_urls=["https://example.com/self"],
                idempotency_token="tok-self",
            ),
        )
        self.assertEqual(self_sub.state, Achievement.State.PENDING)

    def test_ac11_reject_bad_url_and_unauthorized_evidence(self):
        with self.assertRaises(ValidationError):
            validate_proof_url("javascript:alert(1)")

        upload = SimpleUploadedFile("proof.png", _png_bytes(), content_type="image/png")
        ach = submit_achievement(
            actor=self.employee_user,
            draft=Draft(
                employee=self.employee,
                category=self.cat_video,
                occurred_on=date(2026, 9, 10),
                image_uploads=[upload],
                idempotency_token="tok-img",
            ),
        )
        evidence = Evidence.objects.get(achievement=ach, kind=Evidence.Kind.IMAGE)

        # Employee B cannot fetch A's evidence
        self.client.login(username="emp_b", password="pass-emp-b")
        denied = self.client.get(reverse("evidence", args=[evidence.pk]))
        self.assertEqual(denied.status_code, 404)

        # Beneficiary can
        self.client.login(username="emp_a", password="pass-emp-a")
        ok = self.client.get(reverse("evidence", args=[evidence.pk]))
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok["Cache-Control"], "private, no-store")

        # SVG / HTML disguised as image should fail
        bad = SimpleUploadedFile("x.png", b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", content_type="image/png")
        with self.assertRaises(ValidationError):
            submit_achievement(
                actor=self.employee_user,
                draft=Draft(
                    employee=self.employee,
                    category=self.cat_video,
                    occurred_on=date(2026, 9, 11),
                    image_uploads=[bad],
                    idempotency_token="tok-bad",
                ),
            )

    def test_employee_cannot_approve(self):
        ach = submit_achievement(
            actor=self.employee_user,
            draft=Draft(
                employee=self.employee,
                category=self.cat_video,
                occurred_on=date(2026, 9, 10),
                proof_urls=["https://example.com/v"],
                idempotency_token="tok-deny",
            ),
        )
        self.client.login(username="emp_a", password="pass-emp-a")
        response = self.client.post(
            reverse("achievements:approve", args=[ach.pk]),
            {"expected_revision": ach.revision, "note": ""},
        )
        self.assertEqual(response.status_code, 403)
