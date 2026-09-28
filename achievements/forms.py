import uuid

from django import forms

from accounts.models import Employee
from achievements.models import AchievementCategory


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            result = [single(item, initial) for item in data]
            return [item for item in result if item]
        cleaned = single(data, initial)
        return [cleaned] if cleaned else []


class AchievementSubmitForm(forms.Form):
    category = forms.ModelChoiceField(
        label="Catégorie",
        queryset=AchievementCategory.objects.filter(is_active=True),
    )
    occurred_on = forms.DateField(
        label="Date du succès",
        widget=forms.DateInput(attrs={"type": "date", "class": "input input-bordered w-full"}),
    )
    proof_url = forms.CharField(
        label="Lien de preuve",
        required=False,
        widget=forms.URLInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "https://…"}
        ),
    )
    proof_url_2 = forms.CharField(
        label="Lien supplémentaire",
        required=False,
        widget=forms.URLInput(attrs={"class": "input input-bordered w-full"}),
    )
    images = MultipleFileField(
        label="Images (JPEG, PNG, WebP)",
        required=False,
        widget=MultipleFileInput(
            attrs={
                "class": "file-input file-input-bordered w-full",
                "accept": "image/jpeg,image/png,image/webp",
            }
        ),
    )
    beneficiary = forms.ModelChoiceField(
        label="Bénéficiaire",
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        help_text="Réservé aux gérants pour enregistrer au nom d’un collègue.",
    )
    idempotency_token = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["category"].widget.attrs.setdefault("class", "select select-bordered w-full")
        if not self.initial.get("idempotency_token"):
            self.fields["idempotency_token"].initial = str(uuid.uuid4())
        if user is None or not getattr(user, "is_manager", False):
            self.fields["beneficiary"].widget = forms.HiddenInput()
            self.fields["beneficiary"].required = False
        else:
            self.fields["beneficiary"].widget.attrs.setdefault(
                "class", "select select-bordered w-full"
            )


class ReviewForm(forms.Form):
    expected_revision = forms.IntegerField(widget=forms.HiddenInput())
    note = forms.CharField(
        label="Commentaire",
        required=False,
        widget=forms.Textarea(
            attrs={"class": "textarea textarea-bordered w-full", "rows": 3}
        ),
    )


class RejectForm(ReviewForm):
    note = forms.CharField(
        label="Motif du refus",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "textarea textarea-bordered w-full", "rows": 3}
        ),
    )


class ReasonForm(forms.Form):
    expected_revision = forms.IntegerField(widget=forms.HiddenInput())
    reason = forms.CharField(
        label="Motif",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "textarea textarea-bordered w-full", "rows": 3}
        ),
    )


class CorrectForm(forms.Form):
    expected_revision = forms.IntegerField(widget=forms.HiddenInput())
    reason = forms.CharField(
        label="Motif de correction",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "textarea textarea-bordered w-full", "rows": 3}
        ),
    )
    category = forms.ModelChoiceField(
        label="Catégorie",
        queryset=AchievementCategory.objects.filter(is_active=True),
        required=False,
    )
    occurred_on = forms.DateField(
        label="Date du succès",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "input input-bordered w-full"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].widget.attrs.setdefault("class", "select select-bordered w-full")
