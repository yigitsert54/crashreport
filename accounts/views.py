# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.models import User


# Forms
from .forms import RegistrationForm, LoginForm, AccountForm, WorkshopForm
from django.contrib.auth.forms import PasswordChangeForm

# models
from .models import WorkshopData, Account
from reports.models import DamageReport

# Own functions and methods
from .utils import raise_registration_error, workshop_data_complete
from x_global_utils import custom_messages, email_is_valid, phone_number_valid

# bibs
import json


def dashboard(request):
    return render(request, "dashboard.html")


def uikit(request):
    return render(request, "uikit.html")


@workshop_data_complete
def home(request):

    return redirect("reports_home")


def user_registration(request):
    form = RegistrationForm()

    # Handle POST request
    if request.method == "POST":

        # Extract registration form
        form = RegistrationForm(request.POST)

        # Check if form is valid
        if form.is_valid():

            # hold on user
            user = form.save(commit=False)

            # Change user fields
            user.first_name = user.first_name.capitalize()
            user.last_name = user.last_name.capitalize()
            user.email = user.email.lower()
            user.username = user.email.lower()

            # Save user
            user.save()

            # Login user
            login(request, user)

            return redirect("home")

        else:

            # Send error message
            raise_registration_error(request, request.POST)

    context = {
        "purpose": "register",
        "form": form
    }

    return render(request, "accounts/registration.html", context=context)


def user_login(request):

    form = LoginForm()

    # Check if user is already logged in
    if request.user.is_authenticated:
        # redirect to dashboard
        return redirect("home")

    # Handle login request
    if request.method == "POST":

        # Get username and password from POST request
        username = request.POST["username"].lower()
        password = request.POST["password"]

        try:  # Get user from username
            user = User.objects.get(username=username)
        except:  # If username doesn't exist
            custom_messages(request, message_type="error", message_text="Nutzer existiert nicht!")
        else:  # If user does exist authenticate login request
            user = authenticate(request, username=username, password=password)

            # If authentication was successful (user is not None)
            if user is not None:

                # Login user
                login(request, user)

                # Get next string from url
                next = request.GET.get("next")

                # if there is a next string...
                if next != "" and next is not None:
                    # .. redirect to next
                    return redirect(next)
                else:  # if there is no next string

                    # redirect to home screen
                    return redirect("home")

            # If authentication was NOT successful (wrong password)
            else:
                custom_messages(request, message_type="error", message_text="Falsches Passwort!")

    context = {
        "purpose": "login",
        "form": form
    }

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def user_logout(request):
    logout(request)

    return redirect("login")


@login_required(login_url="login")
def settings(request):

    # Get account
    account = request.user.account

    # Get Account form
    account_form = AccountForm(instance=account)

    # Create password change form
    pw_form = PasswordChangeForm(user=request.user)

    # Remove autofocus
    pw_form.fields['old_password'].widget.attrs.pop('autofocus', None)

    # Add classes to passwort form and edit attributes
    for name, field in pw_form.fields.items():
        field.widget.attrs.update({"class": "form-control"})

        # Set icons
        if name == "old_password":
            field.widget.attrs.update({"icon": "envelope"})
        elif name == "new_password1":
            field.widget.attrs.update({"icon": " bxs-envelope"})
        elif name == "new_password2":
            field.widget.attrs.update({"icon": "check-double"})

    # Change placeholders
    pw_form.fields['old_password'].widget.attrs.update({"placeholder": "Aktuelles Passwort"})
    pw_form.fields['new_password1'].widget.attrs.update({"placeholder": "Neues Passwort"})
    pw_form.fields['new_password2'].widget.attrs.update({"placeholder": "Neues Passwort bestätigen"})

    # Extract workshop form
    if WorkshopData.objects.filter(account=account).exists():
        workshop_data = WorkshopData.objects.get(account=account)
    else:
        workshop_data = WorkshopData.objects.create(account=account)

    workshop_form = WorkshopForm(instance=workshop_data)

    for name, field in workshop_form.fields.items():
        # Wenn das Feld im Model leer ist, CSS-Klasse hinzufügen
        if not getattr(workshop_data, name, None):
            field.widget.attrs.update(
                {"class": field.widget.attrs.get("class", "") + " missing-field"})

    context = {
        "pw_form": pw_form,
        "account_form": account_form,
        "workshop_form": workshop_form
    }

    return render(request, 'accounts/settings.html', context=context)


@login_required(login_url="login")
def change_password(request):

    # Handle POST request
    if request.method == "POST":

        # Get form data
        form = PasswordChangeForm(user=request.user, data=request.POST)

        # Check if form is valid
        if form.is_valid():

            form.save()

            # message
            custom_messages(request, message_type="success", message_text="Passwort geändert!")

            # Update session
            update_session_auth_hash(request, form.user)

            # redirect to settings page again
            return redirect("settings")

        # If form is not valid
        else:

            # Create custom error messages
            error_messages = {
                "password_incorrect": "Dein aktuelles Passwort wurde falsch eingegeben!",
                "password_mismatch": "Die beiden Passwörter stimmten nicht überein!",
                "password_too_short": "Dieses Passwort ist zu kurz. Es muss mindestens 8 Zeichen enthalten!",
                "password_entirely_numeric": "Passwort darf nicht ausschließlich aus Zahlen bestehen!",
                "password_too_similar": "Das Passwort ähnelt deinen persönlichen Daten zu sehr!",
                "password_too_common": "Passwort darf kein häufig verwendetes Passwort sein!",
            }

            # Load all error messages from validation errors
            error_dict = json.loads(form.errors.as_json())

            # Set error message
            error_message = ""

           # Loop through each custom error
            for code, msg in error_messages.items():

                # Loop throgh each validation error
                for label, error_list in error_dict.items():

                    # Loop through each error in list
                    for error in error_list:

                        # Check if the codes macth
                        if code == error["code"]:

                            # Set error_message to custom msg
                            error_message = msg

                            # Create error message
                            custom_messages(request, message_type="error", message_text=msg)

                            # redirect to settings page again
                            return redirect("settings")

            # Check if no error message was set
            if error_message == "":

                # Create a general error message
                custom_messages(request, message_type="error", message_text="Das hat leider nicht geklappt!")

                # redirect to settings page again
                return redirect("settings")

    # redirect to settings page again
    return redirect("settings")


@login_required(login_url="login")
def edit_account_data(request):

    # Get User account
    account = request.user.account

    # Handle POST request
    if request.method == "POST":

        # Get form
        form = AccountForm(request.POST, instance=account)

        # Check if form is valid
        if form.is_valid():

            # Save form data without commiting
            account = form.save(commit=False)

            # Extract POST data
            new_email = request.POST["email"].lower()
            new_first_name = request.POST["first_name"].capitalize()
            new_last_name = request.POST["last_name"].capitalize()

            # Check if names are valid
            if len(new_first_name) <= 2 or len(new_last_name) <= 2:

                # Error message
                custom_messages(request, message_type="error", message_text="Vor- oder Nachname ungültig!")
                # redirect to settings page again
                return redirect("settings")

            # Validate Email
            if not email_is_valid(new_email):

                custom_messages(request, message_type="error", message_text="Bitte eine gültige E-Mail eingeben!")

                # redirect to settings page again
                return redirect("settings")

            # Set account values to POST data
            account.first_name = new_first_name
            account.last_name = new_last_name
            account.email = new_email

            # message
            custom_messages(request, message_type="success", message_text="Daten geändert!")

            account.save()

            # redirect to settings page again
            return redirect("settings")

    # redirect to settings page again
    return redirect("settings")


@login_required(login_url="login")
def edit_workshop_data(request):

    # Get User account
    account = request.user.account

    workshop = account.workshop

    # Extract workshop form
    if WorkshopData.objects.filter(account=account).exists():
        workshop_data = WorkshopData.objects.get(account=account)
    else:
        workshop_data = WorkshopData.objects.create(account=account)

    workshop_form = WorkshopForm(instance=workshop_data)

    # Handle POST request
    if request.method == "POST":

        # Get form
        form = WorkshopForm(request.POST, request.FILES, instance=workshop)

        # Check if form is valid
        if form.is_valid():

            # Save form data without commiting
            workshop = form.save(commit=False)

            # Extract email
            new_email = request.POST["email"].lower()

            # Validate Email
            if not email_is_valid(new_email):
                # Error message
                custom_messages(request, message_type="error", message_text="Bitte eine gültige E-Mail eingeben!")

                # redirect to settings page again
                return redirect("edit_workshop_data")

            # Extract phone number
            new_phone_number = request.POST["phone_number"].lower().replace("-", "").replace("/", "").replace(" ", "")

            # Validate phone number
            if not phone_number_valid(new_phone_number):
                # Error message
                custom_messages(request, message_type="error", message_text="Bitte eine gültige Telefonnummer eingeben!")
                # redirect to settings page again
                return redirect("edit_workshop_data")

            # Set new values
            workshop.email = new_email
            workshop.phone_number = new_phone_number

            # Handle file Delete
            if "remove_document" in request.POST:
                workshop.verification_document = None

            # message
            custom_messages(request, message_type="success", message_text="Daten geändert!")

            workshop.save()

            # redirect to settings page again
            return redirect("edit_workshop_data")

    context = {
        "workshop_form": workshop_form
    }

    return render(request, 'accounts/edit_workshop_data.html', context=context)
