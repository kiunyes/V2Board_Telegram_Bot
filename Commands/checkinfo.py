import bot
import time
from handler import MysqlUtils
from telegram import Update
from telegram.ext import ContextTypes

desc = '回复某人来获取使用信息'
config = bot.config['bot']


def onQuery(sql):
    try:
        db = MysqlUtils()
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


def getContent(user):
    text = '📋*个人信息*\n'
    User_id = user[0]
    Register_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(user[1]))
    Plan_id = onQuery('SELECT name FROM v2_plan WHERE id = %s' %
                      user[2])[0][0]
    Expire_time = '长期有效'
    if user[3] is not None:
        Expire_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(user[3]))
    Data_Upload = round(user[4] / 1024 / 1024 / 1024, 2)
    Data_Download = round(user[5] / 1024 / 1024 / 1024, 2)
    Data_Total = round(user[6] / 1024 / 1024 / 1024, 2)
    Data_Last = round(
        (user[6]-user[5]-user[4]) / 1024 / 1024 / 1024, 2)
    Data_Time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(user[7]))

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


async def autoDelete(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.delete_message(job.chat_id, job.data)


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user_id = msg.from_user.id
    chat_id = msg.chat_id
    chat_type = msg.chat.type

    if user_id in config['admin_id'] and (chat_type == 'private' or chat_id == config['group_id']):
        if msg.reply_to_message:
            reply_id = msg.reply_to_message.from_user.id
            user = onQuery(
                'SELECT id,created_at,plan_id,expired_at,u,d,transfer_enable,t FROM v2_user WHERE `telegram_id` = %s' % reply_id)
            if len(user) > 0:
                if user[0][2] is not None:
                    text = getContent(user[0])
                    callback = await msg.reply_markdown(text)
                else:
                    callback = await msg.reply_markdown('❌*错误*\n该账号没有购买过订阅！')
            else:
                callback = await msg.reply_markdown('❌*错误*\n该用户未绑定 Telegram 账号')
        else:
            callback = await msg.reply_markdown('❌*错误*\n你需要回复一条消息来获取信息！')
        if chat_type != 'private':
            context.job_queue.run_once(
                autoDelete, 15, data=msg.id, chat_id=chat_id, name=str(msg.id))
            context.job_queue.run_once(
                autoDelete, 15, data=callback.message_id, chat_id=chat_id, name=str(callback.message_id))

    else:
        await msg.reply_markdown('❌*错误*\n你无法使用该指令！')
