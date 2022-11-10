import bot
import pytz
import os
import datetime
import time
import yaml
from handler import MysqlUtils
from telegram.ext import ContextTypes

desc = '定时推送用量'


class Settings:
    # 服务器统计
    send_server = True
    # 用户统计
    send_user = True
    # 统计多少个
    index = 5


cfg = bot.config['bot']

timezone = pytz.timezone('Asia/Shanghai')
sysday = datetime.datetime.now(timezone).strftime("%Y-%m-%d")
already_sent = True


def onQuery(sql):
    try:
        db = MysqlUtils()
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


def getTimestemp():
    yesterday = (datetime.datetime.now(timezone) -
                 datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    timestemp = int(time.mktime(
        time.strptime(str(yesterday), '%Y-%m-%d')))
    return timestemp


def onSendServer():
    result = onQuery(
        "SELECT * FROM v2_stat_server WHERE record_at = %s" % getTimestemp())
    result_list = []
    if result is not None:
        for i in result:
            result_list.append(i)
        result_list.sort(key=lambda x: x[4], reverse=True)
        index = Settings.index
        if len(result_list) < index:
            index = len(result_list)
        text = f'使用的前 {index} 的节点：\n\n'
        for i in range(index):
            tbl_name = f'v2_server_{result_list[i][2]}'
            if result_list[i][2] == 'vmess':
                tbl_name = 'v2_server_v2ray'
            node_stat = onQuery(
                f"SELECT * FROM {tbl_name} WHERE id = {result_list[i][1]}")
            node_name = node_stat[0][4]
            if result_list[i][2] == 'vmess':
                node_name = node_stat[0][2]
            download = round(result_list[i][4] / 1024 / 1024 / 1024, 2)
            text = f'{text}{node_name} - `{download}` GB\n'
        return text
    else:
        return ''


def onSendUser():
    result = onQuery(
        "SELECT * FROM v2_stat_user WHERE record_at = %s" % getTimestemp())
    result_dict = {}
    if result is not None:
        for i in result:
            if str(i[1]) not in result_dict:
                result_dict[str(i[1])] = i[4]
            else:
                result_dict[str(i[1])] += i[4]
        result_list = sorted(result_dict.items(),
                             key=lambda x: x[1], reverse=True)
        index = Settings.index
        if len(result_list) < index:
            index = len(result_list)
        text = f'流量使用前 {index} 名用户：\n\n'
        for i in range(index):
            user = onQuery("SELECT * FROM v2_user WHERE id = %s" %
                           result_list[i][0])
            download = round(result_list[i][1] / 1024 / 1024 / 1024, 2)
            text = f'{text}`***@***.com` - #`{user[0][0]}` - `{download}` GB\n'
        return text
    else:
        return ''


def onTodayData():
    text = '📊*昨日统计：*\n\n'
    if Settings.send_server is True:
        text = f'{text}{onSendServer()}\n'
    if Settings.send_user is True:
        text = f'{text}{onSendUser()}\n'
    if Settings.send_server is False and Settings.send_user is False:
        return False, ''
    else:
        return True, text


async def exec(context: ContextTypes.DEFAULT_TYPE):
    curpath = os.path.dirname(os.path.realpath(__file__))
    yamlpath = os.path.join(curpath, "../Temp/%s.yaml" % __name__)
    origin = {
        'sysday': datetime.datetime.now(timezone).strftime("%Y-%m-%d"),
        'already_sent': True
    }
    try:
        with open(yamlpath) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as error:
        with open(yamlpath, "w", encoding="utf-8") as f:
            yaml.dump(origin,f)
            config = origin

    if config['already_sent'] is False:
        result, text = onTodayData()
        if result is True:
            await context.bot.send_message(
                chat_id=cfg['group_id'],
                text=text,
                parse_mode='Markdown'
            )
        config['already_sent'] = True
        with open(yamlpath, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
    else:
        curday = datetime.datetime.now(timezone).strftime("%Y-%m-%d")
        if curday > config['sysday']:
            config['already_sent'] = False
            config['sysday'] = curday
            with open(yamlpath, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False)
