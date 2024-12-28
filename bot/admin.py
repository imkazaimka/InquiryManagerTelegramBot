import logging
from telebot import TeleBot
import config
import database.models as models
import handlers.admin as admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_bot(user_bot_ref):
    models.init_db()
    logger.info("Admin database initialized.")

    bot = TeleBot(config.ADMIN_BOT_TOKEN)
    logger.info("Admin bot instance created.")

    admin.register_handlers(bot, user_bot_ref=user_bot_ref)
    logger.info("Admin handlers registered.")

    return bot
