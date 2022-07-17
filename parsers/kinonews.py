# import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# import tools.mongodb as db
import config as cfg
from defs import bm, making, sending, envs
# import defs.common as common


async def parsing_kinonews(nothing):
    """docstring."""
    source = 'kinonews'
    bookmarks = await bm(src=source)
    last_id = bookmarks['bookmarks'][source]
    website = cfg.urls[source]['website']

    for k in range(3):
        r = requests.get(website + cfg.urls[source]['url'])
        if r.status_code != 502:
            break
        await asyncio.sleep(3)

    soup = BeautifulSoup(r.content, 'html.parser')
    div_container = soup.find_all('div', class_='anons-title-new')

    i = 0
    data = {source: {}}
    for item in div_container:
        link = website + item.next_element.next_element.attrs['href']
        item_id = int(link[29:-1])
        if last_id != item_id:
            data[source][i] = {
                        'id': item_id,
                        'publish': True,
                        'link': link,
                        'html_text': item.text
            }
            i -= 1
        else:
            break

    if i < 0:
        last_id = data[source][0]['id']
        await bm(src=source, data={'date': str(datetime.now()), 'bookmarks': {source: last_id}})

        sorted_data = sorted(data[source].items(), key=lambda x: x[0])
        data[source] = dict(sorted_data)

        head = 'kinonews.ru | #kinonews | #кино'
        msgs = await making(data, head=head, header=False, footer=envs['news_footer'])
        await sending(msgs, chat_id=envs['news_chan'])
