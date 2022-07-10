import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import config as cfg
from defs import sending, envs

website = cfg.urls['calend']['url']
date = datetime.now() # - timedelta(hours=24)
str_date = '{}-{}-{}'.format(date.year, date.month, date.day)
pips = cfg.pips
chapts = cfg.urls['calend']['chapts']
pages = [['holidays','events'],['persons']]

hashtags = {'holidays': 'события',
            'thisDay': 'события',
            'events': 'события',
            'births': 'персоны',
            'mourns': 'персоны'
    }

async def making(data):
    tmp = list(data.keys())[0]
    head = 'calend.ru | #календарь | #{}\n'.format(hashtags[tmp])
    msg = ''
    for src in data.keys():
        pip = pips.get(src, '🔹')
        h2 = chapts[src]
        msg = f'{msg}\n{h2}:\n'
        if data[src]:
            i = 0
            for n in data[src]:
                lnk = data[src][n]['link']
                text = data[src][n]['text']
                
                if src in ['holidays','thisDay']:
                    spl_text = text.split()
                    frst_half = spl_text[0]
                    snd_half = ' '.join(spl_text[1:])
                    item = f'{pip}<a href="{lnk}">{frst_half}</a> {snd_half}\n'
                else:
                    b_year = data[src][n]['b_year']
                    d_year = data[src][n]['d_year']
                    html_b_year = f'{pip}<a href="{lnk}">{b_year}</a>' if b_year else ''
                    html_d_year = f' - <a href="{lnk}">{d_year}</a>' if d_year else ''
                    item = f'{html_b_year}{html_d_year} {text}\n'
                msg = f'{msg}{item}'
    if msg:
        footer = envs['summ_footer']
        msg = f'\n\n{head}{msg}\n{head}@{footer}'
    return msg

async def parsing_calend(nothing):    
    datas = []
    for p in pages:
        data = {}
        chapts = {}
        for page in p:
            for i in range(3):
                r = requests.get(f'{website}/{page}/{str_date}')
                if r.status_code != 502:
                    break
                await asyncio.sleep(3)
                
            soup = BeautifulSoup(r.content, 'html.parser')
            if page == 'holidays':
                holidays = soup.find_all('div', class_='block holidays')[0]
                thisDay = soup.find_all('div', class_='block thisDay')
                chapts['holidays'] = holidays.find_all('li', class_='three-three')
                if thisDay:
                    chapts['thisDay'] = thisDay[0].find_all('li', class_='three-three')
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
                if chapt == 'events':
                    b_year = item.find('span', {'class': 'year'}).text
                    d_year = ''
                elif chapt in ['births','mourns']:
                    b_year = item.find('span', {'class': 'year'}).text.split()[-1]
                    tmp = item.find('span', {'class': 'year2'})
                    d_year = tmp.text if tmp else ''
                else:
                    b_year = ''
                    d_year = ''
                data[chapt][k] = {'link': link,
                                'b_year': b_year,
                                'd_year': d_year,
                                'text': title}
                k += 1        
        datas.append(data)
    
    msgs = []
    for d in datas:
        msg = await making(d)
        msgs.append(msg)
    await sending(msgs, chat_id=envs['summ_chan'], forward=envs['opsp_chan'])
