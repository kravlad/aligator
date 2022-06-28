import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler # pip3 install apscheduler

from defs import send_telegram, save_bm
from configs.storage import settings as sets
from parsing.telegram import tg_parsing
# from parsing.finance import fin_parsing

funcs = {
    'telegram': tg_parsing
}

async def handler(event={}): #, context=None):
    if event.get('parse'):
        sources = event['parse'].keys()
        for src in sources:
            if funcs.get(src):
                func = funcs[src]
                arg = event['parse'][src]
                # loop = asyncio.get_event_loop().run_until_complete
                await func(arg)

    # elif event.get('get_bm'):
    #     for i in event['get_bm'].keys():
    #         confile = sets['file_cfg']['bm_path'][i]
    #         with open(confile, 'w+') as f:
    #             json.dump(event['get_bm'][i], f)

    # elif event.get('save_bm'):
    #     for i in event['save_bm']:
    #         confile = sets['file_cfg']['bm_path'][i]
    #         loop = asyncio.get_event_loop().run_until_complete
    #         loop(save_bm(confile))


if __name__ == "__main__":
    test = {"parse": {"telegram": ["svtvnews", "meduzalive"]}}
    # test = {
    #         "get_bm": {
    #             "telegram": {
    #                 "meduzalive": 63070,
    #                 "svtvnews": 10416
    #         }}}
    # test = {"save_bm": ["telegram"]}
    # handler(test)
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(handler, "interval", kwargs={'event': test}, seconds=30)
    scheduler.start()
    
    try:
        asyncio.get_event_loop().run_forever()

    except (KeyboardInterrupt, SystemExit):
            pass
    
    
    
        # scheduler.add_job(sending,
    #                         'date',
    #                         kwargs={'msgs': msgs},
    #                         run_date=run_date,
    #                         timezone=config.timezone,
    #                         misfire_grace_time=60
    #                         )    
