import os
import json
import boto3
import asyncio
import requests
from bs4 import BeautifulSoup

import config as cfg

token = os.environ.get('TOKEN')
news_chan = os.environ.get('NEWS_CHAN')
summ_chan = os.environ.get('SUMM_CHAN')
log_chan = os.environ.get('LOG_CHAN')
opsp_chan = os.environ.get('OPSP_CHAN')
bm_path = os.environ.get('BM_PATH')
bucket_path = os.environ.get('BUCKET_PATH')
news_footer = os.environ.get('NEWS_FOOTER')
summ_footer = os.environ.get('SUMM_FOOTER')
# tzone = os.environ.get('TZONE')

envs = {
    'news_chan': news_chan,
    'summ_chan': summ_chan,
    'opsp_chan': opsp_chan,
    'news_footer': news_footer,
    'summ_footer': summ_footer,
}

tg_link = cfg.urls['telegram']
pips = cfg.pips

cwd = os.getcwd().split('/')[1]
hosting = True if cwd == 'var' else False

async def replacing(text, replacements, spell=False):
    if text is None:
        return
    if spell:
        text = ''.join([replacements.get(c, c) for c in text])
    else:
        for item in replacements:
            text = text.replace(item, replacements[item])
    return text


async def get_balls(num):
    if num > 0:
        sign = '🟢'
    elif num < 0:
        sign = '🔴'
    else:
        sign = '🟡'
    return sign


async def dec_place(num):
    # locale.setlocale(locale.LC_ALL, 'ru_RU.utf8') #ru_RU.UTF-8 for Mac
    # val = '{:n}'.format(num)
    val = '{:,.2f}'.format(num).replace(',', ' ')
    return val


async def aws_s3_dupload(src, to, dl):
    s3 = boto3.resource('s3')
    mybucket = 'my-work-frt-bucket'
    if dl:
        s3.meta.client.download_file(mybucket, src, to)
    else:
        s3.meta.client.upload_file(src, mybucket, to)


async def save_bm(src):
    confile = f'{bm_path}{src}.json'
    if hosting:
        await aws_s3_dupload(f'{bucket_path}/bm/{src}.json', confile, True)
    with open(confile, 'r') as f:
        text = f.read()
    await send_telegram(text, log_chan)


async def bm(src, data=None):
    confile = f'{bm_path}{src}.json'
    if data:
        with open(confile, 'w+') as f:
            json.dump(data, f)
        
        if hosting:
            await aws_s3_dupload(confile, f'{bucket_path}/bm/{src}.json', False)
    
    else:
        if hosting:
            await aws_s3_dupload(f'{bucket_path}/bm/{src}.json', confile, True)
        
        with open(confile, 'r') as f:
            data = json.load(f)
    return data


async def making(data, head, footer, header=True):
    new_data = []
    for source in data.keys():
        pip = pips.get(source, '🔹')
        # source_link = link.format(source)
        # head = f'#{source} | {source_link}{hashtag}\n'
        msg = ''
        if data[source]:
            i = 0
            for n in data[source]:
                if data[source][n]['publish']:
                    if header:
                        text = data[source][n]['header']
                        soup = BeautifulSoup(text, 'html.parser').text
                        if len(soup) > 250:
                            text = soup[:250] + '...'
                    else:
                        text = data[source][n]['html_text']
                    lnk = data[source][n]['link']
                    item = f'{pip}{text} / <a href="{lnk}">read</a>\n\n'
                    if i <= 15:
                        msg = f'{msg}{item}'
                        i += 1
                    else:
                        msg = f'{head}\n\n{msg}{head}\n@{footer}'
                        new_data.append(msg)
                        i = 0
                        msg = f'{item}'
            if msg:
                msg = f'{head}\n\n{msg}{head}\n@{footer}'
                new_data.append(msg)
    return new_data


async def sending(msgs, chat_id, forward=None):
    for msg in msgs:
        await send_telegram(msg, chat_id, forward)
        await asyncio.sleep(3)


async def frwd_telegram(message_id, chat_id=opsp_chan, from_chat_id=summ_chan):
    method = f'https://api.telegram.org/bot{token}/forwardMessage'

    r = requests.post(method, data={
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id,
        'disable_notification': True
        })

    if r.status_code != 200:
        text = json.loads(r.text)
        text.update({'from_chat_id': 'https://t.me/c/{}'.format(str(from_chat_id)[3:]), 
                    'chat_id': 'https://t.me/c/{}'.format(str(chat_id)[3:]),
                    'message_id': message_id,
                    'link': 'https://t.me/c/{}/{}'.format(str(chat_id)[3:], message_id)})
        await send_telegram(text=str(text), chat_id=log_chan, parse_mode=None)


async def send_telegram(text: str, chat_id, forward=None, parse_mode='HTML', ok=True):
    method = f'https://api.telegram.org/bot{token}/sendMessage'
    for i in range(3):
        for i in range(5):
            try:
                r = requests.post(method, data={
                "chat_id": chat_id,
                "text": text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True,
                'disable_notification': True
                })
            except requests.exceptions.ConnectionError as e:
                print(e)
                continue
            else:
                break
        if r.status_code == 200 and ok:
            if forward:
                data = r.json()
                message_id = data['result']['message_id']
                chat_id = data['result']['chat']['id']
                await frwd_telegram(message_id, forward, chat_id)
            break
        elif r.status_code == 200 and not ok:
            text = origin_text
        else:
            ok = False
            parse_mode = None
            chat_id = log_chan
            origin_text = text
            text = r.text
