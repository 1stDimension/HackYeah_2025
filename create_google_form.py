import os
from typing import Any
from faker import Faker
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import jsonl
from src.google_calendar_dataclasses import CalendarListEntry

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/forms.body"]

from pathlib import Path
import os

cred_path = (
    Path(os.getcwd()) / ".." / "client_secret.apps.googleusercontent.com.json"
).resolve()

CALENDAR_ID = os.environ["CALENDAR_ID"]

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

        question_setting = {"requests": requests}
        form_service.forms().batchUpdate(
            formId=form_id, body=question_setting
        ).execute()

        return new_form["responderUri"]


if __name__ == "__main__":
    creds = get_credentials(cred_path)
    calendarService = build("calendar", "v3", credentials=creds)
    calendar = CalendarListEntry.from_dict(
        calendarService.calendarList()
        .get(
            calendarId=CALENDAR_ID
        )
        .execute()
    )
    
    # Please install pytz and Faker if you haven't already: pip install pytz Faker
    import random
    from datetime import datetime, timedelta
    import pytz

    fake = Faker("pl_PL")
    warsaw_tz = pytz.timezone("Europe/Warsaw")

    base_questions = [
        {"title": "Jak masz na imię?", "required": True},
        {"title": "Ile masz lat?"},
        {"title": "Jaki jest Twój adres e-mail?", "required": True},
    ]

    output_file = "forms.jsonl"
    # Clear the file at the beginning of the run
    with open(output_file, "w") as f:
        pass

    for i in range(10):
        form_type = random.choice(["Wolontariat", "Staż"])

        job_title = fake.job()
        if form_type == "Wolontariat":
            form_title = f"Aplikacja na wolontariat: {job_title}"
            additional_questions = [
                {
                    "title": "Dlaczego chcesz być wolontariuszem w naszej organizacji?",
                    "paragraph": True,
                    "required": True,
                },
                {
                    "title": "Jakie umiejętności możesz wnieść do naszego zespołu?",
                    "paragraph": True,
                },
            ]
        else:  # Staż
            form_title = f"Aplikacja na staż: {job_title}"
            additional_questions = [
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
            ]

        all_questions = base_questions + additional_questions

        form_id_file = f"form_id_{i}.txt"
        form_url = create_or_update_form(form_title, all_questions, form_id_file)

        start_date = datetime.now(warsaw_tz) + timedelta(days=random.randint(7, 30))
        end_date = start_date + timedelta(days=random.randint(60, 120))

        form_data = {
            "url": form_url,
            "description": f"To jest formularz aplikacyjny na: {form_title}",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        jsonl.add(form_data, output_file)
        print(f"Appended data for '{form_title}' to {output_file}")

    # Form for animal shelter
    form_title_shelter = "Wolontariat w schronisku dla zwierząt"
    animal_shelter_questions = [
        {"title": "Czy masz doświadczenie w pracy ze zwierzętami?", "paragraph": True},
        {"title": "Czy jesteś alergikiem? Jeśli tak, na co?", "paragraph": True},
        {
            "title": "W jakie dni i w jakich godzinach jesteś dyspozycyjny/a?",
            "paragraph": True,
            "required": True,
        },
        {
            "title": "Czy masz jakieś obawy przed pracą ze zwierzętami po przejściach?",
            "paragraph": True,
        },
    ]
    all_questions_shelter = base_questions + animal_shelter_questions

    form_id_file_shelter = "form_id_animal_shelter.txt"
    form_url_shelter = create_or_update_form(
        form_title_shelter, all_questions_shelter, form_id_file_shelter
    )

    start_date_shelter = datetime.now(warsaw_tz) + timedelta(days=random.randint(7, 30))
    end_date_shelter = start_date_shelter + timedelta(days=random.randint(60, 120))

    form_data_shelter = {
        "url": form_url_shelter,
        "description": "To jest formularz dla wolontariuszy w schronisku dla zwierząt.",
        "start_date": start_date_shelter.isoformat(),
        "end_date": end_date_shelter.isoformat(),
    }

    jsonl.add(form_data_shelter, output_file)
    print(f"Appended data for '{form_title_shelter}' to {output_file}")
