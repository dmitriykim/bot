import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, timeout=30):
        method = 'getupdates'
        params = {'timeout': timeout}
        resp = requests.get(self.api_url + method, params)
        print(resp)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendmessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]

        return last_update

    def get_all_chat_id(self):
        get_result = self.get_updates()
        chat_ids = []
        for updates in get_result:
            chat_id = updates['message']['chat']['id']
            chat_ids.append(chat_id)
        return list(set(chat_ids))


token = "1190799005:AAHKm7-K7ZxSYMhykptRwLcKRr-nLgFeisM"

greet_bot = BotHandler(token)
greetings = ['133929927']


def get_html(url):
    response = requests.get(url)
    return response.text


def get_all_autos(urls):
    div_names = ['a-card a-storage-live ddl_product ddl_product_link not-colored is-visible',
                 'a-card a-storage-live ddl_product ddl_product_link not-colored is-visible is-urgent',
                 'a-card a-storage-live ddl_product ddl_product_link is-colored paid-color-light-red is-visible',
                 'a-card a-storage-live ddl_product ddl_product_link is-colored paid-color-light-red is-visible is-urgent',
                 'a-card a-storage-live ddl_product ddl_product_link is-colored paid-color-light-yellow is-visible',
                 'a-card a-storage-live ddl_product ddl_product_link is-colored paid-color-light-yellow is-visible is-urgent',
                 'a-card a-storage-live ddl_product ddl_product_link is-colored paid-color-light-green is-visible',
                 'a-card a-storage-live ddl_product ddl_product_link is-colored paid-color-light-green is-visible is-urgent']
    all_divs = []
    for url in urls:
        if url == '':
            continue
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        divs = soup.find_all("div", class_=div_names)
        all_divs.extend(divs)

    return all_divs


def check(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            print("created file ", file)


def main():
    try:
        check('urls.xml')
        check('passed_flats.xml')
        tt = time.time()
        with open('urls.xml', 'r') as file:
            urls = file.read().split('\n')
        with open('passed_flats.xml', 'r') as file:
            passed_autos = file.read().split('\n')
        print(time.time() - tt, "Time spent reading the file")
        while True:
            time.sleep(300)
            t = time.time()
            all_autos = get_all_autos(urls)
            # print(len(all_autos))
            ids_dict = {}
            for div in all_autos:
                if div['id'] in passed_autos:
                    continue
                else:
                    with open('passed_flats.xml', 'a') as file:
                        file.write(div['id'] + '\n')
                    passed_autos.append(div['id'])
                    href = urljoin('https://krisha.kz', div.a['href'])
                    # last_region = div['a-info-side col-right-list']
                    price = div.contents[1].contents[3].contents[1].contents[1].contents[3].text.lstrip()
                    name = div.contents[1].contents[3].contents[1].contents[1].contents[1].contents[1].text.lstrip()
                    address = div.contents[1].contents[3].contents[1].contents[3].contents[1].text.strip()
                    info = div.contents[1].contents[3].contents[1].contents[3].contents[3].text.strip()
                    date = div.contents[1].contents[3].contents[3].contents[3].contents[1].contents[3].text.strip()
                    ids_dict.update({div['id']: [str(href), '  ' + str(price), str(name), str(address), str(info),
                                                 str(date)]})
                    # vkapi.messages.send(domain='id204817379', message=ids_dict[div['id']], v=3)
                    greet_bot.send_message(greetings[0], ids_dict[div['id']])
                    # greet_bot.send_message(greetings[1], ids_dict[div['id']])

            print(time.time() - t, 'sec', "One iteration time")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
