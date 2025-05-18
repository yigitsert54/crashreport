from django.db import models
from x_custom_decorators import sorted_verbose_name
from accounts.models import WorkshopData
import uuid

# bibs
from datetime import datetime

# null=True means, it is not required
# blank=True is for the form, it means we are allowed to submit a form with this field empty


@sorted_verbose_name(position=3, database_display_name="Unfallszenarien")
class AccidentScenarioOption(models.Model):

    """Hier werden können verschiedene Optionen für den Unfallhergang angelegt werden """

    scenario = models.CharField(max_length=255, unique=True, verbose_name="Unfallhergang")

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.scenario


@sorted_verbose_name(position=1, database_display_name="Unfallberichte")
class DamageReport(models.Model):

    """Hier werden die angelegten Unfallberichte angezeigt."""

    workshop = models.ForeignKey(WorkshopData, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')

    PERSON_CHOICES = [
        ('private', 'Privatperson'),
        ('company', 'Firma'),
    ]

    # --- Erste Seite ---
    person_or_company = models.CharField(max_length=200, null=True, blank=True,
                                         choices=PERSON_CHOICES, verbose_name="Privatperson/Firma")
    company_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Firmenname")
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Vorname")
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Nachname")
    accident_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Unfalldatum & -uhrzeit")
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True, verbose_name="Unterschrift")
    # signatur code: https://claude.ai/chat/8bf64f0a-86cf-4188-abf1-dda27bc9fbff

    # --- Zweite Seite ---
    # Persönliche Daten
    address = models.CharField(max_length=250, null=True, blank=True, verbose_name="Adresse")
    email = models.EmailField(max_length=150, null=True, blank=True, verbose_name="E-Mail")
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telefonnummer")

    # Bankdaten
    iban = models.CharField(max_length=25, null=True, blank=True, verbose_name="IBAN")
    bank_image = models.ImageField(upload_to='bank_info_images/', null=True, blank=True, verbose_name="Foto der Bankkarte")

    # Fahrzeugdaten
    plate_number = models.CharField(max_length=12, null=True, blank=True, verbose_name="Kennzeichen")
    inspection = models.DateField(null=True, blank=True, verbose_name="HU")
    checkbook_exists = models.BooleanField(blank=True, default=False, verbose_name="Scheckheft vorhanden")
    checkbook = models.FileField(upload_to="reports/checkbooks",
                                 null=True, blank=True, help_text="Schekheft Upload")
    leased = models.BooleanField(blank=True, default=False, verbose_name="Geleast")
    financed = models.BooleanField(blank=True, default=False, verbose_name="Finanziert")

    # --- Dritte Seite ---
    # Unfallgegner
    opponent_plate_number = models.CharField(max_length=12, null=True, blank=True, verbose_name="Kennzeichen (Unfallgegner)")
    opponent_insurance_number = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Vers.-Nr. (Unfallgegner)")
    damage_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Schadensnummer")
    has_witnesses = models.BooleanField(blank=True, default=False, verbose_name="Gibt es Zeugen?")
    witness_textfield = models.TextField(null=True, blank=True)

    # Unfallfragebogen
    accident_location = models.CharField(max_length=250, null=True, blank=True, verbose_name="Unfallort")
    accident_scenarios = models.ManyToManyField(
        AccidentScenarioOption, blank=True,
        verbose_name="unfallszenarien (Mehrfachauswahl möglich)",
        related_name="damage_reports"
    )

    accident_notes = models.TextField(null=True, blank=True, verbose_name="Unfallhergang")

    # --- Vierte Seite ---
    # Bilder

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.accident_datetime} - [{self.workshop}]"

    class Meta:
        ordering = ["created", "first_name", "last_name"]

    @property
    def accident_date_string(self):
        if self.accident_datetime:
            return self.accident_datetime.strftime("%d.%m.%Y")
        else:
            return ""

    @property
    def created_string(self):
        if self.created:
            return self.created.strftime("%d.%m.%Y")


@sorted_verbose_name(position=2, database_display_name="Zeugen")  # Position anpassen
class Witness(models.Model):
    """Speichert Daten zu einzelnen Zeugen eines Unfalls."""
    damage_report = models.ForeignKey(DamageReport, on_delete=models.CASCADE,
                                      related_name='witnesses', verbose_name="Zugehöriger Schadensbericht")
    first_name = models.CharField(max_length=100, verbose_name="Vorname")
    last_name = models.CharField(max_length=100, verbose_name="Nachname")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefonnummer")
    # Optional: email = models.EmailField(max_length=150, blank=True, null=True, verbose_name="E-Mail")

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Zeuge für Bericht {self.damage_report})"

    class Meta:
        ordering = ['damage_report', 'created']


@sorted_verbose_name(position=1, database_display_name="Schadensbilder")
class DamageImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('front_left', 'Ansicht vorne links'),
        ('front_right', 'Ansicht vorne rechts'),
        ('rear_left', 'Ansicht hinten links'),
        ('rear_right', 'Ansicht hinten rechts'),
        ('other', 'Sonstiges'),
    ]

    damage_report = models.ForeignKey(DamageReport, on_delete=models.CASCADE,
                                      related_name='images', verbose_name="Schadensbericht")
    image = models.ImageField(upload_to='damage_reports/%Y/%m/%d/', verbose_name="Bild")
    image_view = models.CharField(max_length=30, choices=IMAGE_TYPE_CHOICES, default='other', verbose_name="Bildansicht")

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return f"{self.damage_report} - Ansicht: {self.image_view}"

    class Meta:

        ordering = ['created']
