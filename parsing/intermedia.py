import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

import configs.config as cfg
from defs import send_telegram, bm, making, sending


async def parsing_intermedia(nothing):
    source = 'intermedia'
    bookmarks = await bm(src=source)
    last_id = bookmarks['bookmarks'][source]
    website = cfg.urls[source]['website']

    for k in range(2):
        r = requests.get(website + cfg.urls[source]['url'])
        if r.status_code != 502:
            break
        await asyncio.sleep(3)
    
    content = r.text.split('news-item')
    if len(content) > 0:
        data = {source: {}}
        k = 0
        for i in content[1:]:
            start = i.find('data-new_id=') + 13
            end = i.find('>', start) - 1
            item_id = int(i[start:end])
            if item_id != last_id:
                start = i.find('alt=', end) + 5
                end = i.find('>', start) - 1
                html_text = i[start:end]
        
                data[source][k] = {
                        'id': item_id,
                        'publish': True,
                        'link': f'{website}/news/{item_id}',
                        'html_text': html_text
                }
                k -= 1
            else:
                break
    
    
    if k < 0:
        last_id = data[source][0]['id']
        await bm(src=source, data={'date': str(datetime.now()), 'bookmarks': {source: last_id}})
    
        sorted_data = sorted(data[source].items(), key=lambda x: x[0])
        data[source] = dict(sorted_data)
        
        msgs = await making(data, link='{}.ru', header=False)
        await sending(msgs)
