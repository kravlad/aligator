import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import config as cfg
from defs import sending, opsp_chan

website = cfg.urls['calend']['url']
date = datetime.now() # + timedelta(hours=10)
str_date = '{}-{}-{}'.format(date.year, date.month, date.day)
pips = cfg.pips
xxx = cfg.urls['calend']['chapts']
pages = [['holidays','events'],['persons']]

async def making(data, hashtag):
    head = f'calend.ru | #календарь | #{hashtag}\n'
    msg = ''
    for src in data.keys():
        pip = pips.get(src, '🔹')
        h2 = xxx[src]
        msg = f'{msg}\n{h2}:\n'
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
                    item = f'{pip}<a href="{lnk}">{t1}</a> {t2}\n'
                msg = f'{msg}{item}'
    if msg:
        msg = f'\n\n{head}{msg}\n{head}@rusmsp'
    return msg

async def parsing_calend(nothing):    
    datas = []
    for p in pages:
        data = {}
        chapts = {}
        for page in p:
            for i in range(2):
                r = requests.get(f'{website}/{page}/{str_date}')
                if r.status_code != 502:
                    break
                await asyncio.sleep(3)
                
            soup = BeautifulSoup(r.content, 'html.parser')
            if page == 'holidays':
                holidays = soup.find_all('div', class_='block holidays')[0]
                thisDay = soup.find_all('div', class_='block thisDay')[0]
                chapts['holidays'] = holidays.find_all('li', class_='three-three')
                chapts['thisDay'] = thisDay.find_all('li', class_='three-three')
            elif page == 'events':
                events = soup.find_all('div', class_='knownDates famous-date')[0]
                chapts['events'] = events.find_all('li', class_='three-three')
            elif page == 'persons':
                chapts['births'] = soup.find_all('li', class_='one-four birth')
                chapts['mourns'] = soup.find_all('li', class_='one-four mourn')
                
        for chapt in chapts:
            k = 0
            data[chapt] = {}
            for item in chapts[chapt]:
                tmp = item.find('span', {'class': 'title'})
                link = tmp.contents[0].attrs['href']
                title = tmp.text
                if chapt in ['events','births','mourns']:
                    b_year = item.find('span', {'class': 'year'}).text
                    if chapt != 'events':
                        tmp = item.find('span', {'class': 'year2'})
                        d_year = tmp.text if tmp else ''
                        years = f'{b_year} - {d_year} '
                    else:
                        years = f'{b_year} - '
                else:
                    years = ''
                data[chapt][k] = {'link': link,
                                'text': f'{years}{title}'}
                k += 1        
        datas.append(data)
    
    msgs = []
    for d in datas:
        msg = await making(d, 'события-персоны')
        msgs.append(msg)
    await sending(msgs, forward=opsp_chan)
