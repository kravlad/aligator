import tweepy
import json
from bot.bot import ubot
import time
from tools.storage import settings as sets


async def send_tweets():
    """docstring."""
    auth = tweepy.OAuthHandler(
        sets['twitter']['consumer_key'], sets['twitter']['consumer_secret'])
    auth.set_access_token(sets['twitter']['access_token'],
                          sets['twitter']['access_secret'])
    api = tweepy.API(auth)

    with open('parsing/files/tweets.json', 'r') as f:
        bookmarks = json.load(f)
    sources = bookmarks.keys()
    # sources = ['MeduzaSafe','svtv_news','agents_media','istories_media','wwwproektmedia','takiedelaru','the_ins_ru','villagemsk','mediazzzona','tvrain','novaya_gazeta']

    for user_id in sources:
        link = 'https://twitter.com/{user_id}/status/'.format(user_id=user_id)
        msg = '#{user_id} | <a href="https://twitter.com/{user_id}">{user_id}</a>\n'.format(
            user_id=user_id)
        tweets = api.user_timeline(
            screen_name=user_id, since_id=bookmarks[user_id])
        if tweets:
            bookmarks[user_id] = tweets[0].id
            i = 1
            for tweet in reversed(tweets):
                if i <= 13:
                    msg = '{msg}\n🔹{n}. {tweet} | <a href="{lnk}{twid}">tweet</a>\n'.format(
                        msg=msg, tweet=tweet.text, n=i, lnk=link, twid=tweet.id)
                    i += 1
                else:
                    await ubot.send_message(sets['sandbox']['id'], msg, disable_notification=True, disable_web_page_preview=True)
                    i = 1
                    msg = '#{user_id} | <a href="https://twitter.com/{user_id}">{user_id}</a>\n'.format(
                        user_id=user_id)
                    msg = '{msg}\n🔹{n}. {tweet} | <a href="{lnk}{twid}">tweet</a>\n'.format(
                        msg=msg, tweet=tweet.text, n=i, lnk=link, twid=tweet.id)
                    i += 1
            await ubot.send_message(sets['sandbox']['id'], msg, disable_notification=True, disable_web_page_preview=True)
        time.sleep(3)

    with open('parsing/files/tweets.json', 'w') as f:
        json.dump(bookmarks, f)

if __name__ == "__main__":
    import asyncio
    asyncio.run(send_tweets())


# 1536795751703056384
