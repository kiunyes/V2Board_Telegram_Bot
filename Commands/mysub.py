import bot
from handler import MysqlUtils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

desc = '获取我的订阅链接'
config = bot.config['bot']


def getContent(uuid):
    header = '📚*订阅链接*\n\n🔮通用订阅地址为（点击即可复制）：\n'
    tolink = '`%s/api/v1/client/subscribe?token=%s`' % (
        config['website'], uuid)
    buttom = '\n\n⚠️*如果订阅链接泄露请前往官网重置！*'
    keyboard = []
    text = f'{header}{tolink}{buttom}'
    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup


async def autoDelete(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.delete_message(job.chat_id, job.data)


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user_id = msg.from_user.id
    chat_id = msg.chat_id
    chat_type = msg.chat.type
    if chat_type == 'private':
        db = MysqlUtils()
        user = db.sql_query(
            'SELECT uuid FROM v2_user WHERE `telegram_id` = %s' % user_id)
        db.close()
        if len(user) > 0:
            text, reply_markup = getContent(user[0][0])
            await msg.reply_markdown(text, reply_markup=reply_markup)
        else:
            await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
    else:
        if chat_id == config['group_id']:
            callback = await msg.reply_markdown('❌*错误*\n为了你的账号安全，请私聊我！')
            context.job_queue.run_once(
                autoDelete, 15, data=msg.id, chat_id=chat_id, name=str(msg.id))
            context.job_queue.run_once(
                autoDelete, 15, data=callback.message_id, chat_id=chat_id, name=str(callback.message_id))
