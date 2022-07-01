import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import configs.config as cfg
from defs import sending


source = 'calend'
website = cfg.urls[source]['url']
date = datetime.now() # + timedelta(hours=10)
str_date = '{}-{}-{}'.format(date.year, date.month, date.day)
pages = ['holidays','events']

# pages = ['events']

async def parsing_events():    
    data = {}
    for i in pages:
        for k in range(2):
            r = requests.get(f'{website}/{i}/{str_date}')
            if r.status_code != 502:
                break
            await asyncio.sleep(3)

        text = r.text
        chapts = text.split('itemsNet')
        data[i] = {}
        k = 0
        for j in chapts[1:]:
            items = j.split('three-three')
            for item in items[1:]:
                text = ''
                if i == 'events':
                    start = item.find('caption') + 5
                    start = item.find('year', start) + 7
                    end = item.find('<', start)
                    text = item[start:end] + ' - '
                
                start = item.find('title') + 5
                start = item.find('<a href=', start) + 9
                end = item.find('>', start) - 1
                link = item[start:end]
                
                start = end + 2
                end = item.find('</a>', start)
                text = text + item[start:end]
                data[i][k] = {
                    'link': link,
                    'text': text
                }
                k += 1
    return data


async def parsing_persons():
    for k in range(2):
        r = requests.get(f'{website}/persons/{str_date}')
        if r.status_code != 502:
            break
        await asyncio.sleep(3)
    
    soup = BeautifulSoup(r.content, 'html.parser')
    births = soup.find_all('li', class_='one-four birth')
    mourns = soup.find_all('li', class_='one-four mourn')
    chapts = {'births': births, 'mourns': mourns}
    
    data = {}
    for i in chapts:
        chapt = chapts[i]
        data[i] = {}
        j = 0
        for k in chapt:
            tmp = k.find('span', {'class': 'title'})
            link = tmp.contents[0].attrs['href']
            title = tmp.text
            b_year = k.find('span', {'class': 'year'}).text
            tmp = k.find('span', {'class': 'year2'})
            d_year = tmp.text if tmp else ''
        
            data[i][j] = {'link': link,
                            'text': f'{b_year} - {d_year} {title}'}
            j += 1
    return data


async def making(data):
    pass
    return data


async def parsing_calend(nothing):
    funcs = [parsing_events, parsing_persons]
    msgs = []
    for f in funcs:
        data = await f()
        msg = await making(data)
        msgs.append(msg)
    await sending(msgs)








async def msgcalev():
    text = await getcalendev()
    now = datetime.now() + timedelta(hours=10)
    date = now.strftime('%d.%m.%Y')
    wd = cfg.weekday[int(now.strftime('%w'))]
    head = 'Calend Events'

    msg = '<b>Календарь событий на сегодня:</b>\n' + wd + ', ' + date + '\n\nПраздники:'
    for i in text['holydays']:
        msg = msg + '\n' + '📍<b>' + text['holydays'][i]['title'][:2].replace("<", "&lt;") + '</b>' + \
                                    text['holydays'][i]['title'][2:].replace("<", "&lt;")
    
    msg = msg + '\n\nЗнаменательные события:'
    for i in text['events']:
        msg = msg + '\n' + '📍' + text['events'][i]['year'] + ' ' + \
                                    text['events'][i]['title'].replace("<", "&lt;")
    
    msg = msg + '\n\nИсточник: calend.ru' + '\n\n#<b>календарь</b> #calend #праздники #сводка' + cfg.bot_msg_tail
    msgdata = {0: msg}
    
    # i = 0
    # while i < len(text['type']):
    #     if text['type'][i] == 'Thisday':
    #         msg = msg + '\n' + text['title'][i]
    #     i += 1
    return msgdata


async def msgcalpers():
    text = await getcalendpers()
    now = datetime.now() + timedelta(hours=10)
    date = now.strftime('%d.%m.%Y')
    wd = cfg.weekday[int(now.strftime('%w'))]
    head = 'Calend Persons'

    msg = '<b>Календарь событий на сегодня:</b>\n' + wd + ', ' + date + '\n\nВ этот день родились:'
    for i in text['born']:
        msg = msg + '\n' + '📍' + text['born'][i]['year'] + ' ' + \
                                    text['born'][i]['title'].replace("<", "&lt;")
    
    msg = msg + '\n\nДень памяти:'
    for i in text['died']:
        msg = msg + '\n' + '📍' + text['died'][i]['year'] + ' ' + \
                                    text['died'][i]['title'].replace("<", "&lt;")
    
    msg = msg + '\n\nИсточник: calend.ru' + '\n\n#<b>календарь</b> #calend #именины #сводка' + cfg.bot_msg_tail
    msgdata = {0: msg}
    return msgdata


if __name__ == "__main__":
    test = msgcalev()
    print(test)
