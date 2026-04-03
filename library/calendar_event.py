
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
        self.uid = uid
        self.title = title
        self.start = start
        self.end = end
        self.duration = duration
        self.whole_day = whole_day
        self.source = calendar_name

    def __iter__(self):
        return (
            self.uid,
            self.title,
            self.start,
            self.end,
            self.duration,
            self.whole_day,
            self.source,
        )

    @property
    def uid(self) -> str:
        return self.uid

    @property
    def title(self) -> str:
        return self.title

    @property
    def start(self) -> datetime:
        return self.start

    @property
    def end(self) -> datetime:
        return self.end

    @property
    def duration(self) -> timedelta:
        return self.duration

    @property
    def whole_day(self) -> bool:
        return self.whole_day

    @property
    def calendar_name(self) -> str:
        return self.source
