from django.db import models
from django.contrib.auth.models import User
from x_custom_decorators import sorted_verbose_name
import uuid

# null=True means, it is not required
# blank=True is for the form, it means we are allowed to submit a form with this field empty


@sorted_verbose_name(position=1, database_display_name="Accounts/Werkstätte")
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    # User data
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=300, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):

        if self.first_name:
            firstname = self.first_name
        else:
            firstname = "Vorname"

        if self.last_name:
            lastname = self.last_name
        else:
            lastname = "Nachname"

        return str(f"{firstname} {lastname} - {self.user.email}")

    class Meta:
        ordering = ["first_name", "last_name", "email", "created"]


@sorted_verbose_name(position=2, database_display_name="Werkstatt Daten")
class WorkshopData(models.Model):

    """Hier werden zusätzliche Daten zu den Werkstätten erhoben"""

    account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='workshop')
    workshop_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="Werkstatt Name")

    # Address info
    address = models.CharField(max_length=250, null=True, blank=True, verbose_name="Addresse")
    plz = models.CharField(max_length=7, null=True, blank=True, verbose_name="Postleitzahl")
    city = models.CharField(max_length=250, null=True, blank=True, verbose_name="Stadt")
    country = models.CharField(max_length=250, null=True, blank=True, verbose_name="Land")

    # contact data
    primary_contact = models.CharField(max_length=150, null=True, blank=True, verbose_name="Ansprechpartner",
                                       help_text="Schlüsselfigur für persönliche Kontakte und Anfragen.")
    phone_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Telefonnummer")
    email = models.CharField(max_length=250, null=True, blank=True, verbose_name="E-Mail-Adresse",
                             help_text="E-Mail-Adresse für digitale Kommunikation")

    # legal info
    tax_id = models.CharField(max_length=150, null=True, blank=True, verbose_name="USt-IdNr.")
    verification_document = models.FileField(upload_to="workshops/verification",
                                             null=True, blank=True, help_text="Z.B. Gewerbeschein, um die Echtheit zu prüfen")

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return f"{self.workshop_name} - [{self.account}]"

    class Meta:
        ordering = ["workshop_name"]
