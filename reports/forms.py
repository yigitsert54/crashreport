from django import forms
from django.forms import ModelForm
from .models import DamageReport, DamageImage


class ReportForm(ModelForm):

    class Meta:
        model = DamageReport

        fields = [
            "person_or_company",
            "first_name",
            "last_name",
            "address",
            "email",
            "phone_number",
            "iban",
            "plate_number",
            "inspection",
            "checkbook_exists",
            "checkbook",
            "leased",
            "financed",
            "opponent_plate_number",
            "opponent_insurance_number",
            "damage_number",
            "has_witnesses",
            "accident_datetime",
            "accident_location",
            "accident_notes",
        ]

        labels = {
            "person_or_company": "Privatperson/Firma",
            "first_name": "Vorname",
            "last_name": "Nachname",
            "address": "Adresse",
            "email": "E-Mail-Adresse",
            "phone_number": "Telefonnummer",
            "iban": "IBAN",
            "plate_number": "Kennzeichen",
            "inspection": "HU",
            "checkbook_exists": "Scheckheft vorhanden",
            "checkbook": "Schekheft Upload",
            "leased": "Geleast",
            "financed": "Finanziert",
            "opponent_plate_number": "Kennzeichen (Unfallgegner)",
            "opponent_insurance_number": "Vers.-Nr. (Unfallgegner)",
            "damage_number": "Schadensnummer",
            "has_witnesses": "Gibt es Zeugen?",
            "accident_datetime": "Unfalldatum & -uhrzeit",
            "accident_location": "Unfallort",
            "accident_notes": "Unfallhergang",
        }

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})


# Enthält Felder, die auf der ersten Seite des Formulars erscheinen sollen.
class DamageReportStep1Form(forms.ModelForm):
    signature_base64 = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = DamageReport  # Das Modell, auf dem dieses Formular basiert

        # Liste der Felder aus dem Modell, die in diesem Schritt angezeigt werden
        fields = [
            'person_or_company',
            'company_name',
            'first_name',
            'last_name',
            'accident_datetime',
            # 'signature',
        ]

        labels = {
            "person_or_company": "Privatperson/Firma",
            "company_name": "Firmenname",
            "first_name": "Vorname",
            "last_name": "Nachname",
            "accident_datetime": "Unfalldatum & -uhrzeit",
            # 'signature': 'Unterschrift'
        }

        # Hier kannst du Widgets anpassen, wenn nötig (z.B. für das Datum)
        widgets = {
            'accident_datetime': forms.DateTimeInput(
                attrs={'type': 'text', 'class': 'form-control datepicker accidentDatetime', 'placeholder': 'TT.MM.JJJJ HH:MM'},
                format='%d.%m.%Y %H:%M'  # Optional: Definiert das Format
            ),
        }

    def __init__(self, *args, **kwargs):
        super(DamageReportStep1Form, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})


# Enthält Felder für persönliche Daten, Bankdaten, Versicherung und Fahrzeugdaten.
class DamageReportStep2Form(forms.ModelForm):
    class Meta:
        model = DamageReport

        fields = [
            # Persönliche Daten
            'address',
            'email',
            'phone_number',
            # Bankdaten
            'iban',
            'bank_image',
            # Versicherungsdaten
            # Fahrzeugdaten
            'plate_number',
            'inspection',
            'checkbook_exists',
            'checkbook',
            'leased',
            'financed',
        ]

        labels = {
            "address": "Adresse",
            "email": "E-Mail-Adresse",
            "phone_number": "Telefonnummer",
            "iban": "IBAN",
            "bank_image": "Foto der Bankkarte",
            "plate_number": "Kennzeichen",
            "inspection": "HU",
            "checkbook_exists": "Scheckheft vorhanden",
            "checkbook": "Schekheft Upload",
            "leased": "Geleast",
            "financed": "Finanziert"
        }

        widgets = {
            'inspection': forms.DateInput(
                attrs={'type': 'text', 'class': 'form-control datepicker inspection', 'placeholder': 'MM/JJJJ'},
                format='%m/%Y'
            ),
        }

    def __init__(self, *args, **kwargs):
        super(DamageReportStep2Form, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})


# Enthält Felder für Unfallgegner und Unfallhergang.
class DamageReportStep3Form(forms.ModelForm):
    class Meta:
        model = DamageReport

        fields = [
            # Unfallgegner
            'opponent_plate_number',
            'opponent_insurance_number',
            'damage_number',
            'has_witnesses',
            'witness_textfield',
            # Unfallfragebogen
            'accident_location',
            'accident_scenarios',
            'accident_notes',
        ]

        labels = {
            "opponent_plate_number": "Kennzeichen (Unfallgegner)",
            "opponent_insurance_number": "Vers.-Nr. (Unfallgegner)",
            "damage_number": "Schadensnummer",
            "has_witnesses": "Gibt es Zeugen?",
            "witness_textfield": "Zeugen Textfeld",
            "accident_location": "Unfallort",
            "accident_scenarios": "Zutreffende Unfallszenarien",
            "accident_notes": "Unfallhergang",
        }

        widgets = {
            'accident_scenarios': forms.CheckboxSelectMultiple(
                attrs={'class': 'multiple-checkbox-group'}
            ),
            'accident_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(DamageReportStep3Form, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})

            if name == 'witness_textfield':
                field.widget.attrs.update({"class": "hide"})


class DamageReportStep4ImagesForm(forms.Form):
    # Hole die Choices direkt aus dem Modell, um Konsistenz zu gewährleisten
    IMAGE_VIEW_CHOICES_DICT = dict(DamageImage.IMAGE_TYPE_CHOICES)

    def __init__(self, *args, **kwargs):
        # Extrahiere die Liste der benötigten Ansichten, die von der View übergeben wird
        required_views = kwargs.pop('required_views', [])
        super().__init__(*args, **kwargs)

        # Erstelle dynamisch ImageFields für jede benötigte Ansicht
        for view_key in required_views:
            field_name = f'image_{view_key}'
            # Hole den lesbaren Namen aus den Choices oder verwende den Key
            label = self.IMAGE_VIEW_CHOICES_DICT.get(view_key, view_key.replace('_', ' ').title())

            self.fields[field_name] = forms.ImageField(
                label=label,
                required=False,  # Mache Felder optional, da der User vielleicht nicht alle Bilder hat
                widget=forms.ClearableFileInput(attrs={
                    'multiple': False,  # Erlaube nur eine Datei pro Feld
                    'accept': 'image/*',  # Beschränke auf Bilddateien
                    'class': 'form-control-file'  # Optional: CSS-Klasse für Styling
                })
            )


class DamageReportConfirmationForm(forms.Form):
    # Absichtlich leer gelassen
    pass


class ReportForm_Step1(ModelForm):

    class Meta:
        model = DamageReport

        # Liste der Felder aus dem Modell, die in diesem Schritt angezeigt werden
        fields = [
            'person_or_company',
            'company_name',
            'first_name',
            'last_name',
            'accident_datetime',
            # 'signature',
        ]

        labels = {
            "person_or_company": "Privatperson/Firma",
            "company_name": "Firmenname",
            "first_name": "Vorname",
            "last_name": "Nachname",
            "accident_datetime": "Unfalldatum & -uhrzeit",
            # 'signature': 'Unterschrift'
        }

    def __init__(self, *args, **kwargs):
        super(ReportForm_Step1, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})
            field.widget.attrs.update({"class": "form-control"})

            if name == "person_or_company":
                field.widget.attrs.update({"class": "selectpicker w-auto"})

            if name == "accident_datetime":
                field.widget.attrs.update({"id": "flatpickr-datetime"})


class ReportForm_Step2(ModelForm):

    class Meta:
        model = DamageReport

        fields = [
            # Persönliche Daten
            'address',
            'email',
            'phone_number',
            # Bankdaten
            'iban',
            'bank_image',
            # Versicherungsdaten
            # Fahrzeugdaten
            'plate_number',
            'inspection',
            'checkbook_exists',
            'checkbook',
            'leased',
            'financed',
        ]

        labels = {
            "address": "Adresse",
            "email": "E-Mail-Adresse",
            "phone_number": "Telefonnummer",
            "iban": "IBAN",
            "bank_image": "Foto der Bankkarte",
            "plate_number": "Kennzeichen",
            "inspection": "HU",
            "checkbook_exists": "Scheckheft vorhanden",
            "checkbook": "Schekheft Upload",
            "leased": "Geleast",
            "financed": "Finanziert"
        }

    def __init__(self, *args, **kwargs):
        super(ReportForm_Step2, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})
            field.widget.attrs.update({"class": "form-control"})

            if isinstance(field.widget, forms.CheckboxInput):
                # CSS-Klasse für Checkboxen setzen (überschreibt 'form-control')
                field.widget.attrs.update({"class": "form-check-input"})


class ReportForm_Step3(ModelForm):

    class Meta:
        model = DamageReport

        fields = [
            # Unfallgegner
            'opponent_plate_number',
            'opponent_insurance_number',
            'damage_number',
            'accident_location',
            # Unfallfragebogen
            'accident_notes',
            'accident_scenarios',
            'has_witnesses',
            'witness_textfield',

        ]

        labels = {
            "opponent_plate_number": "Kennzeichen (Unfallgegner)",
            "opponent_insurance_number": "Vers.-Nr. (Unfallgegner)",
            "damage_number": "Schadensnummer",
            "has_witnesses": "Gibt es Zeugen?",
            "witness_textfield": "Zeugen Textfeld",
            "accident_location": "Unfallort",
            "accident_scenarios": "Zutreffende Unfallszenarien",
            "accident_notes": "Unfallhergang",
        }

        widgets = {
            'accident_scenarios': forms.CheckboxSelectMultiple(
                attrs={'class': 'multiple-checkbox-group'}
            ),
            'accident_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(ReportForm_Step3, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": field.label})
            field.widget.attrs.update({"class": "form-control"})

            if isinstance(field.widget, forms.CheckboxInput):
                # CSS-Klasse für Checkboxen setzen (überschreibt 'form-control')
                field.widget.attrs.update({"class": "form-check-input"})

            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                # CSS-Klasse für Checkboxen setzen (überschreibt 'form-control')
                field.widget.attrs.update({"class": "form-check-input"})
