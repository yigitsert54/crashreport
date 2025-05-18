from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from .models import Account, WorkshopData
from django.utils.html import format_html


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            "placeholder": "Benutzername",
            "class": "formInput",
            "required": "required",
        }),
        label="Benutzername"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Passwort",
            "class": "formInput",
            "required": "required",
        }),
        label="Passwort"
    )


class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]

        labels = {
            "first_name": "Vorname",
            "last_name": "Nachname",
            "email": "E-Mail"
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})
            field.widget.attrs.update({"class": "form-control"})
            field.widget.attrs.update({"required": "required"})

            if name == "password1":
                field.widget.attrs.update({"placeholder": "Passwort"})
                field.label = "Passwort"
            if name == "password2":
                field.widget.attrs.update({"placeholder": "Passwort bestätigen"})
                field.label = "Passwort bestätigen"


class AccountForm(ModelForm):

    class Meta:
        model = Account

        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Vorname",
            "last_name": "Nachname",
            "email": "E-Mail-Adresse"
        }

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})
            field.widget.attrs.update({"class": "form-control"})

            # Set icons
            if name == "first_name":
                field.widget.attrs.update({"icon": "user"})
            elif name == "last_name":
                field.widget.attrs.update({"icon": "user"})
            elif name == "email":
                field.widget.attrs.update({"icon": "envelope"})


class WorkshopForm(ModelForm):

    class Meta:
        model = WorkshopData

        fields = [
            "workshop_name",
            "address",
            "plz",
            "city",
            "country",
            "primary_contact",
            "phone_number",
            "email",
            "tax_id",
            "verification_document",
        ]
        labels = {
            "workshop_name": "Werkstatt Name",
            "address": "Adresse",
            "plz": "Postleitzahl",
            "city": "Stadt",
            "country": "Land",
            "primary_contact": "Primärer Ansprechpartner",
            "phone_number": "Telefonnummer",
            "email": "Kontakt-E-Mail",
            "tax_id": "USt-IdNr.",
            "verification_document": "Nachweisdokument",
        }

        widgets = {
            "verification_document": forms.FileInput(attrs={
                "placeholder": "Nachweisdokument",
            }),
        }

    def __init__(self, *args, **kwargs):
        super(WorkshopForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})
            field.widget.attrs.update({"class": "form-control"})

            if name == "email":
                field.widget.attrs.update({"id": "id_workshopEmail"})
                # Überschreibe das Label mit einem benutzerdefinierten `for`-Attribut
                field.label = format_html(
                    '<label for="{}">{}</label>',
                    "id_workshopEmail",
                    field.label
                )
