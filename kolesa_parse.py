import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os

class bothandler:
    
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


token = "709320970:AAGYB30J43aymiYu2VTCBa9uKHCJsfXNLSc"

greet_bot = bothandler(token)
greetings = ('472717315', '671788131')

def get_html(url):
    response = requests.get(url)
    return response.text


def get_all_autos(urls):
    div_names = ['row vw-item list-item a-elem',\
            'row vw-item list-item blue a-elem',\
            'row vw-item list-item yellow a-elem']
    all_divs = []
    for url in urls:
        if url =='':
            continue
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        divs = soup.find_all("div", class_ = div_names)
        all_divs.extend(divs)

    return all_divs

def check(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            print("created file ", file)

def main():
    try:
        check('urls.xml')
        check('passed_autos.xml')
        with open('urls.xml', 'r') as file:
            urls = file.read().split('\n')
        with open('passed_autos.xml', 'r') as file:
            passed_autos = file.read().split('\n')
        while (1):
            t = time.time()
            all_autos = get_all_autos(urls)
            #print(len(all_autos))
            ids_dict = {}
            for div in all_autos:
                if div['id'] in passed_autos:
                    continue
                else:
                    with open('passed_autos.xml', 'a') as file:
                        file.write(div['id']+'\n')
                    passed_autos.append(div['id'])
                    href = urljoin('https://kolesa.kz', div.a['href'])
                    #last_region = div['a-info-side col-right-list']
                    price = div.contents[1].contents[0].contents[1].text.lstrip()
                    name = div.contents[1].contents[0].contents[0].a.text
                    info = div.contents[1].contents[2].contents[0].text.lstrip()
                    date = div.contents[1].contents[3].contents[0].contents[1].text.lstrip()
                    ids_dict.update({div['id']:[str(href), '  '+str(price), str(name), str(info), str(date)]})
                    # vkapi.messages.send(domain='id204817379', message=ids_dict[div['id']], v=3)
                    greet_bot.send_message(greetings[0], ids_dict[div['id']])
                    greet_bot.send_message(greetings[1], ids_dict[div['id']])

            print(time.time()-t, 'sec')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
