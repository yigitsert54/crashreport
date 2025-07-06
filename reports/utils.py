from .models import DamageReport
from x_global_utils import custom_messages, phone_number_valid, email_is_valid
from django.db import transaction
from schwifty import IBAN
import requests
import json
from datetime import timezone as tz
from datetime import datetime
import mimetypes
import os


def process_report_step_1(data, files, request):
    """
    extracts the data that is needed for step 1 of the report creation process and validates them.
    """

    response = {
        "success": False,
        "data": {}
    }

    # Extract data from request
    person_or_company = data.get("person_or_company", None)
    company_name = data.get("company_name", "")
    first_name = data.get("first_name", "").capitalize()
    last_name = data.get("last_name", "").capitalize()
    accident_datetime = data.get("accident_datetime", None)
    signature_base64 = data.get("signature_base64", None)

    # Validate data: person_or_company
    if person_or_company == "company" and len(company_name) < 2:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie einen gültigen Firmennamen an.")
        return response

    # Validate data: names
    if len(first_name) < 2 or len(last_name) < 2:
        custom_messages(request, message_type="error", message_text="Vor- oder Nachname ungültig!")
        return response

    # Validate data: datetime
    if not accident_datetime:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie ein gültiges Unfalldatum an.")
        return response

    # Validate data: signature
    if not signature_base64 or not signature_base64.startswith("data:image/png;base64,"):
        custom_messages(request, message_type="error", message_text="Bitte unterschreiben Sie das Formular.")
        return response

    response["success"] = True
    response["data"] = {
        "person_or_company": person_or_company,
        "company_name": company_name,
        "first_name": first_name,
        "last_name": last_name,
        "accident_datetime": accident_datetime,
        "signature_base64": signature_base64,
    }

    # Return response
    return response


def process_report_step_2(data, files, request):
    """
    extracts the data that is needed for step 2 of the report creation process and validates them.
    """

    response = {
        "success": False,
        "data": {}
    }

    # Extract data from request
    address = data.get("address", "")
    email = data.get("email", "").lower()
    phone_number = data.get("phone_number", "").lower().replace("-", "").replace("/", "").replace(" ", "")
    iban = data.get("iban", "")
    bank_image = files.get("bank_image", None)
    plate_number = data.get("plate_number", "")
    inspection = data.get("inspection", None)
    checkbook_exists = data.get("checkbook_exists", False)
    if checkbook_exists != False:
        checkbook_exists = True

    checkbook = files.get("checkbook", None)

    leased = data.get("leased", False)
    if leased != False:
        leased = True

    financed = data.get("financed", False)
    if financed != False:
        financed = True

    # Validate data: person_or_company
    if len(address) < 6:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige Adresse an.")
        return response

    # Validate data: email
    if not email_is_valid(email):
        custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige E-Mail-Adresse an.")
        return response

    # Validate data: phone number
    if not phone_number_valid(phone_number):
        custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige Telefonnummer an.")
        return response

    # Validate data: iban
    try:
        iban_obj = IBAN(iban)
        if not iban_obj.is_valid:
            custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige IBAN an.")
            return response
    except ValueError:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige IBAN an.")
        return response

    # Validate data: plate number
    if len(plate_number) < 3:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie ein gültiges Kennzeichen an.")
        return response

    # Validate data: checkbook
    if checkbook_exists and not checkbook:
        custom_messages(request, message_type="error", message_text="Bitte laden Sie das Scheckheft hoch.")
        return response

    response["success"] = True
    response["data"] = {
        "address": address,
        "email": email,
        "phone_number": phone_number,
        "iban": iban,
        "bank_image": bank_image,
        "plate_number": plate_number,
        "inspection": inspection if inspection and len(inspection) > 2 else None,
        "checkbook_exists": checkbook_exists,
        "checkbook": checkbook,
        "leased": leased,
        "financed": financed,
    }

    # Return response
    return response


def process_report_step_3(data, files, request):
    """
    extracts the data that is needed for step 3 of the report creation process and validates them.
    """

    response = {
        "success": False,
        "data": {}
    }

    # Extract data from request
    opponent_plate_number = data.get("opponent_plate_number", "")
    opponent_insurance_number = data.get("opponent_insurance_number", "")
    damage_number = data.get("damage_number", "")
    has_witnesses = data.get("has_witnesses", False)
    if has_witnesses != False:
        has_witnesses = True

    witness_textfield = data.get("witness_textfield", "")
    accident_location = data.get("accident_location", "")
    accident_scenarios = data.getlist("accident_scenarios", [])
    accident_notes = data.get("accident_notes", "")

    # Validate data: opponent_plate_number
    if len(opponent_plate_number) < 3:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie ein gültiges Kennzeichen des Unfallgegners an.")
        return response

    # Validate data: opponent_insurance_number
    if len(opponent_insurance_number) < 3:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige Versicherungsnummer des Unfallgegners an.")
        return response

    # Validate data: damage_number
    if len(damage_number) < 3:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie eine gültige Schadensnummer an.")
        return response

    # Validate data: witness data
    if has_witnesses and len(witness_textfield.split("\n")) < 1:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie mindestens einen Zeugen an.")
        return response

    # Validate data: accident_location
    if len(accident_location) < 3:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie einen gültigen Unfallort an.")
        return response

    response["success"] = True
    response["data"] = {
        "opponent_plate_number": opponent_plate_number,
        "opponent_insurance_number": opponent_insurance_number,
        "damage_number": damage_number,
        "has_witnesses": has_witnesses,
        "witness_textfield": witness_textfield,
        "witness_list": witness_textfield.split("\n") if len(witness_textfield) > 0 else [],
        "accident_location": accident_location,
        "accident_scenarios": accident_scenarios,
        "accident_notes": accident_notes,
    }

    # Return response
    return response


def process_report_step_4(data, files, request):
    """
    extracts the data that is needed for step 4 of the report creation process and validates them.
    """

    response = {
        "success": False,
        "data": {}
    }

    # Extract all image files whose keys start with 'image_'
    image_fields = [key for key in files.keys() if key.startswith("image_")]
    images = {}

    for field in image_fields:
        image_file = files.get(field)
        if image_file:
            images[field] = image_file

    # At least one image must be uploaded
    if not images:
        custom_messages(request, message_type="error", message_text="Bitte laden Sie mindestens ein Bild hoch!")
        return response

    response["success"] = True
    response["data"] = {
        "images": images
    }
    return response


def process_editing_step_1(data, files, request):
    """
    extracts the data that is needed for step 1 of the report creation process and validates them.
    """

    response = {
        "success": False,
        "data": {}
    }

    # Extract data from request
    person_or_company = data.get("person_or_company", None)
    company_name = data.get("company_name", "")
    first_name = data.get("first_name", "").capitalize()
    last_name = data.get("last_name", "").capitalize()
    accident_datetime = data.get("accident_datetime", None)

    # Validate data: person_or_company
    if person_or_company == "company" and len(company_name) < 2:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie einen gültigen Firmennamen an.")
        return response

    # Validate data: names
    if len(first_name) < 2 or len(last_name) < 2:
        custom_messages(request, message_type="error", message_text="Vor- oder Nachname ungültig!")
        return response

    # Validate data: datetime
    if not accident_datetime:
        custom_messages(request, message_type="error", message_text="Bitte geben Sie ein gültiges Unfalldatum an.")
        return response

    response["success"] = True
    response["data"] = {
        "person_or_company": person_or_company,
        "company_name": company_name,
        "first_name": first_name,
        "last_name": last_name,
        "accident_datetime": accident_datetime,
    }

    # Return response
    return response


def process_editing_step_4(data, files, request):
    """
    extracts the data that is needed for step 4 of the report creation process and validates them.
    """

    response = {
        "success": False,
        "data": {}
    }

    # Extract all image files whose keys start with 'image_'
    image_fields = [key for key in files.keys() if key.startswith("image_")]
    images = {}

    for field in image_fields:
        image_file = files.get(field)
        if image_file:
            images[field] = image_file

    response["success"] = True
    response["data"] = {
        "images": images
    }
    return response


def complete_address(address_string: str, country: str = "DE") -> dict:
    """
    Vervollständigt eine Adresse über die Google Geocoding API und
    liefert formatierte Adresse sowie Einzelteile: Straße, Hausnummer, PLZ, Ort.

    Args:
        address_string (str): Die (ggf. unvollständige) Eingabe-Adresse.
        country (str): Ländercode zur Ergebnis-Einschränkung (Default "DE").

    Returns:
        dict: {
            "formatted_address": str,
            "street": str or None,
            "street_number": str or None,
            "postal_code": str or None,
            "city": str or None
        }
        oder {"error": "<Fehlermeldung>"} bei Problemen.
    """

    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address_string,
        "components": f"country:{country}",
        "key": "AIzaSyC7KR7tSiM_BfzUc8MfGC0WADHVFH8XdNE",
        "language": "de",
    }

    try:
        resp = requests.get(endpoint, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

    except requests.RequestException as e:
        print(f"\nHTTP-Fehler bei API-Aufruf: {e}")
        return {
            "address_corrected": False,
            "formatted_address": address_string,
            "street": None,
            "street_number": None,
            "postal_code": None,
            "city": None,
        }

    except ValueError:
        print(f"Ungültiges JSON in der Antwort.")
        return {
            "address_corrected": False,
            "formatted_address": address_string,
            "street": None,
            "street_number": None,
            "postal_code": None,
            "city": None,
            "country": None
        }

    status = data.get("status")
    if status != "OK" or not data.get("results"):
        print(f"API-Fehler: {status}")
        return {
            "address_corrected": False,
            "formatted_address": address_string,
            "street": None,
            "street_number": None,
            "postal_code": None,
            "city": None,
            "country": None
        }

    result = data["results"][0]
    comps = result.get("address_components", [])
    parsed = {"street": None, "street_number": None, "postal_code": None, "city": None, "country": None}

    for c in comps:
        types = c.get("types", [])
        if "route" in types:
            parsed["street"] = c.get("long_name")
        elif "street_number" in types:
            parsed["street_number"] = c.get("long_name")
        elif "postal_code" in types:
            parsed["postal_code"] = c.get("long_name")
        elif "locality" in types or "postal_town" in types:
            parsed["city"] = c.get("long_name")
        elif "country" in types:
            parsed["country"] = c.get("long_name")

    if parsed["street"] and parsed["street_number"] and parsed["postal_code"] and parsed["city"] and parsed["country"]:
        return {
            "address_corrected": True,
            "formatted_address": result.get("formatted_address"),
            **parsed
        }
    else:
        return {
            "address_corrected": False,
            "formatted_address": address_string,
            "street": None,
            "street_number": None,
            "postal_code": None,
            "city": None,
            "country": None
        }


class AutoixpertAPIHandler:
    """
    A class to handle the Autoixpert API interactions.
    This class is responsible for sending the report data to the Autoixpert API.
    """

    def __init__(self):
        self.key = "kT3fRFyi26dV"
        self.base_url = "https://app.autoixpert.de/externalApi/v1"
        self.headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        self.responsible_assessor_id = "8craqPQ95ZWb"

    def get_all_users(self):
        """
        Ruft eine Liste aller aktiven Nutzer (Sachverständigen) von der API ab.

        :return: Eine Liste von Nutzer-Objekten oder None bei einem Fehler.
        """
        users_url = f"{self.base_url}/users"
        print(f"Rufe Nutzerdaten von {users_url} ab...")

        try:
            response = requests.get(users_url, headers=self.headers)
            response.raise_for_status()

            print("Nutzerdaten erfolgreich abgerufen!")
            return response.json().get('users', [])

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP-Fehler beim Abrufen der Nutzer: {http_err}")
            print(f"Antwort-Body: {http_err.response.text}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Netzwerk-Fehler aufgetreten: {req_err}")
            return None

    def get_reports(self, limit=10):
        """
        Ruft eine Liste von Gutachten von der autoiXpert-API ab.

        :param limit: Die maximale Anzahl der zurückzugebenden Gutachten (Standard: 10, Max: 10).
        :return: Ein Dictionary mit den Gutachtendaten oder None bei einem Fehler.
        """
        reports_url = f"{self.base_url}/reports"
        params = {
            'limit': limit
        }

        print(f"Anfrage wird an {reports_url} gesendet...")

        try:
            response = requests.get(reports_url, headers=self.headers, params=params)
            response.raise_for_status()  # Löst eine Ausnahme für HTTP-Fehler aus

            print("Anfrage erfolgreich! Status Code:", response.status_code)
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP-Fehler aufgetreten: {http_err}")
            print(f"Antwort-Body: {response.text}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Netzwerk-Fehler aufgetreten: {req_err}")
            return None

    def create_report(self, damage_report):
        """
        Erstellt ein neues Gutachten in autoiXpert basierend auf einem DamageReport-Objekt.
        Bilder werden hierbei noch nicht berücksichtigt.

        :param damage_report: Eine Instanz Ihres Django-Models `DamageReport`.
        :return: Das JSON-Objekt des neu erstellten Gutachtens oder None bei einem Fehler.
        """

        address_data = complete_address(damage_report.address)
        formatted_accident_location = complete_address(damage_report.accident_location)
        workshop_address_data = complete_address(f"{damage_report.workshop.address} {damage_report.workshop.plz} {damage_report.workshop.city}")

        # --- Schritt 1: Daten aus Ihrem Model in das API-Format mappen ---
        payload = {
            # Pflichtfelder für die API
            "type": "liability",  # Beispiel: Haftpflichtschaden. Passen Sie dies bei Bedarf an.
            "responsible_assessor": self.responsible_assessor_id,

            # Mapping der weiteren Felder
            "claimant": {
                "organization_name": damage_report.company_name if damage_report.person_or_company == 'company' else "",
                "first_name": damage_report.first_name,
                "last_name": damage_report.last_name,
                "street_and_housenumber_or_lockbox": f'{address_data["street"]} {address_data["street_number"]}' if address_data["address_corrected"] else address_data["formatted_address"],
                "zip": address_data["postal_code"] if address_data["address_corrected"] else "",
                "city": address_data["city"] if address_data["address_corrected"] else "",
                "email": damage_report.email,
                "phone": damage_report.phone_number,
                "iban": damage_report.iban
            },
            "visits": [
                {
                    "location_name": damage_report.workshop.workshop_name,
                    "street": f'{workshop_address_data["street"]} {workshop_address_data["street_number"]}' if workshop_address_data["address_corrected"] else workshop_address_data["formatted_address"],
                    "zip": workshop_address_data["postal_code"] if workshop_address_data["address_corrected"] else "",
                    "city": workshop_address_data["city"] if workshop_address_data["address_corrected"] else "",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "dateTime": datetime.now(tz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                }
            ],
            "car": {
                "license_plate": damage_report.plate_number,
                "next_general_inspection_date": damage_report.inspection_string
            },
            "accident": {
                "location": formatted_accident_location["formatted_address"],
                # Konvertiert das Python-datetime-Objekt in einen ISO 8601 String
                "date": damage_report.accident_datetime.strftime("%Y-%m-%d") if damage_report.accident_datetime else None,
                "time": "2020-11-18T15:01:31.667Z",
                # "time": "08:30:00.000Z",
                "circumstances": damage_report.accident_notes_string
            },
            "author_of_damage": {
                "license_plate": damage_report.opponent_plate_number,
                "insurance_number": damage_report.opponent_insurance_number
            },
            "insurance": {
                "case_number": damage_report.damage_number
            },
            "garage": {
                "first_name": damage_report.workshop.primary_contact.split(" ")[0],
                "last_name": damage_report.workshop.primary_contact.split(" ")[-1],
                "organization_name": damage_report.workshop.workshop_name,
                "email": damage_report.workshop.email,
                "phone": damage_report.workshop.phone_number,
                "street_and_housenumber_or_lockbox": f'{workshop_address_data["street"]} {workshop_address_data["street_number"]}' if workshop_address_data["address_corrected"] else workshop_address_data["formatted_address"],
                "zip": workshop_address_data["postal_code"] if workshop_address_data["address_corrected"] else "",
                "city": workshop_address_data["city"] if workshop_address_data["address_corrected"] else "",
            },

            # Felder, die kein direktes Gegenstück haben, werden als "Eigene Felder" (custom_fields) gemappt
            # Diese müssen vorher in der autoiXpert-Oberfläche angelegt worden sein!
            # "custom_fields": {
            #     "Scheckheft vorhanden": damage_report.checkbook_exists,
            #     "Geleast": damage_report.leased,
            #     "Finanziert": damage_report.financed,
            #     "Gibt es Zeugen?": damage_report.has_witnesses,
            #     "Zeugen": damage_report.witness_textfield
            # }
        }

        # --- Schritt 2: API-Anfrage senden ---
        report_url = f"{self.base_url}/reports"

        try:
            response = requests.post(report_url, headers=self.headers, data=json.dumps(payload, default=str))
            response.raise_for_status()

            print("Gutachten erfolgreich erstellt!")
            created_report = response.json()

            # Die ID des erstellten Gutachtens ist wichtig für weitere Schritte (z.B. Bildupload)
            print(f"Neue Gutachten-ID: {created_report.get('report', {}).get('id')}")

            return created_report

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP-Fehler beim Erstellen des Gutachtens: {http_err}")
            print(f"Status Code: {http_err.response.status_code}")
            print(f"Antwort-Body: {http_err.response.text}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Netzwerk-Fehler aufgetreten: {req_err}")
            return None

    def upload_report_photo(self, report_id: str, damage_image_obj):
        """
        Lädt ein Bild zu einem bestehenden Gutachten hoch, basierend auf einem DamageImage-Objekt.

        Dieser Vorgang besteht aus zwei Schritten:
        1. Anlegen der Bild-Metadaten, um eine Upload-URL zu erhalten.
        2. Hochladen der eigentlichen Bilddatei an die erhaltene Upload-URL.

        :param report_id: Die ID des Gutachtens, zu dem das Bild hochgeladen werden soll.
        :param damage_image_obj: Eine Instanz Ihres Django-Models `DamageImage`.
        :return: Das JSON-Objekt des hochgeladenen Bildes oder None bei einem Fehler.
        """
        # Pfad zur Bilddatei aus dem Django ImageField
        photo_path = damage_image_obj.image.path

        # Den angezeigten Namen der Bildansicht für den Titel verwenden
        # Falls image_view nicht in CHOICES ist, wird der raw-Wert genommen
        image_view_display = dict(damage_image_obj.IMAGE_TYPE_CHOICES).get(
            damage_image_obj.image_view, damage_image_obj.image_view
        )

        # Titel des Bildes im autoiXpert System (kann angepasst werden)
        title = f"{damage_image_obj.damage_report.plate_number} - {image_view_display}"
        original_name = os.path.basename(photo_path)  # Dateiname extrahieren
        description = str(image_view_display) + " - " + original_name

        print(f"Beginne Upload des Bildes '{original_name}' für Gutachten-ID: {report_id}")

        # Schritt 1: Bild-Metadaten anlegen und Upload-URL anfordern
        photo_metadata_url = f"{self.base_url}/reports/{report_id}/photos"

        metadata_payload = {
            "title": title,
            "description": description,
            "original_name": original_name,
            "included_in_report": True,  # Annahme: Bilder sollen im Bericht enthalten sein
            "included_in_residual_value_exchange": False,
            "included_in_repair_confirmation": False,
            "included_in_expert_statement": False
        }

        try:
            # Sende POST-Anfrage, um Metadaten zu erstellen
            response_metadata = requests.post(
                photo_metadata_url,
                headers=self.headers,
                data=json.dumps(metadata_payload)
            )
            response_metadata.raise_for_status()  # Löst Ausnahme für HTTP-Fehler

            photo_data = response_metadata.json().get('photo')
            if not photo_data:
                print("Fehler: Keine Bilddaten in der Metadaten-Antwort gefunden.")
                return None

            photo_id = photo_data.get('id')
            upload_url_request_url = f"{self.base_url}/reports/{report_id}/photos/{photo_id}/upload"

            print(f"Metadaten für Bild {photo_id} erfolgreich erstellt. Fordere Upload-URL an...")

            # Schritt 2a: Upload-URL für die Bilddatei anfordern
            # Beachten Sie: Hier wird kein JSON im Header gesendet, nur der Auth-Header
            response_upload_url = requests.get(
                upload_url_request_url,
                headers={"Authorization": f"Bearer {self.key}"}
            )
            response_upload_url.raise_for_status()

            upload_response_data = response_upload_url.json()
            s3_upload_url = upload_response_data.get('upload_url')

            if not s3_upload_url:
                print("Fehler: Keine Upload-URL erhalten.")
                return None

            print(f"Upload-URL für Bild {photo_id} erhalten. Lade Datei hoch...")

            # Schritt 2b: Bilddatei an die signierte S3-URL hochladen
            mime_type, _ = mimetypes.guess_type(photo_path)
            if not mime_type:
                mime_type = 'application/octet-stream'  # Fallback

            with open(photo_path, 'rb') as f:
                photo_content = f.read()

            upload_headers = {
                'Content-Type': mime_type,
                'Content-Length': str(len(photo_content))
            }
            # Der Authorization-Header wird hier nicht benötigt, da die S3-URL bereits signiert ist.
            response_s3_upload = requests.put(s3_upload_url, data=photo_content, headers=upload_headers)
            response_s3_upload.raise_for_status()  # Löst Ausnahme für HTTP-Fehler

            print(f"Bilddatei '{original_name}' erfolgreich für Gutachten-ID {report_id} hochgeladen.")

            # Optional: Die Autoixpert-ID des Bildes im Django-Modell speichern
            # damage_image_obj.autoixpert_photo_id = photo_id # Annahme: Sie haben dieses Feld im DamageImage-Modell
            # damage_image_obj.save()

            return photo_data  # Rückgabe der Bild-Metadaten des hochgeladenen Bildes

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP-Fehler beim Hochladen des Bildes: {http_err}")
            if http_err.response is not None:
                print(f"Antwort-Body: {http_err.response.text}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Netzwerk-Fehler aufgetreten: {req_err}")
            return None
        except FileNotFoundError:
            print(f"Fehler: Die Datei '{photo_path}' wurde nicht gefunden.")
            return None
        except Exception as e:
            print(f"Ein unerwarteter Fehler beim Bild-Upload ist aufgetreten: {e}")
            return None

    def update_report(self, report_id: str, damage_report):
        """
        Aktualisiert ein bestehendes Gutachten in autoiXpert.
        """
        if not report_id:
            print("Fehler: Es wurde keine report_id für die Aktualisierung übergeben.")
            return None

        address_data = complete_address(damage_report.address)
        formatted_accident_location = complete_address(damage_report.accident_location)
        workshop_address_data = complete_address(f"{damage_report.workshop.address} {damage_report.workshop.plz} {damage_report.workshop.city}")

        # --- Schritt 1: Daten aus Ihrem Model in das API-Format mappen ---
        payload = {
            # Mapping der weiteren Felder
            "claimant": {
                "organization_name": damage_report.company_name if damage_report.person_or_company == 'company' else "",
                "first_name": damage_report.first_name,
                "last_name": damage_report.last_name,
                "street_and_housenumber_or_lockbox": f'{address_data["street"]} {address_data["street_number"]}' if address_data["address_corrected"] else address_data["formatted_address"],
                "zip": address_data["postal_code"] if address_data["address_corrected"] else "",
                "city": address_data["city"] if address_data["address_corrected"] else "",
                "email": damage_report.email,
                "phone": damage_report.phone_number,
                "iban": damage_report.iban
            },
            "car": {
                "license_plate": damage_report.plate_number,
                # inspection format is = mm/yyyy
                "next_general_inspection_date": damage_report.inspection_string
            },
            "accident": {
                "location": formatted_accident_location["formatted_address"],
                # Konvertiert das Python-datetime-Objekt in einen ISO 8601 String
                "date": damage_report.accident_datetime.strftime("%Y-%m-%d") if damage_report.accident_datetime else None,
                "time": "2020-11-18T15:01:31.667Z",
                # "time": "08:30:00.000Z",
                "circumstances": damage_report.accident_notes_string
            },
            "author_of_damage": {
                "license_plate": damage_report.opponent_plate_number,
                "insurance_number": damage_report.opponent_insurance_number
            },
            "insurance": {
                "case_number": damage_report.damage_number
            },

            # Felder, die kein direktes Gegenstück haben, werden als "Eigene Felder" (custom_fields) gemappt
            # Diese müssen vorher in der autoiXpert-Oberfläche angelegt worden sein!
            # "custom_fields": {
            #     "Scheckheft vorhanden": damage_report.checkbook_exists,
            #     "Geleast": damage_report.leased,
            #     "Finanziert": damage_report.financed,
            #     "Gibt es Zeugen?": damage_report.has_witnesses,
            #     "Zeugen": damage_report.witness_textfield
            # }
        }

        report_url = f"{self.base_url}/reports/{report_id}"
        print(f"Sende PATCH-Anfrage an {report_url}...")

        try:

            # Wir senden die Anfrage mit den zu aktualisierenden Daten.
            # json.dumps wandelt das Python-Dict in einen JSON-String um.
            response = requests.patch(
                report_url,
                headers=self.headers,
                data=json.dumps(payload, default=str)
            )
            response.raise_for_status()  # Löst eine Ausnahme für HTTP-Fehler aus

            print(f"Gutachten {report_id} erfolgreich aktualisiert!")
            return response

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP-Fehler beim Aktualisieren des Gutachtens: {http_err}")
            print(f"Status Code: {http_err.response.status_code}")
            print(f"Antwort-Body: {http_err.response.text}")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Netzwerk-Fehler aufgetreten: {req_err}")
            return None
