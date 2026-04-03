
from datetime import date, datetime, time, timedelta
from threading import Thread
from time import sleep
from typing import List, Tuple
from os import environ
import sys

from library.caldav import fetch_events, get_local_now, get_local_tz
from library.calendar_event import CalendarEvent
from library.telebot import send_text


# constants
WEEKDAY_TO_LOCALE = ['一', '二' , '三', '四', '五', '六', '日']
NOTIFY_COMING_EVENT_BEFORE_SEC = (
    int(env_value)
    if (
        (env_value := environ.get('CALENDAR_NOTIFY_COMING_EVENT_BEFORE_SEC')) and
        env_value.isdigit()
    )
    else
    900  # 15 mins
)


# global variables
NOTIFY_COMING_THREAD: Thread | None = None
NOTIFY_COMING_SENT: List[str] = []


def weekday_to_locale(obj: datetime | date) -> str:
    return WEEKDAY_TO_LOCALE[obj.weekday()]


def format_date(raw: date) -> str:
    return raw.strftime(f"%Y-%m-%d({weekday_to_locale(raw)})")


def format_datetime(raw: datetime) -> str:
    return raw.strftime(f"%Y-%m-%d({weekday_to_locale(raw)}) %p %I:%M:%S")


def format_d_or_dt(
    raw: date | datetime,
    as_date: bool,
) -> str:
    if as_date:
        return format_date(
            raw
            if type(raw) is date
            else
            raw.date()
        )

    return format_datetime(
        raw
        if type(raw) is datetime
        else
        datetime.combine(raw, time())
    )


def format_duration(raw, as_days: bool) -> str:
    if as_days:
        return f"{raw.days}天"

    days = raw.days
    hours = raw.seconds // 3600
    minutes = (raw.seconds - hours * 3600) // 60

    if days:
        return f"{days}天 {hours}時 {minutes}分"
    elif hours:
        return f"{hours}時 {minutes}分"

    return f"{minutes}分"


def date_range_to_datetime_range(
    start: date,
    end: date,
) -> Tuple[datetime, datetime]:
    return (
        datetime.combine(start, time(0, 0, 0), tzinfo=get_local_tz()),
        datetime.combine(end, time(23, 59, 59), tzinfo=get_local_tz()),
    )


def send_events_notifications(
    events: List[CalendarEvent],
    texts: List[str] | str | None = None,
) -> None:
    if len(events) == 0:
        return

    if isinstance(texts, str):
        send_text(texts)
    elif isinstance(texts, list):
        for text in texts:
            send_text(text)

    for event in events:
        event_whole_day = event.whole_day

        send_text(f'''
📔 {event.title}
 - 起始於 {format_d_or_dt(event.start, event_whole_day)}
 - 結束於 {format_d_or_dt(event.end, event_whole_day)}
 - 總計時長 {format_duration(event.duration, event_whole_day)}
 - 登記於 {event.calendar_name} 日曆
''')


def notify_next_week() -> None:
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=6)

    send_events_notifications(
        fetch_events(*date_range_to_datetime_range(start, end)),
        f"⏰ 下週 {format_date(start)} - {format_date(end)} 的待辦行程",
    )


def notify_today() -> None:
    today = date.today()

    send_events_notifications(
        fetch_events(*date_range_to_datetime_range(today, today)),
        f"⏰ 今天 {format_date(today)} 的行程",
    )


def notify_coming() -> None:
    global NOTIFY_COMING_THREAD, NOTIFY_COMING_SENT

    if NOTIFY_COMING_THREAD is not None:
        # thread is already running
        return

    NOTIFY_COMING_THREAD = Thread(
        target=notify_coming_runner,
        args=(NOTIFY_COMING_SENT,),
    )

    assert(NOTIFY_COMING_THREAD is not None)

    NOTIFY_COMING_THREAD.start()


def notify_coming_runner(sent_list: List[str]) -> None:
    print(f"Notify up coming events before {NOTIFY_COMING_EVENT_BEFORE_SEC} seconds")

    while True:
        start = get_local_now()
        end = (
            start +
            timedelta(seconds=NOTIFY_COMING_EVENT_BEFORE_SEC)
        )

        events = [
            event
            for event in fetch_events(start, end)
            if event.uid not in sent_list
        ]

        sent_list.extend([event.uid for event in events])

        send_events_notifications(
            events,
            '⏰ 以下行程即將到來',
        )

        sleep(30)


def notify_what() -> str:
    if len(sys.argv) != 2:
        return ''

    return sys.argv[1].strip().lower()
