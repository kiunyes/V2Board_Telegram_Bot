import logging
import yaml

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]
if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram.ext import Application, CommandHandler

import commands


def onLog():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.getLogger(__name__)


def onRunning():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    #proxy = 'http://127.0.0.1:7890'
    token = config['bot']['token']
    app = Application.builder().token(token).build()
    #app = Application.builder().token(token).proxy_url(proxy).get_updates_proxy_url(proxy).build()
    for i in commands.cmd:
        model = getattr(commands, i)
        app.add_handler(CommandHandler(i, model.exec))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    onLog()
    onRunning()
