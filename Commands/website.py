import bot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

desc = '打开网站链接'
config = bot.config['bot']


def getContent():
    text = '🗺*前往网站*\n\n🌐点击下方按钮来前往网站地址'
    keyboard = [[InlineKeyboardButton(
        text='打开网站', url="%s" % config['website'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


async def autoDelete(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.delete_message(job.chat_id, job.data)


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    chat_id = msg.chat_id
    chat_type = update.effective_chat.type
    if chat_type == 'private' or chat_id == config['group_id']:
        text, reply_markup = getContent()
        callback = await msg.reply_markdown(text, reply_markup=reply_markup)
        if chat_type != 'private':
            context.job_queue.run_once(
                autoDelete, 15, data=msg.id, chat_id=chat_id, name=str(msg.id))
            context.job_queue.run_once(
                autoDelete, 15, data=callback.message_id, chat_id=chat_id, name=str(callback.message_id))
