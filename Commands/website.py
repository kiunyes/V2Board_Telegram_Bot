import asyncio
import bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

desc = '打开网站链接'
config = bot.config['bot']


def getContent():
    text = '🗺*前往网站*\n\n🌐点击下方按钮来前往网站地址'
    keyboard = [[InlineKeyboardButton(
        text='打开网站', url="%s" % config['website'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


async def exec(update, context) -> None:
    msg = update.message
    tid = msg.from_user.id
    gid = msg.chat.id
    chat_type = msg.chat.type
    if chat_type == 'private' or gid == config['group_id']:
        text, reply_markup = getContent()
        callback = await msg.reply_markdown(text, reply_markup=reply_markup)
        if chat_type != 'private':
            await asyncio.sleep(15)
            await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
