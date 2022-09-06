#!/usr/bin/env python

import logging
import requests
import pymysql
import time
import threading
from sshtunnel import SSHTunnelForwarder

from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext

import Message
import Config
import Command

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = Bot(Config.bot_token)

# Enable ssh
v2_db_port = Config.v2_db_port
if Config.ssh_enable is True:
    ssh = SSHTunnelForwarder(
        ssh_address_or_host=(Config.ssh_ip, Config.ssh_port),
        ssh_username=Config.ssh_user,
        ssh_password=Config.ssh_pass,
        remote_bind_address=(Config.v2_db_url, v2_db_port))
    ssh.start()
    v2_db_port = ssh.local_bind_port
# Database Connection
db = pymysql.connect(host=Config.v2_db_url,
                     user=Config.v2_db_user,
                     password=Config.v2_db_pass,
                     database=Config.v2_db_name,
                     port=v2_db_port,
                     autocommit=True)

current_list = {
    'ticket': 0,
    'order': 0
}


def s(update: Update, context: CallbackContext) -> None:
    # Debugging
    print(update)


def ping(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    text = '💥*嘭*\n'
    utid = f'{text}\n你的ID为：`{tid}`'

    if chat_type == 'private':
        reply(utid)
    else:
        group = f'\n群组ID为：`{gid}`'
        if update.message.from_user.is_bot is False:
            callback = reply(f'{utid}{group}')
        else:
            callback = reply(f'{text}{group}')
        Module.autoDelete(update, callback.chat.id, callback.message_id)


def bind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, tig = Module.getTGbyMail(email)
                    if result is False:
                        reply(Message.Success_Bind)
                        Command.onBind(tid, email)
                    else:
                        reply(Message.Error_BindOther)
                else:
                    reply(Message.Error_Login)
            else:
                reply(Message.Error_BindUsage)
        else:
            reply(Message.Error_BindAlready)
    else:
        if gid == Config.tg_group:
            if result is False:
                callback = reply(Message.Error_PrivateOnly)
            else:
                callback = reply(Message.Error_BindAlready)
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def unbind(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply(Message.Error_NotBind)
        else:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Module.onLogin(email, password) is True:
                    result, id = Module.getTGbyMail(email)
                    if id == tid:
                        reply(Message.Success_UnBind)
                        Command.onUnBind(email)
                    else:
                        reply(Message.Error_UnBindNoMatch)
                else:
                    reply(Message.Error_Login)
            else:
                reply(Message.Error_UnBindUsage)
    else:
        if gid == Config.tg_group:
            if result is False:
                callback = reply(Message.Error_NotBind)
            else:
                callback = reply(Message.Error_PrivateOnly)
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def mysub(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply(Message.Error_NotBind)
        else:
            # 根据客户端
            text, reply_markup = Command.onMySub(user['token'])
            reply(text)
    else:
        if gid == Config.tg_group:
            if result is False:
                callback = reply(Message.Error_NotBind)
            else:
                callback = reply(Message.Error_PrivateOnly)
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myinfo(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            if user['plan'] is not None:
                text = Command.onMyInfo(user)
                callback = reply(text)
            else:
                callback = reply(Message.Error_MyInfoNotFound)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myusage(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)
    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            result, statlist = Module.getUserStat(user['uid'])
            if result is True:
                text, reply_markup = Command.onMyUsage(statlist)
                callback = reply(text, reply_markup=reply_markup)
            else:
                callback = reply(Message.Error_MyUsageNotFound)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def myinvite(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    tid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    result, user = Module.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            invite_code = Module.getInviteCode(user['uid'])
            if invite_code is not None:
                invite_times = Module.getInviteTimes(user['uid'])
                text = Command.onMyInvite(invite_code, invite_times)
                callback = reply(text)
            else:
                keyboard = [[InlineKeyboardButton(
                    text=f'点击打开网站', url=f"{Config.v2_url}/#/invite")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                callback = reply(Message.Error_MyInviteNotFound,
                                 reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def buyplan(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type == 'private' or gid == Config.tg_group:
        text, reply_markup = Command.onBuyPlan()
        callback = reply(text, reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


def website(update: Update, context: CallbackContext) -> None:
    reply = update.message.reply_markdown
    uid = update.message.from_user.id
    gid = update.message.chat.id
    chat_type = update.message.chat.type

    if chat_type == 'private' or gid == Config.tg_group:
        text, reply_markup = Command.onWebsite()
        callback = reply(text, reply_markup=reply_markup)
        if chat_type != 'private':
            Module.autoDelete(update, callback.chat.id, callback.message_id)


class Module:
    def autoDelete(update, chatid, messageid):
        time.sleep(30)
        bot.deleteMessage(chat_id=chatid, message_id=messageid)
        update.message.delete()

    def autoSend():
        # 待优化
        global current_list
        ticket = Module.getNewTicket()
        order = Module.getNewOrder()
        print(current_list)
        if current_list['ticket'] != 0 and len(ticket) > current_list['ticket']:
            for i in range(current_list['ticket'], len(ticket)):
                # id,user_id,subject,level,status,reply_status
                Result, User = Module.getUser('id', ticket[i][1])
                Email = User['email']
                Subject = ticket[i][2]
                Code = {
                    'Level': ['低', '中', '高'],
                    'Status': ['开放', '关闭'],
                    'Reply': ['已回复', '待回复'],
                }
                Level, Status, Reply = ticket[i][3], ticket[i][4], ticket[i][5]
                Level = Code['Level'][Level]
                Status = Code['Status'][Status]
                Reply = Code['Reply'][Reply]
                text = '📠*新的工单*\n\n'
                text = f'{text}👤*用户*：`{Email}`\n'
                text = f'{text}📩*主题*：{Subject}\n'
                text = f'{text}🔔*工单级别*：{Level}\n'
                text = f'{text}🔰*工单状态*：{Status}\n'
                text = f'{text}📝*答复状态*：{Reply}\n'

                keyboard = [[InlineKeyboardButton(
                    text='回复工单', url=f"{Config.v2_url}/admin#/ticket/{i+1}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(
                    chat_id=Config.tg_admin,
                    text=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        if current_list['order'] != 0 and len(order) > current_list['order']:
            for i in range(current_list['order'], len(order)):
                Result, User = Module.getUser('id', order[i][2])
                Email = User['email']
                Plan = Module.getPlanName(order[i][3])
                Payment = Module.getPaymentName(order[i][5])
                Code = {
                    'Type': ['无', '新购', '续费', '升级'],
                    'Period': {
                        'month_price': '月付',
                        'quarter_price': '季付',
                        'half_year_price': '半年付',
                        'year_price': '年付',
                        'two_year_price': '两年付',
                        'three_year_price': '三年付',
                        'onetime_price': '一次性',
                        'reset_price': '重置包',
                    }
                }
                Type = Code['Type'][order[i][6]]
                Period = Code['Period'][order[i][7]]
                Amount = round(order[i][10] / 100, 2)
                Paid_Time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(order[i][21]))

                text = '📠*新的订单*\n\n'
                text = f'{text}👤*用户*：`{Email}`\n'
                text = f'{text}🛍*套餐*：{Plan}\n'
                text = f'{text}💵*支付*：{Payment}\n'
                text = f'{text}📥*类型*：{Type}\n'
                text = f'{text}📅*时长*：{Period}\n'
                text = f'{text}🏷*价格*：{Amount}\n'
                text = f'{text}🕰*支付时间*：{Paid_Time}\n'

                bot.send_message(
                    chat_id=Config.tg_admin,
                    text=text,
                    parse_mode='Markdown'
                )
        current_list = {
            'ticket': len(ticket),
            'order': len(order)
        }
        timer = threading.Timer(60, Module.autoSend)
        timer.start()

    def getNewTicket():
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM v2_ticket")
            result = cursor.fetchall()
            return result

    def getNewOrder():
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM v2_order WHERE `total_amount` > '0' AND `status` = '3'")
            result = cursor.fetchall()
            return result

    def onLogin(email, password):
        login = {
            "email": email,
            "password": password
        }
        x = requests.post(
            f'{Config.v2_url}/api/v1/passport/auth/login', login)
        if x.status_code == 200:
            return True
        else:
            return False

    def getUser(t, id):
        # args t = id or telegram_id
        # return boolean, userdata as dict
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(f"SELECT * FROM v2_user WHERE `{t}` = {id}")
            result = cursor.fetchone()
            if result is None:
                user = {}
                return False, user
            else:
                user = {
                    'uid': result[0],
                    'tg': result[2],
                    'email': result[3],
                    'money': result[7],
                    'time': result[12],
                    'upload': result[13],
                    'download': result[14],
                    'total': result[15],
                    'plan': result[23],
                    'token': result[26],
                    'expire': result[28],
                    'register': result[29]}
                return True, user

    def getUserStat(uid):
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM v2_stat_user WHERE `user_id` = {uid}")
            result = cursor.fetchall()
            print(result)
            if len(result) < 1:
                return False, result
            else:
                return True, result

    def getTGbyMail(email):
        # args email
        # return boolean, TelegramID
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT telegram_id FROM v2_user WHERE email = %s", (email))
            result = cursor.fetchone()
            if result[0] is None:
                return False, 0
            else:
                return True, result[0]

    def getPlanName(planid):
        # args planid
        # return planname
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM v2_plan WHERE id = %s", (planid))
            result = cursor.fetchone()
            return result[0]

    def getInviteCode(uid):
        # args user id
        # return code,status,pv
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT code,status,pv FROM v2_invite_code WHERE user_id = %s", (uid))
            result = cursor.fetchone()
            return result

    def getPlanAll():
        # return planID & Name (Only enable plan)
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id,name FROM v2_plan WHERE `show` = 1")
            result = cursor.fetchall()
            return result

    def getInviteTimes(uid):
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM v2_user WHERE invite_user_id =  %s", (uid))
            result = cursor.fetchall()
            return len(result)

    def getPaymentName(id):
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM v2_payment WHERE id =  %s", (id))
            result = cursor.fetchone()
            return result[0]


def main() -> None:
    updater = Updater(Config.bot_token)

    dispatcher = updater.dispatcher

    bot.deleteMyCommands()
    dispatcher.add_handler(CommandHandler("s", s, run_async=True))
    dispatcher.add_handler(CommandHandler("ping", ping, run_async=True))
    dispatcher.add_handler(CommandHandler("bind", bind, run_async=True))
    dispatcher.add_handler(CommandHandler("unbind", unbind, run_async=True))
    dispatcher.add_handler(CommandHandler("mysub", mysub, run_async=True))
    dispatcher.add_handler(CommandHandler("myinfo", myinfo, run_async=True))
    dispatcher.add_handler(CommandHandler("myusage", myusage, run_async=True))
    dispatcher.add_handler(CommandHandler("myinvite", myinvite, run_async=True))
    dispatcher.add_handler(CommandHandler("buyplan", buyplan, run_async=True))
    dispatcher.add_handler(CommandHandler("website", website, run_async=True))
    commands = [BotCommand('ping', '获取当前聊天信息'),
                BotCommand('bind', '绑定账号信息到该TG'),
                BotCommand('unbind', '解绑该账号的TG信息'),
                BotCommand('mysub', '获取我的订阅链接'),
                BotCommand('myinfo', '获取我的订阅信息'),
                BotCommand('myusage', '获取我的使用信息'),
                BotCommand('myinvite', '获取我的邀请链接'),
                BotCommand('buyplan', '打开购买商店'),
                BotCommand('website', '打开网站链接'),
                ]
    bot.setMyCommands(commands)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    timer = threading.Timer(1, Module.autoSend)
    timer.start()
    main()
