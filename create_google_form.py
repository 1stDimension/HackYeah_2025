
import os
from typing import Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/forms.body"]

from pathlib import Path
import os

cred_path = (
    Path(os.getcwd()) / ".." / "client_secret.apps.googleusercontent.com.json"
).resolve()

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

def create_or_update_form(title: str, bodies: list[dict[str, Any]], form_id_file="form_id.txt"):
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
            requests.append({
                "updateFormInfo": {
                    "info": {"title": title},
                    "updateMask": "title"
                }
            })

            form_service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

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
                                        "textQuestion": {"paragraph": body.get("paragraph", False)},
                                    }
                                },
                            },
                            "location": {"index": i},
                        }
                    }
                )
            
            form_service.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
            
            print(f"Form updated successfully! View it at: {form['responderUri']}")
            return form['responderUri']

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
                                    "textQuestion": {"paragraph": body.get("paragraph", False)},
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

        print(f"Form created successfully! View it at: {new_form['responderUri']}")
        return new_form['responderUri']

if __name__ == "__main__":
    form_title = "My Awesome Form"
    fake_bodies = [
        {"title": "What is your name?", "required": True},
        {"title": "How old are you"},
        {"title": "What is your email address?", "required": True},
    ]
    create_or_update_form(form_title, fake_bodies)
