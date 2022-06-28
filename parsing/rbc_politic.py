if __name__ == "__main__":
    from impdirs import insimpdirs
    insimpdirs()

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

import config.config as cfg
import tools.mongodb as db
import defs.common as common


async def getrbcpolitic():
    # получаем id последней новости из бд
    head = 'RBCpolitic'
    d = {'title': head}
    x = db.find_doc('bookmarks', d, False)
    lId = x['newid']

    # получаем данные с сайта
    url = cfg.urls[head]['url']
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # получаем из бд номер последней новсти для продолжения нумерации
    try:
        lastitem = db.getsortitem('news', {'source': head}, [('_id', -1)])
        n = lastitem['N'] - 1
        rnd = lastitem['round'] + 1
    except:
        n = 0
        rnd = 0

    # парсим новости
    content = soup.find('div', class_='l-row js-load-container')
    i = 0
    j = 0
    data = []
    for item in content:  # берем каждую 3ю(?) запись
        if i % 2 != 0:
            if j % 2 == 0:
                # получаем ссылку
                link = item.find('meta', {'itemprop': 'url'}).attrs['content']
                code = link[-24:]  # получаем id

                # проверяем на соответсвиее id последней новости с предыдущего парсинга (чтобы не дублировались)
                if lId != code:
                    title = item.find(
                        'meta', {'itemprop': 'name'}).attrs['content']  # получаем содердание новости
                    doc = {'srcid': 1,
                            'source': head,
                            'round': rnd,
                            'N': n,
                            'id': code,
                            'text': title,
                            'link': link,
                            'date': datetime.now()
                            }  # записываем в бд
                    data.append(doc)
                    n -= 1
                else:
                    break  # выходим из цикла если эту новость уже парсили
            j += 1
        i += 1
    if data:
        db.ins_doc('news', data, True)

    # записываем id последней новости в бд
    if j > 0:
        try:
            # newid = db.getsortitem('news', {'source': head, 'round': rnd}, [('_id', 1)])[
            #     'id']  # получаем id последней новсти
            newid = data[0]['id']  # получаем id последней новсти
            doc = {'newid': newid, 'date': datetime.now()}
            db.upd_doc('bookmarks', {'title': head},
                    doc, False)  # записываем id в бд
        except:
            pass
    return [head]


async def msgrbcpolitic():
    # получаем время и дату
    tmpDate = await common.get_time()
    wd = tmpDate['msk_wd']
    date = tmpDate['msk_date_tod']

    # определяем текст сообщения (заголовок и конец)
    oldmsg = '<b>Немного о политике:</b>\n\n'
    newmsg = ''
    endmsg = '\nИсточник: rbc.ru' + \
        '\n\n#<b>политика</b> #rbc #рбк #сводка #новости' + cfg.bot_msg_tail
    lenmsg = 111  # кол-во сиволов начального сообщения

    # получаем данные из бд
    xhead = await getrbcpolitic()
    head = xhead[0]
    msgdata = {}
    v = db.sort_doc('news', {'source': head}, [('round', 1), ('N', 1)], True)
    data = list(v)
    
    if not len(data):
        return
    
    # заполняем сообщение новотями из бд
    i = 0
    j = 4 # начинаем счет entities
    for item in data:
        msgitem = '📍' + '<b>' + \
            str(item['text'])[:2].replace("<", "&lt;") + '</b>' + \
            str(item['text'])[2:].replace("<", "&lt;") + \
            ' <a href="' + item['link'] + '">читать</a>\n'
        newmsg = oldmsg + msgitem  # добавляем новость к уже имеющемуся сообщению
        # кол-во символов обновленного сообщения без символов разметки
        lenitem = len(str(item['text'])) + 8
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

    # очищаем бд
    db.del_doc('news', {'source': head}, True)
    return msgdata


if __name__ == "__main__":
    test = msgrbcpolitic()
    print(test)
