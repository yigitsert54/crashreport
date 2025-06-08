from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.contrib.auth.decorators import login_required

# models
from accounts.models import Account, WorkshopData
from .models import DamageReport, DamageImage

# forms
from .forms import (
    ReportForm,
    DamageReportStep4ImagesForm,
    ReportForm_Step1,
    ReportForm_Step2,
    ReportForm_Step3,
    ReportForm_Step4
)

# Import the WizardView.
from formtools.wizard.views import SessionWizardView  # SessionWizardView saves data between the steps in the session.

# Own functions and methods
from x_global_utils import custom_messages, email_is_valid, phone_number_valid


@login_required(login_url="login")
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


@login_required(login_url="login")
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
    report_form_step_4 = ReportForm_Step4()

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
        "report_form_step_4": report_form_step_4,
    }

    return render(request, 'reports/create_report.html', context=context)


@login_required(login_url="login")
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
