import asyncio
import bot
import time
from handler import MysqlUtils

desc = '获取我的使用信息'
config = bot.config['bot']


def onQuery(plan):
    try:
        db = MysqlUtils()
        result = db.sql_query('SELECT name FROM v2_plan WHERE id = %s' % plan)
    finally:
        db.close()
        return result[0][0]


def getContent(user):
    text = '📋*个人信息*\n'
    User_id = user[0]
    Register_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(user[29]))
    Plan_id = onQuery(user[23])
    Expire_time = '长期有效'
    if user[28] is not None:
        Expire_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(user[28]))
    Data_Upload = round(user[13] / 1024 / 1024 / 1024, 2)
    Data_Download = round(user[14] / 1024 / 1024 / 1024, 2)
    Data_Total = round(user[15] / 1024 / 1024 / 1024, 2)
    Data_Last = round(
        (user[15]-user[14]-user[13]) / 1024 / 1024 / 1024, 2)
    Data_Time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(user[12]))

    text = f'{text}\n🎲*UID：* {User_id}'
    text = f'{text}\n⌚️*注册时间：* {Register_time}'
    text = f'{text}\n📚*套餐名称：* {Plan_id}'
    text = f'{text}\n📌*到期时间：* {Expire_time}'
    text = f'{text}\n'
    text = f'{text}\n📤*上传流量：* {Data_Upload} GB'
    text = f'{text}\n📥*下载流量：* {Data_Download} GB'
    text = f'{text}\n📃*剩余流量：* {Data_Last} GB'
    text = f'{text}\n📜*总计流量：* {Data_Total} GB'
    text = f'{text}\n📊*上次使用：* {Data_Time}'
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
                if user[0][23] is not None:
                    text = getContent(user[0])
                    callback = await msg.reply_markdown(text)
                else:
                    callback = await msg.reply_markdown('❌*错误*\n你的账号没有购买过订阅！')
            else:
                callback = await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
            if chat_type != 'private':
                await asyncio.sleep(15)
                await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
    finally:
        db.close()
