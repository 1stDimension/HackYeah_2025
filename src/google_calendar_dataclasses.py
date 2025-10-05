from dataclasses import dataclass, field
from typing import List, Optional, Any

# This file contains dataclasses that model the JSON response structure
# from the Google Calendar API for a list of events.

@dataclass
class DefaultReminder:
    """Represents a default reminder for the calendar."""
    method: str
    minutes: int

@dataclass
class Creator:
    """Represents the creator of an event."""
    email: str
    self: Optional[bool] = None

@dataclass
class EventDateTime:
    """Represents the start or end time of an event."""
    dateTime: str
    timeZone: str

@dataclass
class Organizer:
    """Represents the organizer of an event."""
    email: str
    self: Optional[bool] = None

@dataclass
class Reminders:
    """Represents reminder settings for an event."""
    useDefault: bool

@dataclass
class Attendee:
    """Represents an attendee of an event."""
    email: str
    responseStatus: str
    displayName: Optional[str] = None
    organizer: Optional[bool] = None
    self: Optional[bool] = None

@dataclass
class EventItem:
    """Represents a single event item in the calendar."""
    kind: str
    etag: str
    _id: str
    status: str
    htmlLink: str
    created: str
    updated: str
    summary: str
    creator: Creator
    organizer: Organizer
    start: EventDateTime
    end: EventDateTime
    iCalUID: str
    sequence: int
    reminders: Reminders
    eventType: str
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[Attendee] = field(default_factory=list)
    guestsCanInviteOthers: Optional[bool] = None
    guestsCanSeeOtherGuests: Optional[bool] = None


@dataclass
class CalendarEvents:
    """Represents the top-level structure for a list of calendar events."""
    kind: str
    etag: str
    summary: str
    updated: str
    timeZone: str
    accessRole: str
    description: Optional[str] = None
    defaultReminders: List[DefaultReminder] = field(default_factory=list)
    items: List[EventItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a CalendarEvents object from a dictionary."""
        items_data = data.get('items', [])
        items = [EventItem(
            attendees=[Attendee(**attendee) for attendee in item.get('attendees', [])],
            creator=Creator(**item.get('creator', {})),
            organizer=Organizer(**item.get('organizer', {})),
            start=EventDateTime(**item.get('start', {})),
            end=EventDateTime(**item.get('end', {})),
            reminders=Reminders(**item.get('reminders', {})),
            **{k: v for k, v in item.items() if k not in ['attendees', 'creator', 'organizer', 'start', 'end', 'reminders']}
        ) for item in items_data]

        default_reminders_data = data.get('defaultReminders', [])
        default_reminders = [DefaultReminder(**reminder) for reminder in default_reminders_data]

        return cls(
            items=items,
            defaultReminders=default_reminders,
            **{k: v for k, v in data.items() if k not in ['items', 'defaultReminders']}
        )

@dataclass
class ConferenceProperties:
    """Represents the conference properties for the calendar."""
    allowedConferenceSolutionTypes: List[str]

@dataclass
class CalendarListEntry:
    """Represents a single entry from a user's calendar list."""
    kind: str
    etag: str
    id: str
    summary: str
    timeZone: str
    colorId: str
    backgroundColor: str
    foregroundColor: str
    accessRole: str
    conferenceProperties: ConferenceProperties
    defaultReminders: List[Any] = field(default_factory=list) # Using Any since it's empty in the example

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a CalendarListEntry object from a dictionary."""
        conference_props_data = data.get('conferenceProperties', {})
        conference_props = ConferenceProperties(**conference_props_data)

        return cls(
            conferenceProperties=conference_props,
            **{k: v for k, v in data.items() if k != 'conferenceProperties'}
        )
