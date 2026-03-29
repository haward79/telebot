
import library.telebot as telebot
from library.weather import get_rain_info


if __name__ == '__main__':
    rains = get_rain_info()

    for rain in rains:
        text, chart = rain
        telebot.send_text(text)
        telebot.send_image(chart)
