
from typing import List, Dict
from caldav import DAVClient
from datetime import date, datetime, timedelta

from library.config import quit_on_fatal, read_config
from library.telebot import send_text


CONFIG: dict | None = None


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
) -> List[Dict[str, str | datetime | timedelta | bool]]:
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

    event_collect = []

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

            event_collect.append({
                'uid': uid,
                'title': summary,
                'start': start,
                'end': end,
                'duration': duration,
                'whole_day': whole_day,
                'source': calendar_name,
            })

    return event_collect

init_config()
