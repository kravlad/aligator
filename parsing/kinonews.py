if __name__ == "__main__":
    from impdirs import insimpdirs
    insimpdirs()

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

import tools.mongodb as db
import config.config as cfg
import defs.common as common

async def getkino():
    head = 'kinonews'
    website = cfg.urls[head]['website']
    lId = db.find_doc('bookmarks', {'title': head}, False)['newid']

    # Парсим события с kino.ru
    url = website + cfg.urls[head]['url']
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    #парсим новости
    div_container = soup.find_all('div', class_= 'anons-title-new')

    i = 0
    data = {}
    for item in div_container:
        link = website + item.next_element.next_element.attrs['href']
        newid = link[29:-1]
        if lId != newid:
            data[i] = {
                        'id': newid,
                        'link': link,
                        'text': item.text
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


async def msgkino():
    head, olddata = await getkino()
    if not len(olddata):
        return
    
    data = await common.sort_dict(olddata, 'key', '', True)
    # определяем текст сообщения (заголовок и конец)
    oldmsg = '<b>Новости из мира кино:</b>\n\n'
    newmsg = ''
    endmsg = '\nИсточник: kinonews.ru' + \
        '\n\n#<b>кино</b> #kinonews #сводка #новости' + cfg.bot_msg_tail
    lenmsg = 110  # кол-во сиволов начального сообщения
    msgdata = {}

    # заполняем сообщение новотями из бд
    i = 0
    j = 4 # начинаем счет entities
    for item in data:
        msgitem = '📍' + '<b>' + \
            str(data[item]['text'])[:2].replace("<", "&lt;") + '</b>' + \
            str(data[item]['text'])[2:].replace("<", "&lt;") + \
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
    

if __name__ == "__main__":
    test = msgkino()
    # # i = 0
    # # while i < (len(test)):
    # #     print(test[i])
    # #     i += 1
    print(test)