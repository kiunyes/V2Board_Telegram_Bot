import bot
from handler import MysqlUtils
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Conf:
    desc = '推送新工单'
    method = 'repeating'
    interval = 60


config = bot.config['bot']
ticket_total = 0
ticket_status = []

mapping = {
    'Level': ['低', '中', '高']
}


def onQuery(sql):
    try:
        db = MysqlUtils()
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


def getNewTicket():
    global ticket_total
    global ticket_status
    result = onQuery("SELECT id,user_id FROM v2_ticket_message")
    if ticket_total != 0 and len(result) > ticket_total:
        for i in range(ticket_total, len(result)):
            ticket = result[i]
            getUser = onQuery('SELECT is_admin,is_staff FROM v2_user WHERE `id` = %s' %
                              ticket[1])[0]
            if getUser[0] == 0 and getUser[1] == 0:
                ticket_status.append(ticket[0])
    ticket_total = len(result)


def onTicketData(current_ticket):
    User = onQuery('SELECT email FROM v2_user WHERE `id` = %s' %
                   current_ticket[1])[0][0]
    getTitle = onQuery('SELECT subject,level FROM v2_ticket WHERE `id` = %s' %
                       current_ticket[2])[0]
    Subject = getTitle[0]
    Level = mapping['Level'][getTitle[1]]

    text = '📠*新的工单*\n\n'
    text = f'{text}👤*用户*：`{User}`\n'
    text = f'{text}📩*主题*：{Subject}\n'
    text = f'{text}🔔*级别*：{Level}\n'
    text = f'{text}🧾*内容*：{current_ticket[3]}\n'
    keyboard = [[InlineKeyboardButton(
        text='回复工单', url=f"{config['website']}/admin#/ticket/{current_ticket[2]}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


async def exec(context: ContextTypes.DEFAULT_TYPE):
    getNewTicket()
    global ticket_status
    if len(ticket_status) > 0:
        for i in ticket_status:
            current_ticket = onQuery(
                "SELECT id,user_id,ticket_id,message FROM v2_ticket_message WHERE id = %s" % i)
            text, reply_markup = onTicketData(current_ticket[0])
            for admin_id in config['admin_id']:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            ticket_status.remove(i)
