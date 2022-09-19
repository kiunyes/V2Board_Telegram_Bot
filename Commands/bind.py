import asyncio
import bot
import requests
from handler import MysqlUtils

desc = '绑定账号信息到该 Telegram 账号'
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
    db = MysqlUtils()
    try:
        if chat_type == 'private':
            user = db.sql_query(
                'SELECT * FROM v2_user WHERE `telegram_id` = %s' % tid)
            if len(user) == 0:
                if len(context.args) == 2:
                    email = context.args[0]
                    password = context.args[1]
                    if onLogin(email, password) is True:
                        check = db.sql_query(
                            'SELECT * FROM v2_user WHERE `email` = "%s"' % email)
                        if check[0][2] is None:
                            await msg.reply_markdown('✔️*成功*\n你已成功绑定 Telegram 了！')
                            db.update_one('v2_user', params={
                                'telegram_id': tid}, conditions={'email': email})
                        else:
                            await msg.reply_markdown('❌*错误*\n这个账号已绑定到别的 Telegram 了！')
                    else:
                        await msg.reply_markdown('❌*错误*\n邮箱或密码错误了！')
                else:
                    await msg.reply_markdown('❌*错误*\n正确的格式为：/bind 邮箱 密码')
            else:
                await msg.reply_markdown('❌*错误*\n你已经绑定过账号了！')
        else:
            if gid == config['tg_group']:
                user = db.sql_query(
                    'SELECT * FROM v2_user WHERE `telegram_id` = %s' % tid)
                if len(user) > 0:
                    callback = await msg.reply_markdown('❌*错误*\n你已经绑定过账号了！')
                else:
                    callback = await msg.reply_markdown('❌*错误*\n为了你的账号安全，请私聊我！')
                await asyncio.sleep(15)
                await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
    finally:
        db.conn.commit()
        db.close()
