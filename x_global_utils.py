from django.contrib import messages
from django.core.validators import validate_email
from django.forms import ValidationError


def custom_messages(request, message_type, message_text):

    # Set classes
    classes = ""

    # Error
    if message_type == "error":
        classes = "error_message_class"
        return messages.error(request, message_text, extra_tags=classes)

    # Success
    elif message_type == "success":
        classes = "success_message_class"
        return messages.success(request, message_text, extra_tags=classes)

    # Info
    elif message_type == "info":
        classes = "info_message_class"
        return messages.info(request, message_text, extra_tags=classes)


def email_is_valid(email: str) -> bool:

    try:  # Validate Email
        validate_email(email)

    except ValidationError:  # If email is NOT valid
        # Error message
        # custom_messages(request, message_type="error", message_text="Bitte eine gültige E-Mail eingeben!")

        # redirect to settings page again
        return False

    return True


def phone_number_valid(phone_number: str) -> bool:

    symbol_string = "+.,;:_!?\"'`^°~*#×÷=≠<>≤≥|\\[](){}@&%$€£¥¢©®™µ§¶•¿¡«»‹›""''"

    for symbol in symbol_string:
        if symbol in phone_number:

            if symbol == "+":

                if phone_number[0] != "+":
                    return False
                elif len(phone_number) - len(phone_number.replace("+", "")) > 1:
                    return False
            else:
                return False

    # Remove symbols from phone number
    formatted_number = phone_number.replace("+", "").replace("-", "").replace("/", "").replace(" ", "")

    try:  # turn into int
        number_as_int = int(formatted_number)
    except ValueError:
        return False

    # Check length
    if len(formatted_number) < 6:
        return False

    return True
