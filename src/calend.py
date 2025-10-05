import datetime
import os.path
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_calendar_dataclasses import CalendarEvents, CalendarListEntry

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    # "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/forms.body",
]

from pathlib import Path
import os

cred_path = (
    Path(os.getcwd()) / ".." / "client_secret.apps.googleusercontent.com.json"
).resolve()


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        calendar = CalendarListEntry.from_dict(
            service.calendarList()
            .get(
            )
            .execute()
        )

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        # print("Getting the upcoming 10 events")
        events_result: CalendarEvents = (
            service.events()
            .list(
                calendarId=calendar.id,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        pprint(events_result)
        events = events_result.get("items", [])

        service.events().insert(
                calendarId=calendar.id
        )

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            # pprint(event)
            start = event["start"].get("dateTime", event["start"].get("date"))
            # print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
