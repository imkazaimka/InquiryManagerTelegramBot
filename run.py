"""
Programmer : Shoniyozov Imronbek 

Filename : run.py

Description : Entry point for running the bot
"""

import logging
import threading
import bot.user as user
import bot.admin as admin

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_user_bot(bot):
    bot.infinity_polling()

def run_admin_bot(bot):
    bot.infinity_polling()

if __name__ == "__main__":
    logger.info("Starting both user and admin bots...")

    # Create the user bot instance
    user_bot_instance = user.create_user_bot()

    # Create the admin bot instance, passing user_bot_instance as user_bot_ref
    admin_bot_instance = admin.create_admin_bot(user_bot_ref=user_bot_instance)

    # Create threads for each bot
    user_thread = threading.Thread(target=run_user_bot, args=(user_bot_instance,), name="UserBotThread")
    admin_thread = threading.Thread(target=run_admin_bot, args=(admin_bot_instance,), name="AdminBotThread")

    # Start both threads
    user_thread.start()
    admin_thread.start()

    # Wait for both threads (infinity_polling never ends normally)
    user_thread.join()
    admin_thread.join()
