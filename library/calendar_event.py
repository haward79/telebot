
from datetime import datetime, timedelta


class CalendarEvent:
    def __init__(
        self,
        uid: str,
        title: str,
        start: datetime,
        end: datetime,
        duration: timedelta,
        whole_day: bool,
        calendar_name: str,
    ):
        self._uid = uid
        self._title = title
        self._start = start
        self._end = end
        self._duration = duration
        self._whole_day = whole_day
        self._source = calendar_name

    def __iter__(self):
        return (
            self._uid,
            self._title,
            self._start,
            self._end,
            self._duration,
            self._whole_day,
            self._source,
        )

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def title(self) -> str:
        return self._title

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

    @property
    def duration(self) -> timedelta:
        return self._duration

    @property
    def whole_day(self) -> bool:
        return self._whole_day

    @property
    def calendar_name(self) -> str:
        return self._source
