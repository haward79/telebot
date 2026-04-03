
import library.calendar as calendar


if __name__ == '__main__':
    nw = calendar.notify_what()

    if nw == 'week':
        calendar.notify_next_week()
        exit()

    elif nw == 'today':
        calendar.notify_today()
        exit()

    calendar.notify_coming()
