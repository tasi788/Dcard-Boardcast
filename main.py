import os
from time import sleep
from html import escape

import redis
import requests
import telegram
import telegram.error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

bot = telegram.Bot(os.environ.get(
    'token', None))
client = redis.from_url('redis://redis:6379')
channel_id = os.environ.get('channel_id', None)
tdc = os.environ.get('tdc', None)


def fetch():
    url = 'https://www.dcard.tw/_api/forums/sex/posts?popular=false&limit=80'
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return False
    else:
        try:
            r.json()
            return r.json()
        except:
            return False


def boardcast():
    '''
    [pic]
    title(url)
    body(text)
    '''
    fresh = fetch()
    if fresh == None:
        return
    for x in fresh:
        result = client.lrange('dcard', 0, -1)
        post_id = x['id']
        if str(post_id).encode() not in result:
            try:
                body = x['excerpt']
                captions = f'<b>{escape(x["title"])}</b>\n' \
                           f'#{post_id}\n' \
                           f'{escape(body)}\n'
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
                    '前往原始文章', url=f'https://www.dcard.tw/f/sex/p/{post_id}')]])

                if x['media']:
                    if len(x['media']) >= 2:
                        # telegram.InputMediaPhoto
                        photo_url_list = list(x['url'] for x in x['media'])
                        send_list, tmp_list = [], []
                        for x in photo_url_list:
                            if len(tmp_list) >= 9:
                                send_list.append(tmp_list)
                                tmp_list = []
                            else:
                                tmp_list.append(telegram.InputMediaPhoto(x))
                        if send_list == []:
                            send_list = [tmp_list]
                        for y in send_list:
                            send = bot.send_media_group(channel_id, y)
                        bot.send_message(
                            channel_id, captions, parse_mode='html', disable_web_page_preview=True, reply_to_message_id=send[-1].message_id, reply_markup=keyboard)

                    else:
                        bot.send_photo(channel_id, x['media'][0]['url'], caption=captions,
                                       parse_mode='html', disable_web_page_preview=True, reply_markup=keyboard)
                else:
                    bot.send_message(
                        channel_id, captions, parse_mode='html', disable_web_page_preview=True, reply_markup=keyboard)
            except telegram.error.TimedOut:
                sleep(120)
            except Exception as e:
                # raise
                bot.send_message(tdc, str(e), reply_markup=keyboard)
            else:
                # pass
                client.lpush('dcard', post_id)


while True:
    boardcast()
    sleep(300)
