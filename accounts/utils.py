from x_global_utils import custom_messages
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from .models import WorkshopData


def raise_registration_error(request, post_data):

    # Check if user exists
    if User.objects.filter(email=post_data["email"].lower()).exists():
        custom_messages(request, "error", "User existiert bereits!")

    # Chek if passwords match
    elif post_data["password1"] != post_data["password2"]:
        custom_messages(request, "error", "Passwörter stimmen nicht überein!")


def workshop_data_complete(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # Make sure that the user is logged in
        if not user.is_authenticated:
            return redirect("login")  # If the user is not logged in

        # Extract account
        account = user.account

        try:
            # WorkshopData for the account
            workshop_data = WorkshopData.objects.get(account=account)
        except ObjectDoesNotExist:
            custom_messages(request, "error", "Bitte Werkstatt-Daten ergänzen!")
            return redirect("settings")  # If no WorkshopData exists

        # Check if all fields are filled
        required_fields = [
            "workshop_name",
            "address",
            "plz",
            "city",
            "country",
            "primary_contact",
            "phone_number",
            "email",
            "tax_id",
            # "verification_document",
        ]

        if not all(getattr(workshop_data, field, None) for field in required_fields):
            custom_messages(request, "error", "Bitte Werkstatt-Daten ergänzen!")
            return redirect("settings")  # If data is missing

        # If everything fits, call up the original view
        return view_func(request, *args, **kwargs)

    return wrapper
