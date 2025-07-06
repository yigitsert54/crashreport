from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.contrib.auth.decorators import login_required

# models
from accounts.models import Account, WorkshopData
from .models import DamageReport, DamageImage, Witness

# forms
from .forms import (
    ReportForm,
    DamageReportStep4ImagesForm,
    ReportForm_Step1,
    ReportForm_Step2,
    ReportForm_Step3,
    ReportForm_Step4
)

# import utils
from .utils import (
    AutoixpertAPIHandler,
    process_report_step_1,
    process_report_step_2,
    process_report_step_3,
    process_report_step_4,
    process_editing_step_1,
    process_editing_step_4
)  # SessionWizardView saves data between the steps in the session.

# Own functions and methods
from x_global_utils import custom_messages, email_is_valid, phone_number_valid

import base64
from datetime import datetime
from django.core.files.base import ContentFile
from django.utils import timezone
import json


@login_required(login_url="login")
def reports_home(request):

    api_handler = AutoixpertAPIHandler()
    report = api_handler.get_reports()["reports"][-1]
    print("\n", json.dumps(report, indent=4, ensure_ascii=False))

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


@login_required(login_url="login")
def create_report_initial(request):
    # Extract account
    account: Account = request.user.account

    # Extract workshop
    workshop: WorkshopData = account.workshop

    report_form_step_1 = ReportForm_Step1()
    report_form_step_2 = ReportForm_Step2()
    report_form_step_3 = ReportForm_Step3()
    report_form_step_4 = ReportForm_Step4()

    # Handle POST request
    if request.method == "POST":

        report_form_step_1 = ReportForm_Step1(request.POST, request.FILES)
        report_form_step_2 = ReportForm_Step2(request.POST, request.FILES)
        report_form_step_3 = ReportForm_Step3(request.POST, request.FILES)
        report_form_step_4 = ReportForm_Step4(request.POST, request.FILES)

        # Check if form step 1 is valid
        if report_form_step_1.is_valid():

            # process step 1 of the report creation
            step_1_data = process_report_step_1(request.POST, request.FILES, request)

            # Catch errors in step 1
            if not step_1_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "signature_base64": request.POST.get("signature_base64", ""),
                }

                return render(request, 'reports/create_report.html', context=context)
        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "signature_base64": request.POST.get("signature_base64", ""),
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 1)")
            print("\n######## Form step 1 is not valid:", report_form_step_1.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Check if form step 2 is valid
        if report_form_step_2.is_valid():

            # process step 2 of the report creation
            step_2_data = process_report_step_2(request.POST, request.FILES, request)

            # Catch errors in step 2
            if not step_2_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "signature_base64": request.POST.get("signature_base64", ""),
                }

                return render(request, 'reports/create_report.html', context=context)
        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "signature_base64": request.POST.get("signature_base64", ""),
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 2)")
            print("\n######## Form step 2 is not valid:", report_form_step_2.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Check if form step 3 is valid
        if report_form_step_3.is_valid():

            # process step 3 of the report creation
            step_3_data = process_report_step_3(request.POST, request.FILES, request)

            # Catch errors in step 3
            if not step_3_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "signature_base64": request.POST.get("signature_base64", ""),
                }

                return render(request, 'reports/create_report.html', context=context)
        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "signature_base64": request.POST.get("signature_base64", ""),
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 3)")
            print("\n######## Form step 3 is not valid:", report_form_step_3.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Check if form step 4 is valid
        if report_form_step_4.is_valid():

            # process step 4 of the report creation
            step_4_data = process_report_step_4(request.POST, request.FILES, request)

            # Catch errors in step 4
            if not step_4_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "signature_base64": request.POST.get("signature_base64", ""),
                }

                return render(request, 'reports/create_report.html', context=context)

        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "signature_base64": request.POST.get("signature_base64", ""),
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 4)")
            print("\n######## Form step 4 is not valid:", report_form_step_3.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Create damage report instance
        damage_report = DamageReport.objects.create(workshop=workshop)

        try:

            # Update damage report with step 1 data
            damage_report.person_or_company = step_1_data["data"]["person_or_company"]
            damage_report.company_name = step_1_data["data"]["company_name"]
            damage_report.first_name = step_1_data["data"]["first_name"]
            damage_report.last_name = step_1_data["data"]["last_name"]

            accident_datetime = datetime.strptime(step_1_data["data"]["accident_datetime"], "%d.%m.%Y %H:%M")
            if timezone.is_naive(accident_datetime):
                accident_datetime = timezone.make_aware(accident_datetime)
            # handle accident datetime
            damage_report.accident_datetime = accident_datetime

            # Handle signature
            signature = step_1_data["data"]["signature_base64"]
            format, imgstr = signature.split(';base64,')
            ext = format.split('/')[-1]  # z.B. 'png'
            data = ContentFile(base64.b64decode(imgstr), name=f'signature_{damage_report.id}.{ext}')
            damage_report.signature.save(data.name, data)

            # Update damage report with step 2 data
            damage_report.address = step_2_data["data"]["address"]
            damage_report.email = step_2_data["data"]["email"]
            damage_report.phone_number = step_2_data["data"]["phone_number"]
            damage_report.iban = step_2_data["data"]["iban"]
            if step_2_data["data"]["bank_image"]:
                bank_image = step_2_data["data"]["bank_image"]
                damage_report.bank_image.save(bank_image.name, bank_image)
            damage_report.plate_number = step_2_data["data"]["plate_number"]
            damage_report.inspection = step_2_data["data"]["inspection"]

            damage_report.checkbook_exists = step_2_data["data"]["checkbook_exists"]
            if step_2_data["data"]["checkbook"]:
                checkbook = step_2_data["data"]["checkbook"]
                damage_report.checkbook.save(checkbook.name, checkbook)
            damage_report.leased = step_2_data["data"]["leased"]
            damage_report.financed = step_2_data["data"]["financed"]

            # Update damage report with step 3 data
            damage_report.opponent_plate_number = step_3_data["data"]["opponent_plate_number"]
            damage_report.opponent_insurance_number = step_3_data["data"]["opponent_insurance_number"]
            damage_report.damage_number = step_3_data["data"]["damage_number"]
            damage_report.has_witnesses = step_3_data["data"]["has_witnesses"]

            damage_report.witness_textfield = step_3_data["data"]["witness_textfield"]
            damage_report.accident_location = step_3_data["data"]["accident_location"]
            damage_report.accident_scenarios.set(step_3_data["data"]["accident_scenarios"])
            damage_report.accident_notes = step_3_data["data"]["accident_notes"]

            # Update damage report with images from step 4 data
            for field, image_file in step_4_data["data"]["images"].items():
                if image_file:
                    # Extract the image_view from the field name, e.g. 'image_front_left' -> 'front_left'
                    image_view = field.replace("image_", "")
                    DamageImage.objects.create(
                        damage_report=damage_report,
                        image=image_file,
                        image_view=image_view
                    )

        except Exception as e:
            print(f"Error while processing report data: {e}")
            custom_messages(request, message_type="error", message_text="Fehler beim Verarbeiten der Report-Daten!")
            damage_report.delete()
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "signature_base64": request.POST.get("signature_base64", ""),
            }
            return render(request, 'reports/create_report.html', context=context)

        else:

            # Save the damage report instance
            damage_report.save()

            api_handler = AutoixpertAPIHandler()
            api_report_data = api_handler.create_report(damage_report=damage_report)

            # Überprüfen, ob das Gutachten in Autoixpert erfolgreich erstellt wurde
            if api_report_data and api_report_data.get('report', {}).get('id'):
                report_id_autoixpert = api_report_data['report']['id']

                # Save the Autoixpert ID to the damage report
                damage_report.autoixpert_id = report_id_autoixpert
                damage_report.save()
                custom_messages(request, message_type="success", message_text="Auftraft erfolgreich erstellt!")

                # Iteriere über alle DamageImage-Objekte, die mit diesem DamageReport verknüpft sind
                for damage_image in damage_report.images.all():
                    if damage_image.image:  # Stelle sicher, dass ein Bild tatsächlich hochgeladen wurde
                        uploaded_photo_data = api_handler.upload_report_photo(
                            report_id=report_id_autoixpert,
                            damage_image_obj=damage_image  # Übergabe des Django DamageImage-Objekts
                        )
                        if uploaded_photo_data:
                            damage_image.autoixpert_id = uploaded_photo_data.get('id')
                            damage_image.save()  # Speichere die Autoixpert-ID im DamageImage-Objekt
                            print(f"Bild '{damage_image.image.name}' (ID: {uploaded_photo_data.get('id')}) erfolgreich hochgeladen.")
                        else:
                            custom_messages(request, message_type="error", message_text=f"Fehler beim Hochladen des Bildes '{damage_image.image.name}'.")
                            print(f"Fehler beim Hochladen des Bildes: {damage_image.image.name}")

            # Handle witnesses
            for witness_line in step_3_data["data"]["witness_list"]:
                witness_data = witness_line.split(" | ")
                if len(witness_data) == 3:
                    witness_name = witness_data[0].strip()
                    witness_adress = witness_data[1].strip()
                    witness_phone = witness_data[2].strip()

                    # Create a new witness instance
                    witness = Witness.objects.create(
                        damage_report=damage_report,
                        name=witness_name,
                        address=witness_adress,
                        phone_number=witness_phone

                    )

    context = {
        "report_form_step_1": report_form_step_1,
        "report_form_step_2": report_form_step_2,
        "report_form_step_3": report_form_step_3,
        "report_form_step_4": report_form_step_4,
    }

    return render(request, 'reports/create_report.html', context=context)


@login_required(login_url="login")
def edit_report_form(request, report_id):

    # Extract damage report
    report = DamageReport.objects.get(id=report_id)

    # Extract account
    account: Account = request.user.account

    # Extract all report forms
    report_form_step_1 = ReportForm_Step1(instance=report)
    report_form_step_2 = ReportForm_Step2(instance=report)
    report_form_step_3 = ReportForm_Step3(instance=report)

    # Step 1-3: ModelForms mit instance
    initial_step_4 = {}
    for image in report.images.all():
        field_name = f'image_{image.image_view}'
        initial_step_4[field_name] = image.image

    report_form_step_4 = ReportForm_Step4(initial=initial_step_4)

    # Handle POST request
    if request.method == "POST":

        report_form_step_1 = ReportForm_Step1(request.POST, request.FILES)
        report_form_step_2 = ReportForm_Step2(request.POST, request.FILES)
        report_form_step_3 = ReportForm_Step3(request.POST, request.FILES)
        report_form_step_4 = ReportForm_Step4(request.POST, request.FILES)

        # Check if form step 1 is valid
        if report_form_step_1.is_valid():

            # process step 1 of the report creation
            step_1_data = process_editing_step_1(request.POST, request.FILES, request)

            # Catch errors in step 1
            if not step_1_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "editing": True,
                }

                return render(request, 'reports/create_report.html', context=context)
        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "editing": True,

            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 1)")
            print("\n######## Form step 1 is not valid:", report_form_step_1.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Check if form step 2 is valid
        if report_form_step_2.is_valid():

            # process step 2 of the report creation
            step_2_data = process_report_step_2(request.POST, request.FILES, request)

            # Catch errors in step 2
            if not step_2_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "editing": True,
                }

                return render(request, 'reports/create_report.html', context=context)
        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "editing": True,
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 2)")
            print("\n######## Form step 2 is not valid:", report_form_step_2.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Check if form step 3 is valid
        if report_form_step_3.is_valid():

            # process step 3 of the report creation
            step_3_data = process_report_step_3(request.POST, request.FILES, request)

            # Catch errors in step 3
            if not step_3_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "editing": True,
                }

                return render(request, 'reports/create_report.html', context=context)
        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "editing": True,
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 3)")
            print("\n######## Form step 3 is not valid:", report_form_step_3.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Check if form step 4 is valid
        if report_form_step_4.is_valid():

            # process step 4 of the report creation
            step_4_data = process_editing_step_4(request.POST, request.FILES, request)

            # Catch errors in step 4
            if not step_4_data["success"]:
                context = {
                    "report_form_step_1": report_form_step_1,
                    "report_form_step_2": report_form_step_2,
                    "report_form_step_3": report_form_step_3,
                    "report_form_step_4": report_form_step_4,
                    "editing": True,
                }

                return render(request, 'reports/create_report.html', context=context)

        else:
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "editing": True,
            }

            custom_messages(request, message_type="error", message_text="Fehler bei der Formularvalidierung! (Step 4)")
            print("\n######## Form step 4 is not valid:", report_form_step_3.errors.as_json())

            return render(request, 'reports/create_report.html', context=context)

        # Extract damage report instance
        damage_report = report

        try:

            # Update damage report with step 1 data
            damage_report.person_or_company = step_1_data["data"]["person_or_company"]
            damage_report.company_name = step_1_data["data"]["company_name"]
            damage_report.first_name = step_1_data["data"]["first_name"]
            damage_report.last_name = step_1_data["data"]["last_name"]

            accident_datetime = datetime.strptime(step_1_data["data"]["accident_datetime"], "%Y-%m-%d %H:%M")
            if timezone.is_naive(accident_datetime):
                accident_datetime = timezone.make_aware(accident_datetime)
            # handle accident datetime
            damage_report.accident_datetime = accident_datetime

            # Update damage report with step 2 data
            damage_report.address = step_2_data["data"]["address"]
            damage_report.email = step_2_data["data"]["email"]
            damage_report.phone_number = step_2_data["data"]["phone_number"]
            damage_report.iban = step_2_data["data"]["iban"]
            if step_2_data["data"]["bank_image"]:
                bank_image = step_2_data["data"]["bank_image"]
                damage_report.bank_image.save(bank_image.name, bank_image)
            damage_report.plate_number = step_2_data["data"]["plate_number"]
            damage_report.inspection = step_2_data["data"]["inspection"]

            damage_report.checkbook_exists = step_2_data["data"]["checkbook_exists"]
            if step_2_data["data"]["checkbook"]:
                checkbook = step_2_data["data"]["checkbook"]
                damage_report.checkbook.save(checkbook.name, checkbook)
            damage_report.leased = step_2_data["data"]["leased"]
            damage_report.financed = step_2_data["data"]["financed"]

            # Update damage report with step 3 data
            damage_report.opponent_plate_number = step_3_data["data"]["opponent_plate_number"]
            damage_report.opponent_insurance_number = step_3_data["data"]["opponent_insurance_number"]
            damage_report.damage_number = step_3_data["data"]["damage_number"]
            damage_report.has_witnesses = step_3_data["data"]["has_witnesses"]

            damage_report.witness_textfield = step_3_data["data"]["witness_textfield"]
            damage_report.accident_location = step_3_data["data"]["accident_location"]
            damage_report.accident_scenarios.set(step_3_data["data"]["accident_scenarios"])
            damage_report.accident_notes = step_3_data["data"]["accident_notes"]

            # Update damage report with images from step 4 data
            for field, image_file in step_4_data["data"]["images"].items():
                if image_file:
                    # Extract the image_view from the field name, e.g. 'image_front_left' -> 'front_left'
                    image_view = field.replace("image_", "")
                    DamageImage.objects.create(
                        damage_report=damage_report,
                        image=image_file,
                        image_view=image_view
                    )

        except Exception as e:
            print(f"Error while processing report data: {e}")
            custom_messages(request, message_type="error", message_text="Fehler beim Verarbeiten der Report-Daten!")
            context = {
                "report_form_step_1": report_form_step_1,
                "report_form_step_2": report_form_step_2,
                "report_form_step_3": report_form_step_3,
                "report_form_step_4": report_form_step_4,
                "editing": True,
            }
            return render(request, 'reports/create_report.html', context=context)

        else:

            # Save the damage report instance
            damage_report.save()

            api_handler = AutoixpertAPIHandler()
            update_resone = api_handler.update_report(report_id=damage_report.autoixpert_id, damage_report=damage_report)

            # Überprüfen, ob das Gutachten in Autoixpert erfolgreich erstellt wurde
            if update_resone.status_code == 200:
                custom_messages(request, message_type="success", message_text="Auftraft bearbeitet!")

            # Handle witnesses
            for witness_line in step_3_data["data"]["witness_list"]:
                witness_data = witness_line.split(" | ")
                if len(witness_data) == 3:
                    witness_name = witness_data[0].strip()
                    witness_adress = witness_data[1].strip()
                    witness_phone = witness_data[2].strip()

                    # Create a new witness instance
                    witness = Witness.objects.create(
                        damage_report=damage_report,
                        name=witness_name,
                        address=witness_adress,
                        phone_number=witness_phone

                    )

    context = {
        "report_form_step_1": report_form_step_1,
        "report_form_step_2": report_form_step_2,
        "report_form_step_3": report_form_step_3,
        "report_form_step_4": report_form_step_4,
        "editing": True,
    }

    return render(request, 'reports/create_report.html', context=context)
