import bot
import requests
from handler import MysqlUtils
from telegram import Update
from telegram.ext import ContextTypes

desc = '绑定账号信息到该 Telegram 账号'
config = bot.config['bot']


def onLogin(email, password):
    login = {
        "email": email,
        "password": password
    }
    url = '%s/api/v1/passport/auth/login' % config['website']
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    x = requests.post(url, login, headers=headers, timeout=5)
    if x.status_code == 200:
        return True
    else:
        return False


def onQuery(sql):
    try:
        db = MysqlUtils()
        result = db.sql_query(sql)
    finally:
        db.close()
        return result


async def autoDelete(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.delete_message(job.chat_id, job.data)


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user_id = msg.from_user.id
    chat_id = msg.chat_id
    chat_type = msg.chat.type
    if chat_type == 'private':
        user = onQuery(
            'SELECT * FROM v2_user WHERE `telegram_id` = %s' % user_id)
        if len(user) == 0:
            if len(context.args) == 2:
                email = context.args[0]
                password = context.args[1]
                if onLogin(email, password) is True:
                    check = onQuery(
                        'SELECT telegram_id FROM v2_user WHERE `email` = "%s"' % email)[0]
                    if check[0] is None:
                        db = MysqlUtils()
                        db.update_one('v2_user', params={
                            'telegram_id': user_id}, conditions={'email': email})
                        db.conn.commit()
                        db.close()
                        await msg.reply_markdown('✔️*成功*\n你已成功绑定 Telegram 了！')
                    else:
                        await msg.reply_markdown('❌*错误*\n这个账号已绑定到别的 Telegram 了！')
                else:
                    await msg.reply_markdown('❌*错误*\n邮箱或密码错误了！')
            else:
                await msg.reply_markdown('❌*错误*\n正确的格式为：/bind 邮箱 密码')
        else:
            await msg.reply_markdown('❌*错误*\n你已经绑定过账号了！')
    else:
        if chat_id == config['group_id']:
            callback = await msg.reply_markdown('❌*错误*\n为了你的账号安全，请私聊我！')
            context.job_queue.run_once(
                autoDelete, 15, data=msg.id, chat_id=chat_id, name=str(msg.id))
            context.job_queue.run_once(
                autoDelete, 15, data=callback.message_id, chat_id=chat_id, name=str(callback.message_id))
