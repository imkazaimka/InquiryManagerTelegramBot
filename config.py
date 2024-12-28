"""
Programmer : Shoniyozov Imronbek 

Filename : config.py

Description : Configuration loader for bot settings and environment variables
"""


from dotenv import load_dotenv
import os

load_dotenv()

BHR_BOT_TOKEN = os.getenv("BHR_BOT_TOKEN")
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID"))
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))