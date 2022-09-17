import asyncio

desc = '获取当前聊天信息'


async def exec(update, context) -> None:
    msg = update.message
    tid = msg.from_user.id
    gid = msg.chat.id
    chat_type = msg.chat.type

    text = '💥*嘭*\n'
    utid = f'{text}\n你的ID为：`{tid}`'

    if chat_type == 'private':
        await msg.reply_markdown(utid)
    else:
        group = f'\n群组ID为：`{gid}`'
        if update.message.from_user.is_bot is False:
            callback = await msg.reply_markdown(f'{utid}{group}')
        else:
            callback = await msg.reply_markdown(f'{text}{group}')
        await asyncio.sleep(15)
        await context.bot.deleteMessage(message_id=callback.message_id, chat_id=msg.chat_id)
