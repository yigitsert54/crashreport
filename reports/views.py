from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import base64
import uuid
from django.core.files.base import ContentFile
import logging
import pprint

# models
from accounts.models import Account, WorkshopData
from .models import DamageReport, DamageImage

# forms
from .forms import (
    ReportForm,
    DamageReportStep1Form,
    DamageReportStep2Form,
    DamageReportStep3Form,
    DamageReportStep4ImagesForm,
    DamageReportConfirmationForm,
    ReportForm_Step1,
    ReportForm_Step2,
    ReportForm_Step3,
)

# Import the WizardView.
from formtools.wizard.views import SessionWizardView  # SessionWizardView saves data between the steps in the session.

# Own functions and methods
from x_global_utils import custom_messages, email_is_valid, phone_number_valid


logger = logging.getLogger(__name__)

DAMAGE_REPORT_FORMS = [
    ("step1", DamageReportStep1Form),
    ("step2", DamageReportStep2Form),
    ("step3", DamageReportStep3Form),
    ("step4_images", DamageReportStep4ImagesForm),
    ("confirm", DamageReportConfirmationForm)
    # ("step4", DamageReportStep4Form), # Einkommentieren, wenn Schritt 4 existiert
]


STEP_TITLES = {
    "step1": "Basisdaten",
    "step2": "Details",
    "step3": "Unfallhergang",
    "step4_images": "Bilder",
    "confirm": "Prüfen & Senden",
}


@method_decorator(login_required(login_url='login'), name='dispatch')
class DamageReportWizardView(SessionWizardView):
    # List of forms that will be used by the wizard.
    form_list = DAMAGE_REPORT_FORMS

    # Default template used if a specific template for a step is not provided.
    template_name = 'reports/damage_report_wizard.html'

    # Dictionary mapping each wizard step to its respective template.
    TEMPLATES = {
        "step1": "reports/damage_report_wizard.html",
        "step2": "reports/damage_report_wizard.html",
        "step3": "reports/damage_report_wizard.html",
        "step4_images": "reports/damage_report_wizard.html",
        "confirm": "reports/damage_report_confirmation.html"
    }

    # File storage object to handle file uploads during the wizard process.
    file_storage = default_storage

    IMAGE_VIEW_CHOICES_DICT = dict(DamageImage.IMAGE_TYPE_CHOICES)

    REQUIRED_IMAGE_VIEWS = [
        'front_left',
        'front_right',
        'rear_left',
        'rear_right',
        # 'dashboard', # Beispiel: Wenn du diese Ansicht hinzufügen würdest
        'other',
    ]

    # kwargs an die Bild-Form übergeben
    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step == 'step4_images':
            # Übergib die Liste der benötigten Views an die Form __init__
            kwargs['required_views'] = self.REQUIRED_IMAGE_VIEWS
        return kwargs

    # Method for selecting the appropriate template based on the current wizard step.
    def get_template_names(self):
        # Check if the TEMPLATES attribute is defined; this holds custom templates for each step.
        if hasattr(self, 'TEMPLATES'):
            # Return the template corresponding to the current step wrapped in a list.
            return [self.TEMPLATES[self.steps.current]]
        elif hasattr(self, 'template_name'):
            # Log a warning that TEMPLATES is missing and the system is using the default template.
            logger.warning("TEMPLATES dictionary not defined on WizardView, falling back to template_name.")
            return [self.template_name]
        else:
            # Neither TEMPLATES nor template_name is defined; log an error and raise an exception to signal misconfiguration.
            logger.error("Neither TEMPLATES nor template_name defined on WizardView.")
            raise ImproperlyConfigured("WizardView requires either a definition for 'template_name' or 'TEMPLATES'.")

    # Method to build context data for rendering the wizard's templates, including assembling step information.
    def get_context_data(self, form, **kwargs):
        # Retrieve the default context data from the parent class.
        context = super().get_context_data(form=form, **kwargs)

        # Initialize an empty set to keep track of steps that the user is allowed to access.
        accessible_steps = set()
        current_index = -1  # Initialize current index safely.

        try:
            # Retrieve a list of all step names (e.g., ['step1', 'step2', 'step3', 'confirm']).
            all_step_names = self.steps.all

            # Determine the index of the current step.
            current_index = all_step_names.index(self.steps.current)
        except ValueError:
            # Log a warning if the current step is not found in the list of all steps.
            logger.warning(f"Current step '{self.steps.current}' not found in declared steps: {all_step_names}")

            # Default to index 0 in case of an error, assuming the first step.
            current_index = 0

        # Loop through each step index and add steps up to and including the current one to the accessible set.
        for i, step_name in enumerate(all_step_names):
            # Alle Schritte bis einschließlich des aktuell höchsten erreichten sind zugänglich
            # Wir nehmen hier an, der höchste erreichte ist der aktuelle Index
            if i <= current_index:
                accessible_steps.add(step_name)

        # Build an ordered list of dictionaries, each containing detailed information about each step.
        steps_info = []

        for i, step_name in enumerate(all_step_names):
            steps_info.append({
                'name': step_name,  # Unique identifier for the step.
                # Set a title based on predefined dictionary (STEP_TITLES) or generate a title from the step name.
                'title': STEP_TITLES.get(step_name, step_name.replace('_', ' ').title()),
                'number': i + 1,  # Step number for display purposes (1-indexed).
                'is_current': step_name == self.steps.current,  # Boolean indicating if this is the current step.
                'is_accessible': step_name in accessible_steps  # Boolean indicating if the user can navigate to this step.
            })

        # Update the context with the constructed steps information for use in the templates.
        context['steps_info'] = steps_info  # Ersetzt 'all_steps' und 'step_titles'

        # If the current step is the confirmation step, gather all previously entered data.
        if self.steps.current == 'confirm':
            all_cleaned_data = {}
            signature_base64_for_preview = None  # Für die Vorschau
            uploaded_image_info = {}
            try:

                # Retrieve the list of all forms used in the wizard flow.
                step_list_to_check = self.get_form_list()  # ['step1', 'step2', 'step3', 'confirm']

                # Iterate through each step to aggregate the cleaned form data.
                for step in step_list_to_check:
                    # Skip the confirmation step since its data is not meant for aggregation.
                    if step == 'confirm':
                        continue

                    # Safely check if the step exists in the stored wizard data.
                    step_exists_in_storage = step in self.storage.data.get('step_data', {})

                    if step_exists_in_storage:
                        # Retrieve the cleaned data for the current step.
                        step_data = self.get_cleaned_data_for_step(step)

                        if step_data:

                            if step == 'step1' and 'signature_base64' in step_data:
                                signature_base64_for_preview = step_data.get('signature_base64')

                            if step == 'step4_images':
                                temp_data_for_display = step_data.copy()
                                for view_key in self.REQUIRED_IMAGE_VIEWS:
                                    field_name = f'image_{view_key}'
                                    uploaded_file = step_data.get(field_name)
                                    if uploaded_file:
                                        view_label = self.IMAGE_VIEW_CHOICES_DICT.get(
                                            view_key, view_key.replace('_', ' ').title())
                                        uploaded_image_info[view_key] = {
                                            'name': uploaded_file.name,
                                            'size': uploaded_file.size,
                                            'label': view_label  # Füge den lesbaren Namen hinzu
                                        }

                                    temp_data_for_display.pop(f'image_{view_key}', None)

                                all_cleaned_data.update(temp_data_for_display)

                            # Add the current step's data to the aggregate dictionary.
                            all_cleaned_data.update(step_data)

                        else:
                            # Log a warning if no data was returned despite the step being in storage.
                            logger.warning(f"get_cleaned_data_for_step('{step}') returned None or an empty dictionary.")
                    else:
                        # Warn if there is no stored data for this step.
                        logger.warning(f"No data found in storage for step '{step}'.")

                # Debug log the final aggregated data before adding it to the template context.
                logger.debug("Final aggregated data for 'all_form_data':\n%s", pprint.pformat(all_cleaned_data))

                context['signature_base64_preview'] = signature_base64_for_preview

                # Add the aggregated cleaned data to the context.
                context['all_form_data'] = all_cleaned_data

                context['uploaded_image_info'] = uploaded_image_info

            except Exception as e:
                # Log the exception with the stack trace if data aggregation fails.
                logger.exception("Error encountered while collecting data for the confirmation page!")

        # Return the full context that will be passed to the template.
        return context

    # This method is called after the final form has been validated successfully.
    # It processes the accumulated data and saves the DamageReport object.
    def done(self, form_list, **kwargs):

        # Combine cleaned data from all steps of the wizard.
        all_cleaned_data = self.get_all_cleaned_data()

        # Extrahiere Base64-Daten und entferne sie aus dem Haupt-Dictionary
        signature_base64_data = all_cleaned_data.pop('signature_base64', None)

        # Initialisiere die Datei-Variable
        signature_file = None

        # Extract many-to-many data (accident scenarios) before it is removed from the data dictionary.
        scenarios_data = all_cleaned_data.pop('accident_scenarios', None)

        image_upload_data = {}
        for view_key in self.REQUIRED_IMAGE_VIEWS:
            field_name = f'image_{view_key}'
            uploaded_file = all_cleaned_data.pop(field_name, None)  # Entferne Bilddaten
            if uploaded_file:
                image_upload_data[view_key] = uploaded_file

        # Retrieve the user's account and associated workshop information.
        account: Account = getattr(self.request.user, 'account', None)
        workshop: WorkshopData = getattr(account, 'workshop', None)

        if not workshop:
            # Notify the user that saving cannot proceed due to missing workshop information.
            custom_messages(self.request, "error", "Keine Werkstatt zugeordnet. Speichern nicht möglich.")

            # Redirect the user to the reports home page
            return redirect("reports_home")

        # Add the workshop data into the cleaned data to associate the report with the workshop.
        all_cleaned_data['workshop'] = workshop

        # ---  Verarbeitung der Base64-Signatur ---
        if signature_base64_data and isinstance(signature_base64_data, str) and signature_base64_data.startswith('data:image/png;base64,'):
            try:
                # Extrahiere Header und Base64-Teil
                format, imgstr = signature_base64_data.split(';base64,')
                # Dekodiere Base64-String zu Bytes
                image_data = base64.b64decode(imgstr)
                # Erstelle einen eindeutigen Dateinamen
                file_name = f'signature_{uuid.uuid4()}.png'
                # Erstelle ein Django ContentFile Objekt (quasi eine In-Memory-Datei)
                signature_file = ContentFile(image_data, name=file_name)
                logger.info(f"Signatur erfolgreich dekodiert und als '{file_name}' vorbereitet.")
            except (ValueError, TypeError, base64.binascii.Error) as e:
                logger.error(f"Fehler beim Dekodieren der Base64-Signatur: {e}")
                custom_messages(self.request, "error", "Die Unterschrift konnte nicht verarbeitet werden.")
                # Gehe zurück zum Formular oder zeige Fehler an
                # Hier wird angenommen, dass der aktuelle Schritt der letzte ist (confirm)
                # Wir versuchen, das letzte Formular erneut zu rendern
                return self.render_revalidation_failure(self.steps.current, form_list[-1], **kwargs)
        elif signature_base64_data:
            # Logge, wenn Daten vorhanden, aber im falschen Format sind
            logger.warning(f"Ungültiges Format für signature_base64_data empfangen: {signature_base64_data[:50]}...")
        # --- Ende Signatur-Verarbeitung ---

        try:
            # Begin a database transaction to ensure that all operations are completed atomically.
            with transaction.atomic():
                print("\n###########################")
                print(all_cleaned_data)
                print("###########################\n")

                # Create a new DamageReport instance using the combined cleaned data.
                report = DamageReport(**all_cleaned_data)

                # Weise die erstellte Datei dem ImageField zu, *falls* sie existiert
                if signature_file:
                    report.signature = signature_file

                # Save the main DamageReport object to the database.
                report.save()

                images_created_count = 0
                for view_key, uploaded_file in image_upload_data.items():
                    try:
                        DamageImage.objects.create(
                            damage_report=report,  # Verknüpfung mit dem gespeicherten Report
                            image=uploaded_file,  # Das hochgeladene File-Objekt
                            image_view=view_key   # Der Key der Ansicht
                        )
                        images_created_count += 1
                    except Exception as img_e:
                        # Logge Fehler beim Speichern einzelner Bilder, aber fahre fort
                        logger.error(
                            f"Fehler beim Speichern von Bild '{uploaded_file.name}' für Ansicht '{view_key}' bei Report {report.id}: {img_e}")

                # If accident scenarios data exists, set up the many-to-many relationship after saving the report.
                if scenarios_data is not None:
                    report.accident_scenarios.set(scenarios_data)

            # Build the URL for redirecting the user to the edit form for the newly created report.
            success_url = reverse_lazy("edit_report_form", kwargs={'report_id': report.id})

            # display a success message including the report owner's first and last names.
            custom_messages(self.request, "success",
                            f"Schadensbericht für {report.first_name} {report.last_name} erfolgreich angelegt.")

            # Redirect to the report edit page.
            return HttpResponseRedirect(success_url)

        except Exception as e:
            # Log the exception with full details if any error occurs during the transaction.
            logger.exception("Error saving DamageReport within the transaction: %s", e)

            # Notify the user about the error and prompt them to try again.
            custom_messages(self.request, "error", "Fehler beim Speichern des Berichts. Bitte versuchen Sie es erneut.")

            return self.render_revalidation_failure(self.steps.current, self.get_form(), **kwargs)


def reports_home(request):
    # Extract account
    account: Account = request.user.account

    # Extract workshop
    workshop: WorkshopData = account.workshop

    # Extract all reports
    reports: DamageReport = workshop.reports.all()

    context = {
        "reports": reports
    }

    return render(request, 'reports/reports_home.html', context=context)


def create_report_initial(request):
    # Extract account
    account: Account = request.user.account

    # Extract workshop
    workshop: WorkshopData = account.workshop

    # report form
    report_form = ReportForm()

    report_form_step_1 = ReportForm_Step1()
    report_form_step_2 = ReportForm_Step2()
    report_form_step_3 = ReportForm_Step3()

    # Handle POST request
    if request.method == "POST":

        # Get form
        report_form = ReportForm(request.POST)

        # Check if form is valid
        if report_form.is_valid():

            # Save form data without commiting
            report = report_form.save(commit=False)

            # Extract POST data
            new_email = request.POST["email"].lower()
            new_first_name = request.POST["first_name"].capitalize()
            new_last_name = request.POST["last_name"].capitalize()

            # Check if names are valid
            if len(new_first_name) <= 2 or len(new_last_name) <= 2:

                # Error message
                custom_messages(request, message_type="error", message_text="Vor- oder Nachname ungültig!")

                context = {
                    "form": report_form
                }

                return render(request, 'reports/create_report.html', context=context)

            # Validate Email
            if not email_is_valid(new_email):

                custom_messages(request, message_type="error", message_text="Bitte eine gültige E-Mail eingeben!")

                context = {
                    "form": report_form
                }

                return render(request, 'reports/create_report.html', context=context)

            # Extract phone number
            new_phone_number = request.POST["phone_number"].lower().replace("-", "").replace("/", "").replace(" ", "")

            # Validate phone number
            if not phone_number_valid(new_phone_number):
                # Error message
                custom_messages(request, message_type="error", message_text="Bitte eine gültige Telefonnummer eingeben!")

                context = {
                    "form": report_form
                }

                return render(request, 'reports/create_report.html', context=context)

            report.workshop = workshop
            report.email = new_email
            report.first_name = new_first_name
            report.last_name = new_last_name
            report.phone_number = new_phone_number

            custom_messages(request, message_type="success", message_text="Geändert!")

            context = {
                "form": report_form
            }

            report.save()

            return redirect("edit_report_form", report_id=report.id)

    context = {
        "form": report_form,
        "report_form_step_1": report_form_step_1,
        "report_form_step_2": report_form_step_2,
        "report_form_step_3": report_form_step_3,

    }

    return render(request, 'reports/create_report.html', context=context)


def edit_report_form(request, report_id):

    # Extract damage report
    report = DamageReport.objects.get(id=report_id)

    # report form
    report_form = ReportForm(instance=report)

    # Handle POST request
    if request.method == "POST":

        # Get form
        report_form = ReportForm(request.POST, instance=report)

        # Check if form is valid
        if report_form.is_valid():

            # Save form data without commiting
            report = report_form.save(commit=False)

            # Extract POST data
            new_email = request.POST["email"].lower()
            new_first_name = request.POST["first_name"].capitalize()
            new_last_name = request.POST["last_name"].capitalize()

            # Check if names are valid
            if len(new_first_name) <= 2 or len(new_last_name) <= 2:

                # Error message
                custom_messages(request, message_type="error", message_text="Vor- oder Nachname ungültig!")

                context = {
                    "form": report_form
                }

                return render(request, 'reports/create_report.html', context=context)

            # Validate Email
            if not email_is_valid(new_email):

                custom_messages(request, message_type="error", message_text="Bitte eine gültige E-Mail eingeben!")

                context = {
                    "form": report_form
                }

                return render(request, 'reports/create_report.html', context=context)

            # Extract phone number
            new_phone_number = request.POST["phone_number"].lower().replace("-", "").replace("/", "").replace(" ", "")

            # Validate phone number
            if not phone_number_valid(new_phone_number):
                # Error message
                custom_messages(request, message_type="error", message_text="Bitte eine gültige Telefonnummer eingeben!")

                context = {
                    "form": report_form
                }

                return render(request, 'reports/create_report.html', context=context)

            report.email = new_email
            report.first_name = new_first_name
            report.last_name = new_last_name
            report.phone_number = new_phone_number

            custom_messages(request, message_type="success", message_text="Geändert!")
            report.save()

    context = {
        "form": report_form,
        "report": report,
        "purpose": "edit"
    }

    return render(request, 'reports/create_report.html', context=context)
