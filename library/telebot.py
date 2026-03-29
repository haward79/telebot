
import requests

from library.config import quit_on_fatal, read_config


CONFIG: dict | None = None


def init_config() -> None:
    global CONFIG

    # config has been already loaded
    if CONFIG is not None:
        return

    config_template = {
        'token': None,
        'receiver': None,
    }

    config = read_config(
        'telebot.yml',
        config_template,
    )

    if config is None:
        quit_on_fatal()
        return

    CONFIG = config


def send_text(text: str) -> bool:
    init_config()

    global CONFIG

    url = f'https://api.telegram.org/bot{CONFIG.get("token")}/sendMessage'
    data = {
        'chat_id': CONFIG.get("receiver"),
        'text': text
    }

    req = requests.post(url, data=data)

    return req.status_code == 200


def send_image(image: bytes) -> bool:
    init_config()

    global CONFIG

    url = f'https://api.telegram.org/bot{CONFIG.get("token")}/sendPhoto'
    data = {'chat_id': CONFIG.get("receiver")}
    files = {'photo': image}

    req = requests.post(url, data=data, files=files)

    return req.status_code == 200
