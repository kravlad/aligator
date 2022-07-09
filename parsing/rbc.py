import requests
from datetime import datetime
from bs4 import BeautifulSoup # pip3 install bs4

import config as cfg
from defs import bm, making, sending, envs

hashtags = {
            'finec': 'финансы',
            'business': 'бизнес',
            'politic': 'политика'
            }


async def parsing_rbc(sources):
    data = {}
    for source in sources.keys():
        j = 0
        data = {source: {}}
        bookmarks = await bm(src='rbc')
        for chapt in sources[source]:
            last_id = bookmarks[chapt]['bookmark']
            website = cfg.urls['rbc'][chapt]

            for k in range(3):
                r = requests.get(website)
                if r.status_code != 502:
                    break
                await asyncio.sleep(3)
            
            soup = BeautifulSoup(r.content, 'html.parser')
            content = soup.find_all('span', itemprop='itemListElement')
        
            l = 0
            for i in content:
                link = i.contents[3].attrs['content']
                item_id = link.split('/')[-1]
                if last_id != item_id:
                    if l == 0:
                        bookmarks[chapt]['bookmark'] = item_id
                    data[source][j] = {
                                        'id': item_id,
                                        'publish': True,
                                        'link': link,
                                        'html_text': i.contents[5].attrs['content']
                    }
                    j -= 1
                else:
                    break
                l += 1
        
        if j < 0:
            bookmarks[chapt]['date'] = str(datetime.now())
            await bm(src='rbc', data=bookmarks)
        
            sorted_data = sorted(data[source].items(), key=lambda x: x[0])
            data[source] = dict(sorted_data)
                
            head = 'rbc.ru | #рбк | #{}'.format(hashtags[source])
            msgs = await making(data, head=head, header=False, footer=envs['news_footer'])
            await sending(msgs, chat_id=envs['news_chan'])
