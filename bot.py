#!/usr/bin/env python

import logging
from unittest import result
import pymysql
import time
import threading
import pytz
import datetime
from sshtunnel import SSHTunnelForwarder

from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import Updater, CommandHandler, CallbackContext

import Message
import Config
import Command
import Schedule
import Handler

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
tz = pytz.timezone('Asia/Shanghai')
sysday = datetime.datetime.now(tz).strftime("%Y-%m-%d")
task_autoSend = False


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

    result, user = Handler.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Handler.onLogin(email, password) is True:
                    result, tig = Handler.getTGbyMail(email)
                    if result is False:
                        reply(Message.Success_Bind)
                        Handler.onBind(tid, email)
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

    result, user = Handler.getUser('telegram_id', tid)

    if chat_type == 'private':
        if result is False:
            reply(Message.Error_NotBind)
        else:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if Handler.onLogin(email, password) is True:
                    result, id = Handler.getTGbyMail(email)
                    if id == tid:
                        reply(Message.Success_UnBind)
                        Handler.onUnBind(email)
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

    result, user = Handler.getUser('telegram_id', tid)

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

    result, user = Handler.getUser('telegram_id', tid)

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

    result, user = Handler.getUser('telegram_id', tid)
    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            result, statlist = Handler.getUserStat(user['uid'])
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

    result, user = Handler.getUser('telegram_id', tid)

    if chat_type == 'private' or gid == Config.tg_group:
        if result is False:
            callback = reply(Message.Error_NotBind)
        else:
            invite_code = Handler.getInviteCode(user['uid'])
            if invite_code is not None:
                invite_times = Handler.getInviteTimes(user['uid'])
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
        global task_autoSend
        global sysday
        ticket = Handler.getNewTicket()
        order = Handler.getNewOrder()
        if current_list['ticket'] != 0 and len(ticket) > current_list['ticket']:
            for i in range(current_list['ticket'], len(ticket)):
                # id,user_id,subject,level,status,reply_status
                Result, User = Handler.getUser('id', ticket[i][1])
                text, reply_markup = Schedule.onTicket(
                    User['email'], ticket, i)

                bot.send_message(
                    chat_id=Config.tg_admin,
                    text=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        current_list['ticket'] = len(ticket)
        if current_list['order'] != 0 and len(order) > current_list['order']:
            for i in range(current_list['order'], len(order)):
                Total_amount = order[i][10]
                Status = order[i][17]
                if Total_amount > 0 and Status == 3 and order[i][5] is not None:
                    Result, User = Handler.getUser('id', order[i][2])
                    text = Schedule.onOrder(User['email'], order, i)

                    bot.send_message(
                        chat_id=Config.tg_admin,
                        text=text,
                        parse_mode='Markdown'
                    )
                    current_list['order'] = i+1
        else:
            current_list['order'] = len(order)
        # 待优化
        if Schedule.Settings.send_serverdata is True:
            if task_autoSend is False:
                result,text = Schedule.onTodayData()
                if result is True:
                    bot.send_message(
                        chat_id=Config.tg_group,
                        text=text,
                        parse_mode='Markdown'
                    )
                task_autoSend = True
            else:
                curday = datetime.datetime.now(tz).strftime("%Y-%m-%d")
                if curday > sysday:
                    task_autoSend = False
                    sysday = curday
        timer = threading.Timer(60, Module.autoSend)
        timer.start()


def main() -> None:
    updater = Updater(Config.bot_token)

    dispatcher = updater.dispatcher

    bot.deleteMyCommands()

    commands = {
        'ping': [ping, '获取当前聊天信息'],
        'bind': [bind, '绑定账号信息到该TG'],
        'unbind': [unbind, '解绑该账号的TG信息'],
        'mysub': [mysub, '获取我的订阅链接'],
        'myinfo': [myinfo, '获取我的订阅信息'],
        'myusage': [myusage, '获取我的使用信息'],
        'myinvite': [myinvite, '获取我的邀请链接'],
        'buyplan': [buyplan, '打开购买商店'],
        'website': [website, '打开网站链接'],
    }
    commands_list = []
    for i in commands:
        dispatcher.add_handler(CommandHandler(
            i, commands[i][0], run_async=True))
        commands_list.append(BotCommand(i, commands[i][1]))

    bot.setMyCommands(commands_list)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    timer = threading.Timer(1, Module.autoSend)
    timer.start()
    main()
