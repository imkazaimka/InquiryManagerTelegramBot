"""
Programmer : Shoniyozov Imronbek 

Filename : handlers/admin.py

Description : Handlers for the admin part of the bot
"""

import logging

from telebot import TeleBot, types

from config import ADMIN_GROUP_ID

from handlers.logic import (
    answer_inquiry, get_inquiry_details, get_inquiries_by_status,
    get_inquiries_by_workplace
)


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


ADMIN_STATE = {}


WORKPLACE_OPTIONS = [
    "NAVBAHOR TEKSTIL MCHJ ",
    "PTK (PAXTA TOZALASH KORXONASI)",
    "QISHLOQ XO'JALIGI BO'LIMI",
    "MTP (QISHLOQ XO'JALIK TEXNIKASI VA MEXANIZATSIYA XIZMATI)",
    "KORXONA OLDI PTM (PAXTA TAYYORLASH MASKANI)",
    "G XASANOV PTM (PAXTA TAYYORLASH MASKANI)",
    "IJAND PTM (PAXTA TAYYORLASH MASKANI)",
    "BHR SPINNING MCHJ"
    "BAHAR MILK  MCHJ (CHORVACHILIK BO'LIMI)"
    "QORAJON TEKSTIL MCHJ"
    "BHR BETA TEKS MCHJ"
    "BHR OUTPUT MCHJ"
    "SAMARQAND COTTON CLASTER MCHJ"
    "FORTUNA TEKSTIL  MCHJ" 
    "ARAL ECO SPIN  MCHJ" 
]


FILTER_OPTIONS = [
    [types.InlineKeyboardButton("🔍 Javob berilmaganlar", callback_data="filter_status_unanswered")],
    [types.InlineKeyboardButton("✅ Javob berilganlar", callback_data="filter_status_answered")],
    [types.InlineKeyboardButton("🏢 Ish joyi bo'yicha", callback_data="filter_workplace")],
    [types.InlineKeyboardButton("🆔 Ma'lumot olish", callback_data="filter_get_info")]
]


def register_handlers(bot: TeleBot, user_bot_ref: TeleBot):
    @bot.message_handler(commands=['answer'])
    def handle_answer_command(message):
        if message.chat.id != ADMIN_GROUP_ID:
            bot.reply_to(message, "🔒 Bu komanda faqat admin guruhida ishlatilishi mumkin.")
            return
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "ℹ️ Foydalanish: /answer <so'rov_id>")
            return
        inquiry_id = args[1]
        if not inquiry_id.isdigit():
            bot.reply_to(message, "❌ Iltimos, to'g'ri so'rov ID sini kiriting (raqam).")
            return
        inquiry_id = int(inquiry_id)
        inquiry = get_inquiry_details(inquiry_id)
        if not inquiry:
            bot.reply_to(message, "❌ So'rov topilmadi.")
            return
        if inquiry[10] == "answered":
            bot.reply_to(message, "ℹ️ Bu so'rov allaqachon javob berilgan.")
            return

        ADMIN_STATE[message.from_user.id] = {"action": "answering", "inquiry_id": inquiry_id}
        bot.reply_to(message, f"📝 Iltimos, {inquiry_id} ID li so'rovga javob matnini yuboring:")



    @bot.message_handler(func=lambda message: ADMIN_STATE.get(message.from_user.id, {}).get("action") == "answering")
    def receive_answer(message):
        admin_id = message.from_user.id
        state = ADMIN_STATE.get(admin_id)
        if not state:
            bot.reply_to(message, "❌ Hech qanday faol so'rov yo'q.")
            return
        inquiry_id = state.get("inquiry_id")
        answer_text = message.text.strip()
        answer_inquiry(inquiry_id, answer_text)
        logger.info(f"Admin {admin_id} answered inquiry ID {inquiry_id}")

        # Get inquiry details and user_id
        inquiry = get_inquiry_details(inquiry_id)
        user_id = inquiry[1]

        # Use the user_bot_ref to send the answer message to the user
        user_bot_ref.send_message(
            user_id,
            f"✅ Sizning so'rovingiz (ID: {inquiry_id}) ga javob berildi:\n\n{answer_text}"
        )

        bot.reply_to(message, f"✅ So'rov ID {inquiry_id} javob berilgan holatda belgilandi.")
        del ADMIN_STATE[admin_id]



    @bot.message_handler(commands=['filter'])
    def handle_filter_command(message):
        if message.chat.id != ADMIN_GROUP_ID:
            bot.reply_to(message, "🔒 Bu komanda faqat admin guruhida ishlatilishi mumkin.")
            return
        markup = types.InlineKeyboardMarkup()
        for option in FILTER_OPTIONS:
            markup.add(*option)
        bot.send_message(
            message.chat.id,
            "🔍 Iltimos, filtr opsiyasini tanlang:",
            reply_markup=markup
        )



    @bot.callback_query_handler(func=lambda call: call.data.startswith("filter_"))
    def handle_filter_menu(call):
        if call.message.chat.id != ADMIN_GROUP_ID:
            bot.answer_callback_query(call.id, "🔒 Bu komanda faqat admin guruhida ishlatilishi mumkin.")
            return
        data = call.data

        if data == "filter_status_unanswered":
            inquiries = get_inquiries_by_status("unanswered")
            if not inquiries:
                bot.send_message(call.message.chat.id, "❌ Hech qanday javob berilmagan so'rov topilmadi.")
                return
            msg = "**Javob berilmagan so'rovlari**\n\n"
            for r in inquiries:
                msg += f"**ID**: {r[0]} | **Ish joyi**: {r[2]}\n"
            bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
        elif data == "filter_status_answered":
            inquiries = get_inquiries_by_status("answered")
            if not inquiries:
                bot.send_message(call.message.chat.id, "❌ Hech qanday javob berilgan so'rov topilmadi.")
                return
            msg = "**Javob berilgan so'rovlari**\n\n"
            for r in inquiries:
                msg += f"**ID**: {r[0]} | **Ish joyi**: {r[2]}\n"
            bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
        elif data == "filter_workplace":
            markup = types.InlineKeyboardMarkup()
            for workplace in WORKPLACE_OPTIONS:
                markup.add(types.InlineKeyboardButton(workplace, callback_data=f"filter_workplace_{workplace}"))
            markup.add(types.InlineKeyboardButton("⬅ Ortga", callback_data="back_to_filter_main"))
            bot.send_message(
                call.message.chat.id,
                "🏢 Iltimos, ish joyini tanlang:",
                reply_markup=markup
            )
        
        elif data.startswith("filter_workplace_"):
            workplace = data.split("_", 2)[2]
            inquiries = get_inquiries_by_workplace(workplace)
            if not inquiries:
                bot.send_message(call.message.chat.id, f"❌ {workplace} ish joyi uchun so'rov topilmadi.")
                return
            msg = f"**{workplace} Ish Joyi Bo'yicha So'rovlari**\n\n"
            for r in inquiries:
                msg += f"**ID**: {r[0]} | **Status**: {r[3]}\n"
            bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
        elif data == "filter_get_info":
            ADMIN_STATE[call.from_user.id] = {"action": "get_info"}
            bot.send_message(call.message.chat.id, "🆔 Iltimos, So'rov ID sini yuboring:")

        elif data == "back_to_filter_main":
            handle_filter_command(call.message)
        
        bot.answer_callback_query(call.id)



    @bot.message_handler(func=lambda message: ADMIN_STATE.get(message.from_user.id, {}).get("action") == "get_info")
    def handle_get_info(message):
        admin_id = message.from_user.id
        inquiry_id = message.text.strip()
        if not inquiry_id.isdigit():
            bot.reply_to(message, "❌ Iltimos, to'g'ri So'rov ID sini kiriting (raqam).")
            return
        inquiry_id = int(inquiry_id)
        inquiry = get_inquiry_details(inquiry_id)
        if not inquiry:
            bot.reply_to(message, "❌ So'rov topilmadi. Iltimos, boshqa ID ni sinab ko'ring.")
            return
        msg = (
            "**So'rov Tafsilotlari**\n\n"
            f"**So'rov ID**: {inquiry[0]}\n"
            f"**Foydalanuvchi ID**: {inquiry[1]}\n"
            f"**Ism**: {inquiry[3]}\n"
            f"**Familiya**: {inquiry[4]}\n"
            f"**Telefon**: {inquiry[5]}\n"
            f"**Ish joyi**: {inquiry[6]}\n"
            f"**Rol**: {inquiry[7]}\n"
            f"**So'rov**: {inquiry[8]}\n"
            f"**Holat**: {inquiry[10]}\n"
            f"**Javob**: {inquiry[9] if inquiry[9] else 'Hozircha javob yoq'}"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        del ADMIN_STATE[admin_id]



    @bot.message_handler(commands=['view'])
    def handle_view_command(message):
        if message.chat.id != ADMIN_GROUP_ID:
            bot.reply_to(message, "🔒 Bu komanda faqat admin guruhida ishlatilishi mumkin.")
            return
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "ℹ️ Foydalanish: /view <so'rov_id>")
            return
        inquiry_id = args[1]
        if not inquiry_id.isdigit():
            bot.reply_to(message, "❌ Iltimos, to'g'ri So'rov ID sini kiriting (raqam).")
            return
        inquiry_id = int(inquiry_id)
        inquiry = get_inquiry_details(inquiry_id)
        if not inquiry:
            bot.reply_to(message, "❌ So'rov topilmadi.")
            return
        msg = (
            "**So'rov Tafsilotlari**\n\n"
            f"**So'rov ID**: {inquiry[0]}\n"
            f"**Foydalanuvchi ID**: {inquiry[1]}\n"
            f"**Ism**: {inquiry[3]}\n"
            f"**Familiya**: {inquiry[4]}\n"
            f"**Telefon**: {inquiry[5]}\n"
            f"**Ish joyi**: {inquiry[6]}\n"
            f"**Rol**: {inquiry[7]}\n"
            f"**So'rov**: {inquiry[8]}\n"
            f"**Holat**: {inquiry[10]}\n"
            f"**Javob**: {inquiry[9] if inquiry[9] else 'Hozircha javob yoq'}"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")



    @bot.message_handler(func=lambda message: True)
    def handle_unknown(message):
        bot.send_message(message.chat.id, "😕 Noto'g'ri komanda yoki xatolik yuz berdi.")
