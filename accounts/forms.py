from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class FrenchAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Identifiant ou mot de passe incorrect.",
        "inactive": "Ce compte est inactif.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Identifiant"
        self.fields["password"].label = "Mot de passe"
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input input-bordered w-full")

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not getattr(user, "is_salon_active", True):
            raise forms.ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

class UserCreateForm(forms.Form):
    username = forms.CharField(label="Identifiant", max_length=150)
    display_name = forms.CharField(label="Nom affiché", max_length=150, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmation", widget=forms.PasswordInput)
    is_manager = forms.BooleanField(label="Gérant", required=False)
    is_salon_active = forms.BooleanField(label="Compte actif", required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "checkbox")
            else:
                field.widget.attrs.setdefault("class", "input input-bordered w-full")

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        return cleaned


class UserUpdateForm(forms.Form):
    display_name = forms.CharField(label="Nom affiché", max_length=150)
    email = forms.EmailField(label="E-mail", required=False)
    is_manager = forms.BooleanField(label="Gérant", required=False)
    is_salon_active = forms.BooleanField(label="Compte actif", required=False)
    new_password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput,
        required=False,
        help_text="Laisser vide pour ne pas changer.",
    )

    def __init__(self, *args, user: User | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "checkbox")
            else:
                field.widget.attrs.setdefault("class", "input input-bordered w-full")
