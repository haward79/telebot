
from time import sleep
from datetime import datetime
from selenium import webdriver


def get_mini_info() -> str:
    mini_info = ''

    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('-headless')

    firefox = webdriver.Firefox(options=firefox_options)
    firefox.get('https://www.facebook.com/love11mini')
    sleep(3)
    source_code = firefox.page_source
    firefox.close()

    pos = source_code.find(datetime.now().strftime('%-m/%-d'))
    end_pos = source_code.find('買一送一', pos)

    if pos != -1 and end_pos != -1:
        mini_info = source_code[pos:end_pos+4]
        mini_info = mini_info.replace('＂', '').replace('"', '').replace("'", '')

    if len(mini_info) > 0:
        resp = '米里Mini 今日優惠\n' + mini_info
    else:
        resp = '無法取得米里Mini今天的優惠資訊。'

    return resp
