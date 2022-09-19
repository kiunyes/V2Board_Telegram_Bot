import asyncio
import bot
import requests
from handler import MysqlUtils

desc = '解绑该账号的 Telegram 账号'
config = bot.config['bot']


def onLogin(email, password):
    login = {
        "email": email,
        "password": password
    }
    x = requests.post(
        '%s/api/v1/passport/auth/login' % config['website'], login)
    print(x)
    if x.status_code == 200:
        return True
    else:
        return False


async def exec(update, context) -> None:
    msg = update.message
    tid = msg.from_user.id
    gid = msg.chat.id
    chat_type = msg.chat.type

    try:
        db = MysqlUtils()
        if chat_type == 'private':
            user = db.sql_query(
                'SELECT * FROM v2_user WHERE `telegram_id` = %s' % tid)
            if len(user) == 0:
                await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
            else:
                if len(context.args) == 2:
                    email = context.args[0]
                    password = context.args[1]
                    if onLogin(email, password) is True:
                        check = db.sql_query(
                            'SELECT * FROM v2_user WHERE `email` = "%s"' % email)
                        if tid == check[0][2]:
                            await msg.reply_markdown('✔️*成功*\n你已成功解绑 Telegram 了！')
                            db.execute_sql(
                                sql='UPDATE v2_user SET telegram_id = NULL WHERE email = "%s"' % email)
                        else:
                            await msg.reply_markdown('❌*错误*\n这个账号与绑定的 Telegram 不匹配！')
                    else:
                        await msg.reply_markdown('❌*错误*\n邮箱或密码错误了！')
                else:
                    await msg.reply_markdown('❌*错误*\n正确的格式为：/unbind 邮箱 密码')
        else:
            if gid == config['tg_group']:
                user=db.sql_query(
                    'SELECT * FROM v2_user WHERE `telegram_id` = %s' % tid)
                if len(user) > 0:
                    callback=await msg.reply_markdown('❌*错误*\n为了你的账号安全，请私聊我！')
                else:
                    callback=await msg.reply_markdown('❌*错误*\n你还没有绑定过账号！')
                await asyncio.sleep(15)
                await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
    finally:
        db.close()
