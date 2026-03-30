
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Tuple
import sys

from library.caldav import fetch_events, get_local_now, get_local_tz
from library.telebot import send_text


WEEKDAY_TO_LOCALE = ['一', '二' , '三', '四', '五', '六', '日']
NOTIFY_COMING_EVENT_BEFORE_SEC = 900  # 15 mins


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


def is_event_start(
    cmp_point: date | datetime,
    event_start: date | datetime,
) -> bool:
    if type(cmp_point) is date or type(event_start) is date:
        return False

    return (
        # exclude midnight
        event_start.hour != 0 and event_start.minute != 0 and
        cmp_point.replace(second=0, microsecond=0) ==
        event_start.replace(second=0, microsecond=0)
    )


def send_events_notifications(
    events: List[Dict[str, str | datetime | timedelta | bool]],
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
        event_whole_day = event["whole_day"]

        send_text(f'''
📔{event["title"]}
 - 起始於 {format_d_or_dt(event["start"], event_whole_day)}
 - 結束於 {format_d_or_dt(event["end"], event_whole_day)}
 - 總計時長 {format_duration(event["duration"], event_whole_day)}
 - 登記於 {event["source"]} 日曆
''')


def notify_next_week() -> None:
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=6)

    send_events_notifications(
        fetch_events(*date_range_to_datetime_range(start, end)),
        f"⏰下週 {format_date(start)} - {format_date(end)} 的待辦行程",
    )


def notify_today() -> None:
    today = date.today()

    send_events_notifications(
        fetch_events(*date_range_to_datetime_range(today, today)),
        f"⏰今天 {format_date(today)} 的行程",
    )


def notify_coming() -> None:
    start = (
        get_local_now().replace(second=0, microsecond=0) +
        timedelta(seconds=NOTIFY_COMING_EVENT_BEFORE_SEC)
    )
    end = start + timedelta(seconds=59)

    send_events_notifications(
        [
            event
            for event in fetch_events(start, end)
            if is_event_start(start, event['start'])
        ],
        '⏰以下行程即將到來',
    )


def notify_what() -> str:
    if len(sys.argv) != 2:
        return ''

    return sys.argv[1].strip().lower()


if __name__ == '__main__':
    nw = notify_what()

    if nw == 'week':
        notify_next_week()
    elif nw == 'today':
        notify_today()
    else:
        notify_coming()
