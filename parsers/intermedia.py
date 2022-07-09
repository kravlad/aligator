import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

import config as cfg
from defs import bm, making, sending, envs

async def parsing_intermedia(nothing):
    source = 'intermedia'
    bookmarks = await bm(src=source)
    last_id = bookmarks['bookmarks'][source]
    website = cfg.urls[source]['website']

    for k in range(3):
        r = requests.get(website + cfg.urls[source]['url'])
        if r.status_code != 502:
            break
        await asyncio.sleep(3)
        
    soup = BeautifulSoup(r.content, 'html.parser')
    content = soup.find_all('section', class_= 'news-item')
        
    if len(content) > 0:
        data = {source: {}}
        k = 0
        for i in content:
            item_id = int(i.attrs['data-new_id'])
            if item_id != last_id:
                text = i.find('div', class_= 'title').contents[-1].replace('\r', '').replace('\n', '').replace('\t', '')
                data[source][k] = {
                        'id': item_id,
                        'publish': True,
                        'link': f'{website}/news/{item_id}',
                        'html_text': text
                }
                k -= 1
            else:
                break
            
    if k < 0:
        last_id = data[source][0]['id']
        await bm(src=source, data={'date': str(datetime.now()), 'bookmarks': {source: last_id}})
    
        sorted_data = sorted(data[source].items(), key=lambda x: x[0])
        data[source] = dict(sorted_data)
        
        head = 'intermedia.ru | #intermedia | #музыка'
        msgs = await making(data, head=head, header=False, footer=envs['news_footer'])
        await sending(msgs, chat_id=envs['news_chan'])
