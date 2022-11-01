import asyncio
import bot
import time
import pytz
import datetime
from handler import MysqlUtils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

desc = '获取我的使用信息'
config = bot.config['bot']

# TineZone
tz = pytz.timezone('Asia/Shanghai')


def onQuery(uid):
    try:
        db = MysqlUtils()
        result = db.sql_query(
            'SELECT * FROM v2_stat_user WHERE `user_id` = %s' % uid)
    finally:
        db.close()
        return result


def getContent(uid):
    current_date = datetime.datetime.now(tz).strftime("%Y-%m-%d")
    stat = onQuery(uid)
    today_usage = 0
    for i in stat:
        today_date = i[6]
        ltime = time.localtime(today_date)
        today_date = time.strftime("%Y-%m-%d", ltime)
        if today_date == current_date:
            today_usage = today_usage + i[4]
    today_usage = round(today_usage / 1024 / 1024 / 1024, 2)

    text = f'📚*今日流量*\n\n📈本日总计使用流量为：*{today_usage} GB*\n'
    text = f'{text}\n📜*详细流量记录请点击下方按钮*'
    keyboard = [[InlineKeyboardButton(
        text='流量明细', url="%s/#/traffic" % config['website'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup


async def exec(update, context) -> None:
    msg = update.message
    tid = msg.from_user.id
    gid = msg.chat.id
    chat_type = msg.chat.type
    try:
        db = MysqlUtils()
        user = db.sql_query(
            'SELECT * FROM v2_user WHERE `telegram_id` = %s' % tid)
        if chat_type == 'private' or gid == config['group_id']:
            if len(user) > 0:
                if user[0][13] != 0 and user[0][14] != 0:
                    text, reply_markup = getContent(user[0][0])
                    callback = await msg.reply_markdown(text, reply_markup=reply_markup)
                else:
                    callback = await msg.reply_markdown('❌*错误*\n你还没有消耗过流量！')
            else:
                callback = await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
            if chat_type != 'private':
                await asyncio.sleep(15)
                await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
    finally:
        db.close()
