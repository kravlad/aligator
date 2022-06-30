import asyncio
import requests
import json
import boto3
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
from configs.storage import settings as sets

news_chan = sets['news_chan']
log_chan = sets['log_chan']
hosting = sets['hosting']
tg_link = sets['cfg'].links['telegram']

pips = {
    'telegram': '🔹',
    'kinonews': '🎬',
    'intermedia': '🎵',
    
}

async def replacing(text, replacements, spell=False):
    if text is None:
        return
    if spell:
        text = ''.join([replacements.get(c, c) for c in text])
    else:
        for item in replacements:
            text = text.replace(item, replacements[item])
    return text

async def get_time():
    d_time = {}
    d_time['timenow'] = datetime.now()
    d_time['msk_now'] = datetime.now(pytz.timezone('Europe/Moscow'))
    d_time['msk_yest'] = d_time['msk_now'] - timedelta(hours=24)
    d_time['msk_date_tod'] = d_time['msk_now'].strftime('%d.%m.%Y')
    d_time['msk_date_yest'] = d_time['msk_yest'].strftime('%d.%m.%Y')
    d_time['msk_wd'] = cfg.weekday[int(d_time['msk_now'].strftime('%w'))]
    d_time['logdate'] = d_time['timenow'].strftime('%Y-%m-%d')

    d_time['msktime'] = datetime(
        int(d_time['msk_now'].strftime('%Y')),
        int(d_time['msk_now'].strftime('%m')),
        int(d_time['msk_now'].strftime('%d')),
        int(d_time['msk_now'].strftime('%H')),
        int(d_time['msk_now'].strftime('%M')),
        int(d_time['msk_now'].strftime('%S'))
    )
    dif = (d_time['msktime'] - d_time['timenow']).total_seconds()
    d_time['diff'] = int(divmod(dif, 3600)[0]) + 1
    d_time['dateid'] = int(d_time['msk_now'].strftime('%Y%m%d%H%M%S'))
    d_time['dateidtxt'] = str(d_time['msk_now'].strftime('%Y-%m-%d-%H-%M-%S'))
    d_time['servdateidtxt'] = str(
        d_time['timenow'].strftime('%Y-%m-%d-%H-%M-%S'))
    d_time['sched'] = (datetime.now() + timedelta(minutes=60)).strftime(f'%Y-%m-%d %H:15:00')
    d_time['msklist'] = [int(d_time['msk_now'].strftime('%Y')),
                        int(d_time['msk_now'].strftime('%m')),
                        int(d_time['msk_now'].strftime('%d'))]
    
    d_time['mskylist'] = [int(d_time['msk_yest'].year),
                        int(d_time['msk_yest'].month),
                        int(d_time['msk_yest'].day)]
    return d_time


async def get_balls(num):
    if num > 0:
        sign = '🟢'
    elif num < 0:
        sign = '🔴'
    else:
        sign = '🟡'
    return sign


async def send_telegram(text: str, chat_id=news_chan):
    # token = sets['token']
    # url = "https://api.telegram.org/bot"
    # channel_id = "@ИМЯ_КАНАЛА"
    # url += sets['token']
    # method = url + "/sendMessage"
    method = 'https://api.telegram.org/bot{}/sendMessage'.format(sets['token'])

    r = requests.post(method, data={
        "chat_id": chat_id,
        "text": text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
        'disable_notification': True
        })

    if r.status_code != 200:
        requests.post(method, data={
                                "chat_id": log_chan,
                                "text": r.text,
                                'parse_mode': 'HTML',
                                'disable_web_page_preview': True,
                                'disable_notification': True
        })
        save_bm(sets['file_cfg']['bm_path']['telegram'])
        raise Exception(r.text)


async def save_bm(src):
    if hosting:
        confile = f'/tmp/{src}.json'
        await aws_s3_dupload(f'aligator/bm/{src}.json', confile, True)
    else:
        confile = f'files/{src}.json'
    with open(confile, 'r') as f:
        text = f.read()
    await send_telegram(text, log_chan)


async def aws_s3_dupload(src, to, dl):
    s3 = boto3.resource('s3')
    mybucket = 'my-work-frt-bucket'
    if dl:
        s3.meta.client.download_file(mybucket, src, to)
    else:
        s3.meta.client.upload_file(src, mybucket, to)


async def bm(src, data=None):
    # if hosting:
    #     confile = f'/tmp/{src}.json'
    # else:
    #     confile = f'files/{src}.json'
    
    x = '/tmp' if hosting else 'files'
    confile = f'{x}/{src}.json'
    
    if data:
        with open(confile, 'w+') as f:
            json.dump(data, f)
        
        if hosting:
            await aws_s3_dupload(confile, f'aligator/bm/{src}.json', False)

    else:
        if hosting:
            await aws_s3_dupload(f'aligator/bm/{src}.json', confile, True)
        
        with open(confile, 'r') as f:
            data = json.load(f)
    return data


async def making(data, link='@{}', header=True, hashtag=''):
    new_data = []
    for source in data.keys():
        pip = pips.get(source, '🔹')
        source_link = link.format(source)
        head = f'#{source} | {source_link}{hashtag}\n'
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
                    item = f'\n{pip}{text} / <a href="{lnk}">read</a>\n'
                    if i <= 15:
                        msg = f'{msg}{item}'
                        i += 1
                    else:
                        msg = f'{head}{msg}\n{head}@rufeedsp'
                        new_data.append(msg)
                        i = 0
                        msg = f'{item}'
            if msg:
                msg = f'{head}{msg}\n{head}@rufeedsp'
                new_data.append(msg)
    return new_data


async def sending(msgs, chat_id=news_chan):
    for msg in msgs:
        await send_telegram(msg, chat_id)
        await asyncio.sleep(3)
