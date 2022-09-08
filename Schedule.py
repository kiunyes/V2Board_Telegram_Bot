import Handler
import Config
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import time
import datetime
import pytz
tz = pytz.timezone('Asia/Shanghai')


class Settings:
    send_serverdata = True


class Mapping:
    ticket = {
        'Level': ['低', '中', '高'],
        'Status': ['开放', '关闭'],
        'Reply': ['已回复', '待回复'],
    }
    order = {
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


def onTicket(email, ticket, i):
    Subject = ticket[i][2]
    Level, Status, Reply = ticket[i][3], ticket[i][4], ticket[i][5]
    Level = Mapping.ticket['Level'][Level]
    Status = Mapping.ticket['Status'][Status]
    Reply = Mapping.ticket['Reply'][Reply]

    text = '📠*新的工单*\n\n'
    text = f'{text}👤*用户*：`{email}`\n'
    text = f'{text}📩*主题*：{Subject}\n'
    text = f'{text}🔔*工单级别*：{Level}\n'
    text = f'{text}🔰*工单状态*：{Status}\n'
    text = f'{text}📝*答复状态*：{Reply}\n'
    keyboard = [[InlineKeyboardButton(
        text='回复工单', url=f"{Config.v2_url}/admin#/ticket/{i+1}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup


def onOrder(email, order, i):
    Plan = Handler.getPlanName(order[i][3])
    Payment = Handler.getPaymentName(order[i][5])
    Type = Mapping.order['Type'][order[i][6]]
    Period = Mapping.order['Period'][order[i][7]]
    Amount = round(order[i][10] / 100, 2)
    Paid_Time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(order[i][21]))

    text = '📠*新的订单*\n\n'
    text = f'{text}👤*用户*：`{email}`\n'
    text = f'{text}🛍*套餐*：{Plan}\n'
    text = f'{text}💵*支付*：{Payment}\n'
    text = f'{text}📥*类型*：{Type}\n'
    text = f'{text}📅*时长*：{Period}\n'
    text = f'{text}🏷*价格*：{Amount}\n'
    text = f'{text}🕰*支付时间*：{Paid_Time}\n'


def getTodayTimestemp():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    timestemp = int(time.mktime(
        time.strptime(str(yesterday), '%Y-%m-%d')))
    return timestemp


def onTodayData():
    result = Handler.getServerStat(getTodayTimestemp())
    result_list = []
    if result is None:
        return False, ''
    else:
        for i in result:
            result_list.append(i)
        result_list.sort(key=lambda x: x[4], reverse=True)
        index = 5 
        text = '📊*昨日统计：*\n\n'
        text = f'{text}使用的前 {index} 个节点（不算倍率）：\n\n'
        for i in range(index):
            server = Handler.getServerName(
                result_list[i][2], result_list[i][1])
            servername = server[4]
            download = round(result_list[i][4] / 1024 / 1024 / 1024, 2)
            text = f'{text}{servername} - `{download}` GB\n'
        return True, text
