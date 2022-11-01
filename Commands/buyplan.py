import asyncio
import bot
from handler import MysqlUtils
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

desc = '打开购买商店'
config = bot.config['bot']


def onQuery():
    try:
        db = MysqlUtils()
        result = db.sql_query('SELECT * FROM v2_plan WHERE `show` = 1')
    finally:
        db.close()
        return result


def getContent():
    text = '📦*购买套餐*\n\n🌐点击下方按钮来前往购买地址'
    plan = onQuery()
    keyboard = []
    url = '%s/#/plan/' % config['website']
    for i in plan:
        keyboard.append([InlineKeyboardButton(
            text=f'购买 {i[3]}', url=f"{url}{i[0]}")])
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
