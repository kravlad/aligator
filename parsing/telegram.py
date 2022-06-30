import json
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # pip3 install apscheduler

from defs import replacing, send_telegram, bm, making, sending
from configs.storage import settings as sets

# scheduler = AsyncIOScheduler(daemon=True)
tg_link = sets['cfg'].links['telegram']
replacement = sets['cfg'].replacement['telegram']
summ_chan = sets['summ_chan']


async def daily(data):
    msgs = await making(data, False, ' | #главное')
    await sending(msgs, summ_chan)
    # run_date = datetime.now() + timedelta(minutes=10)
    # scheduler.add_job(sending,
    #                         'date',
    #                         kwargs={'msgs': msgs},
    #                         run_date=run_date,
    #                         timezone=config.timezone,
    #                         misfire_grace_time=60
    #                         )    


async def tg_parsing(sources):
    bookmarks = await bm(src='telegram')
    # sources = list(bookmarks.keys())
    data = {}
    for source in sources:
        # print(source)
        for k in range(2):
            r = requests.get(tg_link + 's/' + source)
            if r.status_code != 502:
                break
            await asyncio.sleep(3)
        content = r.text.split('data-post=')
        if len(content) > 0:
            source = source.split('?')[0]
            last_id = bookmarks[source]
            if not data.get(source):
                data[source] = {}
            all_ids = []
            for i in content[1:]:
                end = i.find('data-view=') - 2
                link = i[1:end]
                msg_id = int(link.split('/')[1])
                all_ids.append(msg_id)
                if msg_id > last_id:
                    start = i.find('tgme_widget_message_text', end)
                    xwer = i[start:(start + 70)]
                    if 'js-message_reply_text' in xwer:
                        start = i.find('tgme_widget_message_text', (start + 70))
                        
                    start = i.find('>', start) + 1
                    end = i.find('tgme_widget_message_link_preview', start) - 17
                    if end < 0:
                        end = i.find('tgme_widget_message_footer', start) - 20
                    html_text = i[start:end]
                    if html_text.startswith('<i class='):
                        start = i.find('>', start) + 1
                        html_text = '<i>' + i[start:end]
                    # html_text = html_text
                    if 'pinned a photo' not in html_text:
                        new_text = await replacing(html_text, replacement)
                        while new_text.startswith('\n'):
                            new_text = new_text[2:]
                        
                        header = new_text.split('\n')[0].replace('<b>', '').replace('</b>', '')
                        data[source][msg_id] = {'id': msg_id, 'publish': True, 'link': f'{tg_link}{link}', 'header': header, 'html_text': new_text}
                        
                        if (source == 'svtvnews' and header.startswith('Что случилось')) or \
                            (source == 'theinsider' and header.startswith('Главное за день')) or \
                            (source == 'tele_eve' and '#картинадня' in html_text) or \
                            (source == 'tele_eve' and '#главноезаночь' in html_text):
                            
                            await daily({source: {msg_id: data[source][msg_id]}})
                            data[source][msg_id]['publish'] = False
        
        sorted_tuple = sorted(data[source].items(), key=lambda x: x[0])
        data[source] = dict(sorted_tuple)

        # all_ids.sort()
        m_ids = list(data[source].keys())
        if m_ids:
            # print(m_ids[0], ' - ', m_ids[-1])
            if all_ids[0] > last_id:
                sources.append(f'{source}?before={m_ids[0]}')
            else:
                bookmarks[source] = m_ids[-1]
            
        await asyncio.sleep(3)
    
    await bm(src='telegram', data=bookmarks)
    
    if data.get('tele_eve'):
        data.pop('tele_eve')
    
    msgs = await making(data)
    await sending(msgs)
