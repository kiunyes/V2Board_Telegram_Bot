import logging
import yaml
import sys
from sshtunnel import SSHTunnelForwarder
from datetime import time

from telegram import __version__ as TG_VER
from telegram import BotCommand

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]
if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This bot is not compatible with your current PTB version {TG_VER}. To upgrade use this command:"
        f"pip3 install python-telegram-bot --upgrade --pre"
    )
from telegram.ext import Application, CommandHandler, ContextTypes

token='********************************'

class SensitiveFormatter(logging.Formatter):
    def format(self, record):
        recordText = logging.Formatter.format(self, record)
        return recordText.replace(token,"***bot_token***")

LOG_FORMAT ='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)
for handler in logging.root.handlers:
   handler.setFormatter(SensitiveFormatter(LOG_FORMAT))

VERSION = "2.0"

try:
    f = open('config.yaml', 'r')
    config = yaml.safe_load(f)
    # 兼容老config
    if isinstance(config['bot']['admin_id'], int) is True:
        with open("config.yaml", "w", encoding="utf-8") as f:
            admin_id = [config['bot']['admin_id']]
            config['bot']['admin_id'] = admin_id
            yaml.dump(config, f)
except FileNotFoundError as error:
    print('没有找到 config.yaml，请复制 config.yaml.example 并重命名为 config.yaml')
    sys.exit(0)

try:
    ssh_cfg = config['v2board']['ssh']
    db_cfg = config['v2board']['database']
    port = db_cfg['port']
    if ssh_cfg['enable'] is True:
        if ssh_cfg['type'] == "passwd":
            ssh = SSHTunnelForwarder(
                ssh_address_or_host=(ssh_cfg['ip'], ssh_cfg['port']),
                ssh_username=ssh_cfg['user'],
                ssh_password=ssh_cfg['pass'],
                remote_bind_address=(db_cfg['ip'], db_cfg['port']))

        if ssh_cfg['type'] == "pkey":
            ssh = SSHTunnelForwarder(
                ssh_address_or_host=(ssh_cfg['ip'], ssh_cfg['port']),
                ssh_username=ssh_cfg['user'],
                ssh_pkey=ssh_cfg['keyfile'],
                ssh_private_key_password=ssh_cfg['keypass'],
                remote_bind_address=(db_cfg['ip'], db_cfg['port']))
        ssh.start()
        port = ssh.local_bind_port
except Exception as error:
    print('你已启用 SSH，但是 SSH 的相关配置不正确')
    sys.exit(0)

try:
    token = config['bot']['token']
    app = Application.builder().token(token).build()
except Exception as error:
    print('无法启动 Telegram Bot，请确认 Bot Token 是否正确，或者是否能连接 Telegram 服务器')
    sys.exit(0)

try:
    if config['enhanced']['enable']:
        isEnhanced = True
        enhancedModules=list(config['enhanced']['module'])
    else:
        isEnhanced = False
except Exception as err:
    print('增强模组未启动成功', err)
    isEnhanced = False


async def onCommandSet(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands()
    await context.bot.set_my_commands(context.job.data)


def main():
    try:
        # 导入命令文件夹
        import Commands
        command_list = []
        for i in Commands.content:
            cmds = getattr(Commands, i)
            app.add_handler(CommandHandler(i, cmds.exec))
            command_list.append(BotCommand(i, cmds.desc))
        app.job_queue.run_once(onCommandSet, 1, command_list, 'onCommandSet')
        # 导入任务文件夹
        import Modules
        for i in Modules.content:
            mods = getattr(Modules, i)
            Conf = mods.Conf
            if Conf.method == 'daily':
                app.job_queue.run_daily(
                    mods.exec, time.fromisoformat(Conf.runtime), name=i)
            elif Conf.method == 'repeating':
                app.job_queue.run_repeating(
                    mods.exec, interval=Conf.interval, name=i)
        # 启动 Bot
        app.run_polling(drop_pending_updates=True)
    except Exception as error:
        print(error)
        sys.exit(0)


if __name__ == "__main__":
    main()
