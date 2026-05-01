
from datetime import datetime
import logging
from logging import Logger
from random import random
from pathlib import Path
from webdav3.client import Client
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from library.config import quit_on_fatal, read_config


IMAGE_TMP_DIR = Path('./images')
PRIVILEGE_ISSUE_MSG = 'You do NOT have privilege to access this feature.'
TOO_STUPID_MSG = '''
很抱歉，我不懂您的意思 \U0001F62D 。
看來我們的工程師還不夠努力！！
'''

TELE_CONFIG: dict = {}
CLOUD_CONFIG: dict = {}


def init_logger() -> Logger:
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    # Set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


LOGGER: Logger = init_logger()


def init_tele_config() -> None:
    global TELE_CONFIG

    config_template = {
        'bot_name': None,
        'author': None,
        'website': None,
        'contact': None,
        'token': None,
        'allowed_sender': None,
    }

    config = read_config(
        'telebot.yml',
        config_template,
    )

    if config is None:
        return

    TELE_CONFIG = config


def init_cloud_config() -> None:
    global CLOUD_CONFIG

    config_template = {
        'username': None,
        'password': None,
        'file_ap': None,
    }

    config = read_config(
        'webdav.yml',
        config_template,
    )

    if config is None:
        return

    CLOUD_CONFIG = config


async def block_unauthorized(update: Update) -> bool:
    if not update.message:
        return False

    if (
        not update.message.from_user or
        update.message.from_user.id != TELE_CONFIG.get('allowed_sender')
    ):
        await update.message.reply_text(PRIVILEGE_ISSUE_MSG)
        return False

    return True


async def save_to_cloud(
    context: ContextTypes.DEFAULT_TYPE,
    file_id: str,
    file_ext: str = ''
) -> str | None:
    filename = Path(str(int(random() * 1e10)) + file_ext)
    fullpath = IMAGE_TMP_DIR / filename
    has_failure = False

    try:
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(fullpath)

        dav_options = {
            'webdav_hostname': CLOUD_CONFIG.get('file_ap'),
            'webdav_login': CLOUD_CONFIG.get('username'),
            'webdav_password': CLOUD_CONFIG.get('password')
        }

        client = Client(dav_options)
        client.upload_sync(
            remote_path=f'Cloud/line/{str(filename)}',
            local_path=str(fullpath)
        )

    except Exception as e:
        LOGGER.error(e)
        has_failure = True

    finally:
        fullpath.unlink(missing_ok=True)

    if has_failure:
        return None

    return str(filename)


async def save_image(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await block_unauthorized(update):
        return

    if update.message is None:
        return

    photo_id = update.message.photo[-1].file_id
    filename = await save_to_cloud(context, photo_id, '.jpg')

    await update.message.reply_text(
        'Image failed to save'
        if filename is None
        else
        f'Image saved to cloud as "{filename}"'
    )


async def save_file(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await block_unauthorized(update):
        return

    if update.message is None:
        return

    # Only handle documents not others like stickers.
    if not update.message.document:
        await update.message.reply_text(TOO_STUPID_MSG)
        return

    file_id = update.message.document.file_id
    file_ext = (
        Path(update.message.document.file_name).suffix
        if update.message.document.file_name
        else
        ''
    )

    filename = await save_to_cloud(context, file_id, file_ext)

    await update.message.reply_text(
        'File failed to save'
        if filename is None
        else
        f'File saved to cloud as "{filename}"'
    )


async def save_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await block_unauthorized(update):
        return

    if update.message is None or update.message.text is None:
        return

    message = update.message.text.replace('/save', '').strip()

    # TODO
    with open('Cloud/line/note.txt', 'a', encoding='utf-8') as fout:
        fout.write(
            '\n' +
            datetime.now().strftime('%Y.%m.%d %H:%M:%S') +
            '\n' + message + '\n'
        )

    await update.message.reply_text('Text saved to cloud.')


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None or update.effective_user is None:
        return

    await update.message.reply_html(rf'''
哈囉，{update.effective_user.mention_html()}
試著輸入 /help 來取得使用說明
    ''')


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message:
        await update.message.reply_text(f'''
您好，我是 {TELE_CONFIG.get("bot_name")}！很高興為您服務～
我是 {TELE_CONFIG.get("author")} 製作的智慧型聊天機器人
輸入關鍵字，讓我為您服務吧！

使用時遇到問題了嗎？
趕緊聯繫系統管理員吧： {TELE_CONFIG.get("contact")}
或從網站尋找詳細資訊： {TELE_CONFIG.get("website")}
        ''')


async def cant_understand(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await block_unauthorized(update):
        return

    if update.message is None:
        return

    await update.message.reply_text(TOO_STUPID_MSG)


def bot_server() -> None:
    token = TELE_CONFIG.get('token')

    if not (isinstance(token, str) and len(token) > 0):
        quit_on_fatal()
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # On image
    application.add_handler(MessageHandler(filters.PHOTO, save_image))

    # On file
    application.add_handler(MessageHandler(filters.ATTACHMENT, save_file))

    # On defined commands
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('save', save_command))

    # On other cases
    application.add_handler(MessageHandler(filters.COMMAND, cant_understand))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cant_understand))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    init_tele_config()
    init_cloud_config()

    if not CLOUD_CONFIG or not TELE_CONFIG:
        quit_on_fatal()

    bot_server()
