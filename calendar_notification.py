
from datetime import date, datetime, time

from library.caldav import fetch_events
from library.telebot import send_text


WEEKDAY_TO_LOCALE = ['一', '二' , '三', '四', '五', '六', '日']


def weekday_to_locale(obj: datetime | date) -> str:
    return WEEKDAY_TO_LOCALE[obj.weekday()]


def format_date(raw: date) -> str:
    return raw.strftime(f"%Y-%m-%d({weekday_to_locale(raw)})")


def format_datetime(raw: datetime) -> str:
    return raw.strftime(f"%Y-%m-%d({weekday_to_locale(raw)}) %p %I:%M:%S")


def format_d_or_dt(
    raw: datetime | date,
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
    minutes = raw.seconds // 60

    if days:
        return f"{days}天 {hours}時 {minutes}分"
    elif hours:
        return f"{hours}時 {minutes}分"

    return f"{minutes}分"


if __name__ == '__main__':
    for event in fetch_events():
        event_whole_day = event["whole_day"]

        send_text(f'''
📔{event["title"]}
 - 起始於 {format_d_or_dt(event["start"], event_whole_day)}
 - 結束於 {format_d_or_dt(event["end"], event_whole_day)}
 - 總計時長 {format_duration(event["duration"], event_whole_day)}
 - 登記於 {event["source"]} 日曆
''')
