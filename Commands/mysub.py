import asyncio
import bot
from handler import MysqlUtils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

desc = '获取我的订阅链接'
config = bot.config['bot']


def getContent(token):
    header = '📚*订阅链接*\n\n🔮通用订阅地址为（点击即可复制）：\n'
    tolink = '`%s/api/v1/client/subscribe?token=%s`' % (
        config['website'], token)
    buttom = '\n\n⚠️*如果订阅链接泄露请前往官网重置！*'
    keyboard = []
    text = f'{header}{tolink}{buttom}'
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
        if chat_type == 'private':
            if len(user) > 0:
                text, reply_markup = getContent(user[0][26])
                await msg.reply_markdown(text, reply_markup=reply_markup)
            else:
                await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
        else:
            if gid == config['group_id']:
                if len(user) > 0:
                    callback = await msg.reply_markdown('❌*错误*\n为了你的账号安全，请私聊我！')
                else:
                    callback = await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
                await asyncio.sleep(15)
                await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
    finally:
        db.close()
