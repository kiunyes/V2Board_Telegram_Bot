import requests

import bot
import Config

db = bot.db


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


def onBind(tid, email):
    # args tid,email
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE v2_user SET telegram_id = %s WHERE email = %s", (int(tid), email))


def onUnBind(tid, email):
    # args tid,email
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE v2_user SET telegram_id = NULL WHERE email = %s", (email))


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
            "SELECT * FROM v2_order")
        result = cursor.fetchall()
        return result


def getServerStat(timestemp):
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM v2_stat_server WHERE record_at = %s", (timestemp))
        result = cursor.fetchall()
        return result


def getServerName(server_type, server_id):
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        server = f'v2_server_{server_type}'
        cursor.execute(
            f"SELECT * FROM {server} WHERE id = {server_id}")
        result = cursor.fetchone()
        return result


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
            "SELECT * FROM v2_stat_user WHERE `user_id` = %s", (uid))
        result = cursor.fetchall()
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
