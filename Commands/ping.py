from telegram import Update
from telegram.ext import ContextTypes

desc = '获取当前聊天信息'


async def autoDelete(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.delete_message(job.chat_id, job.data)


async def exec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    user_id = msg.from_user.id
    chat_id = msg.chat_id
    chat_type = msg.chat.type

    text = '💥*嘭*\n'
    utid = f'{text}\n你的ID为：`{user_id}`'

    if chat_type == 'private':
        await msg.reply_markdown(utid)
    else:
        group = f'\n群组ID为：`{chat_id}`'
        callback = await msg.reply_markdown(f'{utid}{group}')
        context.job_queue.run_once(
                autoDelete, 15, data=msg.id, chat_id=chat_id, name=str(msg.id))
        context.job_queue.run_once(
            autoDelete, 15, data=callback.message_id, chat_id=chat_id, name=str(callback.message_id))
