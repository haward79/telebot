
from typing import Tuple, List
from time import sleep
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import requests
from io import BytesIO

from library.config import quit_on_fatal, read_config


CONFIG: dict | None = None


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
        return

    CONFIG = config


def fetch_rain_info(
    location_name: str,
    coordinate: Tuple[float, float],
) -> Tuple[str, bytes] | None:
    if len(coordinate) != 2:
        return None

    parameters = {
        'key': CONFIG.get('token'),
        'q': str(coordinate[0]) + ',' + str(coordinate[1]),
        'days': '1'
    }

    resp = requests.get(
        'http://api.weatherapi.com/v1/forecast.json',
        params=parameters
    )

    if resp.status_code != 200:
        return None

    will_it_rain_hourly = []
    chance_of_rain_hourly = []

    try:
        resp = resp.json()
        hours_data = resp['forecast']['forecastday'][0]['hour']

        for hour_data in hours_data:
            will_it_rain_hourly.append(hour_data['will_it_rain'])
            chance_of_rain_hourly.append(hour_data['chance_of_rain'])

        if len(will_it_rain_hourly) != len(chance_of_rain_hourly):
            raise ValueError('Data from api are wrong. The api may be changed.')

    except ValueError as e:
        print(f"ERROR: {e}")
        return None

    text = ''

    time_set = []
    time_set_formatted = []

    # TODO
    for i in range(len(will_it_rain_hourly)):
        if will_it_rain_hourly[i] == 1:
            time_set.append(i)

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

    for period in time_set_formatted:
        text += period + '\n'

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

    if CONFIG is None:
        quit_on_fatal()

    rain_info_collect = []

    for location in CONFIG.get('locations'):
        rtn = fetch_rain_info(location['name'], location['coordinate'])

        if rtn is not None:
            rain_info_collect.append(rtn)

        sleep(1)

    return rain_info_collect
