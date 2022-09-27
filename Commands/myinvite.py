import asyncio
import bot
import time
import pytz
import datetime
from commands.buyplan import getContent
from handler import MysqlUtils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

desc = '获取我的使用信息'
config = bot.config['bot']

# TineZone
tz = pytz.timezone('Asia/Shanghai')


def onQuery(uid):
    try:
        db = MysqlUtils()
        result1 = db.sql_query(
            'SELECT * FROM v2_invite_code WHERE user_id = %s' % uid)
        result2 = db.count_sql_query('v2_user',sql_condition='WHERE invite_user_id = %s' % uid)
    finally:
        db.close()
        return result1, result2


def getContent(uid):
    code, times = onQuery(uid)
    text = '❌*错误*\n你还没有生成过邀请码，点击前往网站生成一个吧！'
    if len(code) > 0:
        header = '📚*邀请信息*\n\n🔮邀请地址为（点击即可复制）：\n'
        tolink = '`%s/api/v1/client/subscribe?token=%s`' % (
            config['website'], code[0][2])
        buttom = '\n\n👪*邀请人数：* %s' % times
        text = f'{header}{tolink}{buttom}'

    return text


async def exec(update, context) -> None:
    msg = update.message
    tid = msg.from_user.id
    gid = msg.chat.id
    chat_type = msg.chat.type
    try:
        db = MysqlUtils()
        user = db.sql_query(
            'SELECT * FROM v2_user WHERE `telegram_id` = %s' % tid)
        if chat_type == 'private' or gid == config['tg_group']:
            if len(user) > 0:
                text = getContent(user[0][0])
                callback = await msg.reply_markdown(text)
            else:
                callback = await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
            if chat_type != 'private':
                await asyncio.sleep(15)
                await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
    finally:
        db.close()
