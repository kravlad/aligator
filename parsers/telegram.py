import json
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # pip3 install apscheduler

import config as cfg
from defs import replacing, send_telegram, bm, making, sending, envs

# scheduler = AsyncIOScheduler(daemon=True)
tg_link = cfg.urls['telegram']
replacement = cfg.replacement['telegram']

async def daily(data, chat_id, head, frwd=None):
    msgs = await making(data, head=head, header=False, footer=envs['summ_footer'])
    await sending(msgs, chat_id, forward=frwd)
    # run_date = datetime.now() + timedelta(minutes=10)
    # scheduler.add_job(sending,
    #                         'date',
    #                         kwargs={'msgs': msgs},
    #                         run_date=run_date,
    #                         timezone=config.timezone,
    #                         misfire_grace_time=60
    #                         )    


async def parsing_tg(kwargs):
    params = kwargs.get('params', {})
    chat_id = envs.get(params.get('chat_id'))
    if chat_id:
        bookmarks = await bm(src='telegram')
        # sources = list(bookmarks.keys())
        data = {}
        j = 0
        dayly_chat_id = envs.get(params.get('dayly_chat_id'))
        limit = params.get('limit', -1)
        sources = kwargs['sources']
        for source in sources:
            # print(source)
            for k in range(3):
                r = requests.get(tg_link + 's/' + source)
                if r.status_code != 502:
                    break
                await asyncio.sleep(3)
                
            soup = BeautifulSoup(r.content, 'html.parser')
            content = soup.find_all('div', class_= 'tgme_widget_message_wrap')
            if len(content) > 0:
                source = source.split('?')[0]
                last_id = bookmarks['bookmarks']['regular'][source]
                last_daily_id = bookmarks['bookmarks']['daily'].get(source)
                if not data.get(source):
                    data[source] = {}
                all_ids = []
                for i in content:
                    tmp = i.find('div', class_= 'tgme_widget_message')
                    link = tmp.attrs['data-post']
                    msg_id = int(link.split('/')[-1])
                    all_ids.append(msg_id)

                    if msg_id > last_id:
                        x = tmp.find('div', class_= 'tgme_widget_message_text js-message_text')
                        y = [str(i) for i in x.contents]
                        html_text = ''.join(y)
                        if 'pinned' not in html_text:
                            new_text = await replacing(html_text, replacement)
                            while new_text.startswith('\n'):
                                new_text = new_text[2:]
                            
                            header = new_text.split('\n')[0].replace('<b>', '').replace('</b>', '')
                            data[source][msg_id] = {'id': msg_id, 'publish': True, 'link': f'{tg_link}{link}', 'header': header, 'html_text': new_text}
                                    
                            if (source == 'svtvnews' and header.startswith('Что случилось')) or \
                                (source == 'tele_eve' and '#картинадня' in html_text) or \
                                (source == 'tele_eve' and '#главноезаночь' in html_text):
                                # (source == 'theinsider' and header.startswith('Главное за день')) or \
                                
                                if dayly_chat_id and (msg_id > last_daily_id):
                                    head = f'@{source} | #{source} | #главное'
                                    dayly_frwd = envs.get(params.get('dayly_frwd'))
                                    await daily({source: {msg_id: data[source][msg_id]}}, dayly_chat_id, head, dayly_frwd)
                                    bookmarks['bookmarks']['daily'][source] = msg_id
                                data[source][msg_id]['publish'] = False
            
            if len(data[source]) < limit:
                data.pop(source)
                continue
            
            sorted_tuple = sorted(data[source].items(), key=lambda x: x[0])
            data[source] = dict(sorted_tuple)

            # all_ids.sort()
            m_ids = list(data[source].keys())
            
            if m_ids:
                # print(m_ids[0], ' - ', m_ids[-1])
                if all_ids[0] > last_id:
                    sources.insert(j + 1, f'{source}?before={m_ids[0]}')
                    # sources.append(f'{source}?before={m_ids[0]}')
                else:
                    bookmarks['bookmarks']['regular'][source] = m_ids[-1]
                
            j += 1
            await asyncio.sleep(3)
        
        bookmarks['date'] = str(datetime.now())
        await bm(src='telegram', data=bookmarks)
        
        if data.get('tele_eve'):
            data.pop('tele_eve')
        
        for m in data.keys():
            head = f'@{m} | #{m} | #новости'
            msg = await making({m: data[m]}, head, footer=envs['news_footer'])
            # msgs.append(msg)
            await sending(msg, chat_id=chat_id)
