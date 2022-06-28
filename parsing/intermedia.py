if __name__ == "__main__":
    from impdirs import insimpdirs
    insimpdirs()

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

import config.config as cfg
import tools.mongodb as db
import defs.common as common


async def getmusnews():
    head = 'musicnews'
    website = cfg.urls[head]['website']

    # Парсим события с intermedia.ru
    url = website + cfg.urls[head]['url']
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # парсим новости
    div_container = soup.find_all('section', class_='news-item')
    l = db.find_doc('bookmarks', {'title': head}, False)
    lId = l['newid']
        
    i = 0
    data = {}
    a = {'\n': '', '\t': ''}
    for item in div_container:
        newid = item.attrs['data-new_id']
        if newid != lId:
            x = await common.replacing(item.text, a, False)
            y = x.split('\r')[1]
            data[i] = {
                    'id': newid,
                    'link': website + item.contents[1].attrs['href'],
                    'text': y
            }
            i += 1
        else:
            break

    if i > 0:
        try:
            doc = {'newid': data[0]['id'], 'date': datetime.now()}
            db.upd_doc('bookmarks', {'title': head},
                doc, False)  # записываем id в бд
        except:
            pass
    return(head, data)


async def msgmusnews():
    head, olddata = await getmusnews()
    if not len(olddata):
        return
    
    data = await common.sort_dict(olddata, 'key', '', True)
    # определяем текст сообщения (заголовок и конец)
    oldmsg = '<b>Музыкальные новости:</b>\n\n'
    newmsg = ''
    endmsg = '\nИсточник: intermedia.ru' + \
        '\n\n#<b>музыка</b> #intermedia #сводка #новости' + cfg.bot_msg_tail
    lenmsg = 112  # кол-во сиволов начального сообщения
    msgdata = {}

    # заполняем сообщение новотями из бд
    i = 0
    j = 4 # начинаем счет entities
    for item in data:
        msgitem = '📍' + '<b>' + \
            str(data[item]['text'])[:2].replace("<", "&lt;") + '</b>' + \
            str(data[item]['text'])[2:].replace("<", "&lt;").replace('  ', ' ') + \
            ' <a href="' + data[item]['link'] + '">читать</a>\n'
        newmsg = oldmsg + msgitem  # добавляем новость к уже имеющемуся сообщению
        # кол-во символов обновленного сообщения без символов разметки
        lenitem = len(str(data[item]['text'])) + 8
        lenmsg = lenmsg + lenitem
        if lenmsg >= cfg.tg_limits['msg_lim'] or j > cfg.tg_limits['entities']:  # проверяем не привышает ли обновленное сообщение лимит телеграм или кол-во entities 100
            # если превышает записываем сообщение в словарь и обнуляем новое сообщение и счетчик символов
            msgdata[i] = oldmsg
            oldmsg = msgitem
            lenmsg = lenitem
            i += 1
            j = 4 # сбрасываем entities
        else:
            oldmsg = newmsg
            j += 2

    # добавляем к последнему сообщению концовку и записываем в msgdata
    msg = oldmsg + endmsg
    msgdata[i] = msg
    return msgdata

if __name__ == '__main__':
    print(msgmusnews())