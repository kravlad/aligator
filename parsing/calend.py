import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import config as cfg
from defs import sending

source = 'calend'
website = cfg.urls[source]['url']
date = datetime.now() # + timedelta(hours=10)
str_date = '{}-{}-{}'.format(date.year, date.month, date.day)
pages = ['holidays','events']
pips = cfg.pips

xxx = {
    'holidays': 'Праздники',
    'thisDay': 'Также в этот день',
    'events': 'События',
    'births': 'В этот день родились',
    'mourns': 'День памяти',
}

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


async def making(data, hashtag):
    head = f'calend.ru | #календарь | #{hashtag}'
    msg = ''
    for src in data.keys():
        pip = pips.get(src, '🔹')
        h2 = xxx[src]
        msg = f'{msg}\n\n{h2}:'
        if data[src]:
            i = 0
            for n in data[src]:
                lnk = data[src][n]['link']
                text = data[src][n]['text']
                l_text = text.split()
                if src in ['births','mourns']:
                    t1 = l_text[0]
                    t2 = l_text[2]
                    t3 = ' '.join(l_text[3:])
                    item = f'{pip}<a href="{lnk}">{t1}</a> - <a href="{lnk}">{t2}</a> {t3}\n'
                else:
                    t1 = l_text[0]
                    t2 = ' '.join(l_text[1:])
                    item = f'\n{pip}<a href="{lnk}">{t1}</a> {t2}'
                msg = f'{msg}{item}'
    if msg:
        msg = f'\n\n{head}{msg}\n{head}\n@rusmsp'
    return msg


async def parsing_calend(nothing):
    funcs = {1: {'f': parsing_events, 
                'h1': 'события'},
            2: {'f': parsing_persons,
                'h1': 'персоны'}}
    msgs = []
    for f in funcs:
        data = await funcs[f]['f']()
        msg = await making(data, funcs[f]['h1'])
        msgs.append(msg)
    await sending(msgs)
