
from typing import List, Dict
from calendav import DAVClient
from datetime import date, datetime, timedelta, timezone

from library.calendar_event import CalendarEvent
from library.config import quit_on_fatal, read_config


CONFIG: dict | None = None


def get_local_tz() -> timezone:
    return timezone(timedelta(hours=8))


def get_local_now() -> datetime:
    return datetime.now(tz=get_local_tz())


def get_local_today() -> datetime:
    return get_local_now().replace(hour=0, minute=0, second=0, microsecond=0)


def init_config() -> None:
    global CONFIG

    config_template = {
        'calendar_ap': None,
        'username': None,
        'password': None,
        'calendars': None,
    }

    config = read_config(
        'webdav.yml',
        config_template,
    )

    if config is None:
        quit_on_fatal()
        return

    CONFIG = config


def fetch_events(
    filter_start_date: datetime,
    filter_end_date: datetime,
) -> List[CalendarEvent]:
    global CONFIG

    client = DAVClient(
        CONFIG.get('calendar_ap'),
        username=CONFIG.get('username'),
        password=CONFIG.get('password'),
    )

    calendars = [
        cal
        for cal in client.principal().get_calendars()
        if (
            len(CONFIG.get('calendars')) == 0 or
            cal.get_display_name() in CONFIG.get('calendars')
        )
    ]

    event_collect: List[CalendarEvent] = []

    for calendar in calendars:
        calendar_name = calendar.get_display_name()

        calendar_events = calendar.search(
            start=filter_start_date,
            end=filter_end_date,
            event=True,
            expand=True,
        )

        calendar_events.reverse()

        for calendar_event in calendar_events:
            v_event = calendar_event.get_icalendar_component()

            uid = v_event.uid
            summary = v_event.summary
            duration = v_event.duration
            start = v_event.start
            end = v_event.end
            whole_day = type(start) is date and type(end) is date

            if whole_day:
                end -= timedelta(days=1)

            event_collect.append(CalendarEvent(
                uid,
                summary,
                start,
                end,
                duration,
                whole_day,
                calendar_name,
            ))

    return event_collect


init_config()
