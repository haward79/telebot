# Overview

This is a lightweight Telegram bot project.

It supports two main interaction modes:

## 1. Interactive Responses

Users can interact directly with the bot and receive replies.

Supported features include:

- Saving plain text messages and files to a WebDAV-compatible cloud storage
- Sending simple, predefined responses
- Extensible architecture for adding more features

## 2. Proactive Notifications

The bot can actively send notifications to users.

Supported features include:

- Fetching events from CalDAV-compatible calendars
  - Daily event notifications
  - Weekly event notifications
  - Upcoming event notifications

- Sending rain/weather reports

# Usage & Quick Start

## Dependencies & Requirements

1. Docker and Docker Compose
2. A Telegram Bot and its API token
3. A WebDAV/CalDAV-compatible service (e.g. [NextCloud](https://nextcloud.com/) or [OwnCloud](https://owncloud.com/))
4. An API key from [weatherapi.com](https://www.weatherapi.com/)

## Build & Run

```bash
git clone https://github.com/haward79/telebot.git
cd telebot

docker compose build
docker compose up -d

# Follow logs
docker compose logs -f
```

## Routine & Crontab

```bash
crontab -e

# assume you put this project at /telebot

# send raining report at three moments every day
#  0 5,12,18  *   *   *   /bin/bash /telebot/cron_helper.bash routine_daily

# send daily events notification at early morning
# 50 4        *   *   *   /bin/bash /telebot/cron_helper.bash calendar_notification today

# send weekly events notification at early morning
# 30 4        *   *   0   /bin/bash /telebot/cron_helper.bash calendar_notification week
```
