if __name__ == "__main__":
    from impdirs import insimpdirs
    insimpdirs()

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import time

import config.config as cfg
import tools.mongodb as db
import defs.common as common


async def getrbcecnfin():
    headlist = ['RBCeconomy', 'RBCfin']
    # headlist = []
    # data = {}
    # i = 3
    data = await getrbceconomy(headlist)
    # for item in tmpheadlist:
    #     headlist.append(item)
    #     i += 1
    #     time.sleep(3)
    return(headlist, data)

async def getrbceconomy(headlist):
    # получаем id последней новости
    data = {}
    k = 0
    srcid = 3
    for z in headlist:
        bm = k
        head = z
        url = cfg.urls[head]['url']
        lId = db.find_doc('bookmarks', {'title': head}, False)['newid']

        # получаем данные с сайта
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        # получаем из бд номер последней новсти для продолжения нумерации
        # try:
        #     lastitem = db.getsortitem('news', {'source': head}, [('_id', -1)])
        #     n = lastitem['N'] - 1
        #     rnd = lastitem['round'] + 1
        # except:
        #     n = 0
        #     rnd = 0

        # парсим новости
        content = soup.find('div', class_='l-row js-load-container')
        i = 0
        j = 0
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
                        data[k] = {'srcid': srcid,
                                'source': head,
                                # 'round': rnd,
                                # 'N': n,
                                'id': code,
                                'text': title,
                                'link': link,
                                'date': datetime.now()
                                }  # записываем в бд
                        # db.ins_doc('news', data, False)
                        # n -= 1
                        k += 1
                    else:
                        break  # выходим из цикла если эту новость уже парсили
                j += 1
            i += 1

        # записываем id последней новости в бд
        if j > 0:
            try:
                # newid = db.getsortitem('news', {'source': head, 'round': rnd}, [('_id', 1)])[
                #     'id']  # получаем id последней новсти
                newid = data[bm]['id']
                doc = {'newid': newid, 'date': datetime.now()}
                db.upd_doc('bookmarks', {'title': head},
                        doc, False)  # записываем id в бд
            except:
                pass
        srcid += 1
        time.sleep(3)
    return data

async def msgrbcecnfin():
    # получаем время и дату
    tmpDate = await common.get_time()
    wd = tmpDate['msk_wd']
    date = tmpDate['msk_date_tod']

    # определяем текст сообщения (заголовок и конец)
    oldmsg = '<b>Экономика и финансы:</b>\n\n'
    newmsg = ''
    endmsg = '\nИсточник: rbc.ru' + \
        '\n\n#<b>финансы</b> #экономика #rbc #рбк #сводка #новости' + cfg.bot_msg_tail
    lenmsg = 122  # кол-во сиволов начального сообщения

    # получаем данные из data.json
    msgdata = {}
    # elems = []
    yy = await getrbcecnfin()
    head, olddata = yy[0], yy[1]
    if not len(olddata):
        return
    
    data = await common.sort_dict(olddata, 'key', '', True)
    # for i in headlist:
    #     elems.append({'source': i})

    # elems = {'$or': elems}
    # data = list(db.sort_doc('news', elems, [
    #             ('round', 1), ('N', 1)], True))
        
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

    # очищаем бд
    # db.del_doc('news', elems, True)
    return msgdata


if __name__ == "__main__":
    test = msgrbcecnfin()
    print(test)
