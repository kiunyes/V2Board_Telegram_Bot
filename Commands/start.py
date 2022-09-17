desc = '开始使用 Bot'


async def exec(update, context) -> None:
    msg = update.message
    chat_type = msg.chat.type

    if chat_type == 'private':
        await msg.reply_markdown('欢迎使用这个Bot，绑定请输入 /bind 账号 密码')
