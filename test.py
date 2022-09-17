import asyncio
from telegram import Update
from telegram.ext import CallbackContext


class infomation:
    desc = '开始使用 Bot'


def getInfo():
    return infomation


async def exec(update: Update, context: CallbackContext) -> None:
    msg = update.message
    tid = msg.from_user.id
    gid = msg.chat.id
    chat_type = msg.chat.type

    if chat_type == 'private':
        callback = await msg.reply_markdown('欢迎使用这个Bot，绑定请输入 /bind 账号 密码')
        await asyncio.sleep(15)
        await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
