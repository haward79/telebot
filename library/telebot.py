
import requests
from requests import Response

from library.config import quit_on_fatal, read_config


CONFIG: dict = {}
RETRY = 3


def init_config() -> None:
    global CONFIG

    config_template = {
        'token': None,
        'receiver': None,
        'calendar_token': None,
        'calendar_receiver': None,
    }

    config = read_config(
        'telebot.yml',
        config_template,
    )

    if config is None:
        quit_on_fatal()
        return

    CONFIG = config


def get_config_value(key: str, prefix: str | None = None) -> str | int:
    value = CONFIG.get(
        f'{prefix}_{key}'
        if prefix
        else
        key
    )

    if isinstance(value, str) or isinstance(value, int):
        return value

    quit_on_fatal()
    return ''


def send_request(args: dict) -> bool:
    req = None

    for i in range(RETRY):
        try:
            req = requests.post(**args)
        except Exception as e:
            print('Handled Exception:', e)
        else:
            break

    return isinstance(req, Response) and req.status_code == 200


def send_text(text: str, prefix: str | None = None) -> bool:
    return send_request({
        'url': f'https://api.telegram.org/bot{get_config_value("token", prefix)}/sendMessage',
        'data': {
            'chat_id': get_config_value("receiver", prefix),
            'text': text,
        }
    })


def send_image(image: bytes, prefix: str | None = None) -> bool:
    return send_request({
        'url': f'https://api.telegram.org/bot{get_config_value("token", prefix)}/sendPhoto',
        'data': {
            'chat_id': get_config_value("receiver", prefix)
        },
        'files': {'photo': image},
    })


init_config()
