import logging
from telebot import TeleBot
import config
import database.models as models
import handlers.user as user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user_bot():
    models.init_db()
    logger.info("User database initialized.")

    bot = TeleBot(config.BHR_BOT_TOKEN)
    logger.info("User bot instance created.")

    user.register_handlers(bot)
    logger.info("User handlers registered.")

    return bot
