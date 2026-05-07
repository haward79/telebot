
from json import JSONDecodeError
from typing import Tuple, List, Dict
from time import sleep
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
from io import BytesIO
from requests import Response

from library.config import quit_on_fatal, read_config


CONFIG: dict = {}


def init_config() -> None:
    global CONFIG

    config_template = {
        'token': None,
        'locations': None,
    }

    config = read_config(
        'weather.yml',
        config_template,
    )

    if config is None:
        quit_on_fatal()
        return

    CONFIG = config


def hourly_timeset_to_str(time_set: List[int]) -> List[str]:
    time_set_formatted = []

    time_set = time_set.copy()
    time_set.sort()

    i = 0
    while i < len(time_set):
        start = i

        while i + 1 < len(time_set):
            i += 1

            if time_set[i-1] + 1 != time_set[i]:
                i -= 1
                break

        if start == i:
            time_set_formatted.append(str(time_set[i]) + ':00~' + str(time_set[i]) + ':59')
        else:
            time_set_formatted.append(str(time_set[start]) + ':00~' + str(time_set[i]) + ':59')

        i += 1

    return time_set_formatted


def request_rain_info(coordinate_x: float, coordinate_y: float, days: int = 1) -> Dict | None:
    if days <= 0:
        return None

    try:
        resp = requests.get(
            'https://api.weatherapi.com/v1/forecast.json',
            params={
                'key': CONFIG.get('token'),
                'q': str(coordinate_x) + ',' + str(coordinate_y),
                'days': str(days),
            },
        )
    except Exception as e:
        print('Handled Exception:', e)
        return None

    if not isinstance(resp, Response) or resp.status_code != 200:
        return None

    try:
        resp_json = resp.json()
    except (UnicodeDecodeError, JSONDecodeError) as e:
        print('Handled Exception:', e)
        return None

    if not isinstance(resp_json, dict):
        return None

    return resp_json


def fetch_hourly_rain_metrix(coordinate_x: float, coordinate_y: float) -> Tuple[List[int] | None, List[int] | None]:
    resp = request_rain_info(coordinate_x, coordinate_y)

    if resp is None:
        return None, None

    will_it_rain_hourly = []
    chance_of_rain_hourly = []

    try:
        hours_data = resp['forecast']['forecastday'][0]['hour']

        for hour_data in hours_data:
            will_it_rain_hourly.append(hour_data['will_it_rain'])  # 1 or 0
            chance_of_rain_hourly.append(hour_data['chance_of_rain'])  # in percent

    except (KeyError, ValueError) as e:
        print(f"Handled Exception: {e}")
        return None, None

    return will_it_rain_hourly, chance_of_rain_hourly


def fetch_rain_info(
    location_name: str,
    coordinate: Tuple[float, float],
) -> Tuple[str, bytes] | None:
    if len(coordinate) != 2:
        return None

    (
        will_it_rain_hourly,
        chance_of_rain_hourly,
    ) = fetch_hourly_rain_metrix(coordinate[0], coordinate[1])

    if will_it_rain_hourly is None or chance_of_rain_hourly is None:
        return None

    time_set = [
        i
        for i in range(len(will_it_rain_hourly))
        if will_it_rain_hourly[i] == 1
    ]

    text = '\n'.join(hourly_timeset_to_str(time_set))

    if len(text) > 0:
        text = '今天' + location_name + '地區在以下時段有降雨：\n' + text
    else:
        text = '今天' + location_name + '地區全日無雨 ^_^'

    # Set matplotlib font family
    matplotlib.rcParams['font.family'] = ['Microsoft JhengHei']

    fig, ax = plt.subplots()

    bar_list = ax.bar(np.arange(24), chance_of_rain_hourly, width=1, color='#399AFF', edgecolor="#004185", linewidth=1)

    for i in range(24):
        if will_it_rain_hourly[i] == 1:
            bar_list[i].set_color('#0361C6')

    ax.set_xlim(0, 23)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Hour')
    ax.set_ylabel('Raining Rate')
    ax.set_xticks(np.arange(0, 24, 1))
    ax.set_title('Hourly Raining Rate in ' + location_name)

    buffer = BytesIO()
    fig.savefig(buffer, format='jpg')
    buffer.seek(0)
    chart = buffer.read()

    plt.close(fig)

    return text, chart


def get_rain_info() -> List[Tuple[str, bytes]]:
    init_config()

    rain_info_collect = []

    for location in CONFIG.get('locations', []):
        rtn = fetch_rain_info(location['name'], location['coordinate'])

        if rtn is not None:
            rain_info_collect.append(rtn)

        sleep(1)

    return rain_info_collect


init_config()
