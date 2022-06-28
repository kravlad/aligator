import time
import tools.mongodb as db

from defs.specific import msg_to_dict_from_bot
from parsing.politic import msgrbcpolitic, getrbcpolitic
from parsing.calend import msgcalev, msgcalpers
from parsing.busnfin import msgrbcbusiness
from parsing.economy import msgrbcecnfin
from parsing.musicnews import msgmusnews
from parsing.finance import msgfin
from parsing.kino import msgkino
import config.privately as priv
from tools.storage import markups

p_funcs = {
    'finance': {'module': 'p_fin', 'parse': True, 'pfunc': msgfin, 'preparse': False, 'prepfunc': None},
    'calendev': {'module': 'p_calend', 'parse': True, 'pfunc': msgcalev, 'preparse': False, 'prepfunc': None},
    'calendpers': {'module': 'p_calend', 'parse': True, 'pfunc': msgcalpers, 'preparse': False, 'prepfunc': None},
    'kinonews': {'module': 'p_kino', 'parse': True, 'pfunc': msgkino, 'preparse': False, 'prepfunc': None},
    'musicnews': {'module': 'p_mNews', 'parse': True, 'pfunc': msgmusnews, 'preparse': False, 'prepfunc': None},
    'rbcpolitic': {'module': 'p_polit', 'parse': True, 'pfunc': msgrbcpolitic, 'preparse': True, 'prepfunc': getrbcpolitic},
    'rbcbus': {'module': 'p_busines', 'parse': True, 'pfunc': msgrbcbusiness, 'preparse': False, 'prepfunc': None},
    'rbcecnfin': {'module': 'p_economy', 'parse': True, 'pfunc': msgrbcecnfin, 'preparse': False, 'prepfunc': None}
}


async def custom_parser(args):
    data = {}
    # try:
    f = p_funcs[args]['pfunc']
    messages = await f()
    data = await msg_to_dict_from_bot({'message': messages})
# except:
    #     pass
    return data


async def run_parser():
    titles = {}
    i = 1
    for f in p_funcs:
        if p_funcs[f]['parse']:
            try:
                data = await p_funcs[f]['pfunc']()
                # data = getattr(globals()[func['module']], func['pfunc'])()
                title = list(data.keys())[0]
                titles[i] = title
                yield data[title]
                time.sleep(3)
                i += 1
            except:
                pass


async def run_preparser():
    titles = {}
    i = 1
    for f in p_funcs:
        func = p_funcs[f]
        if func['preparse']:
            title = await p_funcs[f]['prepfunc']()
            # title = getattr(globals()[func['module']], func['prepfunc'])()
            for item in title:
                titles[i] = item
                i += 1
            time.sleep(3)
    return titles


async def run_parser_test():
    test = await msgcalev()
    return test

async def msg_to_db_from_bot(args):
    for i in args:
        data = await custom_parser(i)
        if data:
            db.ins_doc('messages', data.get('data'), data.get('many'))

async def parse(**kwargs):
    message = kwargs.get('message')
    params = message.text[7:].split(',')
    srcs = ['finance','calendev','calendpers','kinonews','musicnews','rbcpolitic','rbcbus','rbcecnfin']
    x = []
    for i in params:
        x.append(srcs[int(i)])
    await msg_to_db_from_bot(x)

async def preparse(**kwargs):
    bot = kwargs.get('bot')
    titles = await run_preparser()
    msg = 'SysMsg:\ncmd[<i>Preparse</i>]\n'
    for title in titles:
        msg = msg + '\n' + str(title) + '. <b>' + titles[title] + '</b> is <b>done</b>👍'
    await bot.send_message(priv.sandbox_id, msg, disable_notification=True, reply_markup=markups.get('sndbxlog'))








if __name__ == "__main__":
    
    # msg_to_db_from_bot(['finance'])
    msg_to_db_from_bot(['calendev','calendpers','kinonews'])

    
    # test = run_preparser()
    # print(test)
    # pass
