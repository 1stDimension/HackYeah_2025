import os
from typing import Any
from faker import Faker
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import jsonl
import random
from datetime import datetime, timedelta
import pytz

# If modifying these SCOPES, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/forms.body",
]

from pathlib import Path

cred_path = (
    Path(os.getcwd()) / ".." / "client_secret.apps.googleusercontent.com.json"
).resolve()

CALENDAR_ID = os.environ.get("CALENDAR_ID", "primary")


def get_credentials(c_path: os.PathLike):
    """Gets user credentials from a local file."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(c_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def create_or_update_form(
    title: str, bodies: list[dict[str, Any]], form_id_file="form_id.txt"
):
    """Creates a new Google Form or updates an existing one."""
    creds = get_credentials(cred_path)
    form_service = build("forms", "v1", credentials=creds)
    form_id = None

    if os.path.exists(form_id_file):
        with open(form_id_file, "r") as f:
            form_id = f.read().strip()

    if form_id:
        try:
            form = form_service.forms().get(formId=form_id).execute()
            print(f"Form {form_id} already exists. Updating it.")

            # Clear existing questions
            items = form.get("items", [])
            requests = []
            if items:
                for _ in range(len(items)):
                    requests.append({"deleteItem": {"location": {"index": 0}}})

            # Update title
            requests.append(
                {"updateFormInfo": {"info": {"title": title}, "updateMask": "title"}}
            )

            if requests:
                form_service.forms().batchUpdate(
                    formId=form_id, body={"requests": requests}
                ).execute()

            # Add new questions
            requests = []
            for i, body in enumerate(bodies):
                requests.append(
                    {
                        "createItem": {
                            "item": {
                                "title": body["title"],
                                "questionItem": {
                                    "question": {
                                        "required": body.get("required", False),
                                        "textQuestion": {
                                            "paragraph": body.get("paragraph", False)
                                        },
                                    }
                                },
                            },
                            "location": {"index": i},
                        }
                    }
                )

            if requests:
                form_service.forms().batchUpdate(
                    formId=form_id, body={"requests": requests}
                ).execute()

            return form["responderUri"]
        except HttpError as e:
            if e.resp.status == 404:
                print("Form not found. Creating a new one.")
                form_id = None
            else:
                raise e

    if not form_id:
        form = {"info": {"title": title}}
        new_form = form_service.forms().create(body=form).execute()
        form_id = new_form["formId"]

        with open(form_id_file, "w") as f:
            f.write(form_id)

        requests = []
        for i, body in enumerate(bodies):
            requests.append(
                {
                    "createItem": {
                        "item": {
                            "title": body["title"],
                            "questionItem": {
                                "question": {
                                    "required": body.get("required", False),
                                    "textQuestion": {
                                        "paragraph": body.get("paragraph", False)
                                    },
                                }
                            },
                        },
                        "location": {"index": i},
                    }
                }
            )

        if requests:
            question_setting = {"requests": requests}
            form_service.forms().batchUpdate(
                formId=form_id, body=question_setting
            ).execute()

        return new_form["responderUri"]


def create_or_update_event(calendar_service, calendar_id, event_data, event_id_file):
    """Creates a new Google Calendar event or updates an existing one and returns its ID."""
    event_id = None
    if os.path.exists(event_id_file):
        with open(event_id_file, "r") as f:
            event_id = f.read().strip()

    event_body = {
        "summary": event_data["title"],
        "description": event_data["description"],
        "start": {
            "dateTime": event_data["start_date"],
            "timeZone": "Europe/Warsaw",
        },
        "end": {
            "dateTime": event_data["end_date"],
            "timeZone": "Europe/Warsaw",
        },
    }

    try:
        if event_id:
            updated_event = (
                calendar_service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event_body)
                .execute()
            )
            print(f"Event {updated_event['id']} updated.")
            return updated_event["id"]
        else:
            new_event = (
                calendar_service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )
            event_id = new_event["id"]
            with open(event_id_file, "w") as f:
                f.write(event_id)
            print(f"Event {event_id} created.")
            return event_id
    except HttpError as e:
        if e.resp.status == 404:
            print("Event not found, creating a new one.")
            new_event = (
                calendar_service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )
            event_id = new_event["id"]
            with open(event_id_file, "w") as f:
                f.write(event_id)
            print(f"Event {event_id} created.")
            return event_id
        else:
            raise e


if __name__ == "__main__":
    creds = get_credentials(cred_path)
    calendar_service = build("calendar", "v3", credentials=creds)

    fake = Faker("pl_PL")
    warsaw_tz = pytz.timezone("Europe/Warsaw")

    base_questions = [
        {"title": "Jak masz na imię?", "required": True},
        {"title": "Ile masz lat?"},
        {"title": "Jaki jest Twój adres e-mail?", "required": True},
    ]

    form_types = {
        "Wolontariat": {
            "title_template": "Aplikacja na wolontariat: {}",
            "questions": [
                {
                    "title": "Dlaczego chcesz być wolontariuszem w naszej organizacji?",
                    "paragraph": True,
                    "required": True,
                },
                {
                    "title": "Jakie umiejętności możesz wnieść do naszego zespołu?",
                    "paragraph": True,
                },
            ],
        },
        "Staż": {
            "title_template": "Aplikacja na staż: {}",
            "questions": [
                {"title": "Jakie jest Twoje pole studiów?", "required": True},
                {
                    "title": "Proszę wymienić swoje umiejętności i doświadczenie.",
                    "paragraph": True,
                },
                {
                    "title": "Jakie są Twoje cele zawodowe?",
                    "paragraph": True,
                    "required": True,
                },
            ],
        },
        "Praca": {
            "title_template": "Aplikacja o pracę: {}",
            "questions": [
                {
                    "title": "Jakie jest Twoje doświadczenie zawodowe?",
                    "paragraph": True,
                    "required": True,
                },
                {"title": "Jakie są Twoje oczekiwania finansowe?", "required": True},
                {
                    "title": "Dlaczego chcesz pracować w naszej firmie?",
                    "paragraph": True,
                },
            ],
        },
        "Praktyki": {
            "title_template": "Aplikacja na praktyki: {}",
            "questions": [
                {
                    "title": "W jakiej dziedzinie chciałbyś/chciałabyś odbyć praktyki?",
                    "required": True,
                },
                {"title": "Jaki jest Twój poziom znajomości języka angielskiego?"},
                {"title": "Czy posiadasz własny laptop?", "required": True},
            ],
        },
        "Wolontariat w schronisku dla zwierząt": {
            "title_template": "Wolontariat w schronisku dla zwierząt",
            "questions": [
                {
                    "title": "Czy masz doświadczenie w pracy ze zwierzętami?",
                    "paragraph": True,
                },
                {
                    "title": "Czy jesteś alergikiem? Jeśli tak, na co?",
                    "paragraph": True,
                },
                {
                    "title": "W jakie dni i w jakich godzinach jesteś dyspozycyjny/a?",
                    "paragraph": True,
                    "required": True,
                },
                {
                    "title": "Czy masz jakieś obawy przed pracą ze zwierzętami po przejściach?",
                    "paragraph": True,
                },
            ],
        },
    }

    output_file = "forms.jsonl"
    with open(output_file, "w") as f:
        pass

    created_event_ids = []

    form_keys = list(form_types.keys())
    forms_to_create = random.choices(form_keys[:-1], k=10) + [
        "Wolontariat w schronisku dla zwierząt"
    ]
    random.shuffle(forms_to_create)

    regular_form_counter = 0
    for form_key in forms_to_create:
        form_details = form_types[form_key]
        job_title = fake.job()

        if "{}" in form_details["title_template"]:
            form_title = form_details["title_template"].format(job_title)
        else:
            form_title = form_details["title_template"]

        additional_questions = form_details["questions"]
        all_questions = base_questions + additional_questions

        if form_key == "Wolontariat w schronisku dla zwierząt":
            form_id_file = "form_id_animal_shelter.txt"
            event_id_file = "event_id_animal_shelter.txt"
        else:
            form_id_file = f"form_id_{regular_form_counter}.txt"
            event_id_file = f"event_id_{regular_form_counter}.txt"
            regular_form_counter += 1

        form_url = create_or_update_form(form_title, all_questions, form_id_file)

        start_date = datetime.now(warsaw_tz) + timedelta(days=random.randint(7, 30))
        end_date = start_date + timedelta(days=random.randint(60, 120))

        description = (
            f"To jest formularz aplikacyjny na: {form_title}. "
            f"{fake.paragraph(nb_sentences=2)}"
        )

        form_data = {
            "url": form_url,
            "title": form_title,
            "description": description,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        jsonl.add(form_data, output_file)
        print(f"Appended data for '{form_title}' to {output_file}")

        event_id = create_or_update_event(
            calendar_service, CALENDAR_ID, form_data, event_id_file
        )
        if event_id:
            created_event_ids.append(event_id)

    # Add attendee to all created events
    attendee_email = "enter@example.com"
    print(f"\nAdding {attendee_email} to all created events...")
    for event_id in created_event_ids:
        if not event_id:
            continue
        try:
            event = (
                calendar_service.events()
                .get(calendarId=CALENDAR_ID, eventId=event_id)
                .execute()
            )
            attendees = event.get("attendees", [])
            # Check if attendee already exists
            if not any(att["email"] == attendee_email for att in attendees):
                attendees.append({"email": attendee_email})
                body = {"attendees": attendees}
                calendar_service.events().patch(
                    calendarId=CALENDAR_ID,
                    eventId=event_id,
                    body=body,
                    sendUpdates="all",
                ).execute()
                print(f"  - Added attendee to event {event_id}")
            else:
                print(f"  - Attendee already exists in event {event_id}")
        except HttpError as e:
            print(f"  - Failed to add attendee to event {event_id}: {e}")
