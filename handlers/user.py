"""
Programmer : Shoniyozov Imronbek 

filename : handlers/user.py

description : Handlers for the user part of the bot
"""


import logging

from telebot import TeleBot, types

from config import PRIVATE_CHANNEL_ID

from handlers.logic import submit_user_inquiry


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


STATE = {}

ANONYMOUS_STATE = {}

STATE["user_data"] = {}  # Initialize user_data so it's always available


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



def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.from_user.id
        logger.info(f"User {user_id} started the bot.")
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📋 So'rov yuborish", callback_data="submit_inquiry"),
            types.InlineKeyboardButton("🕶 Anonim yuborish", callback_data="submit_anonymous")
        )
        bot.send_message(
            message.chat.id,
            "👋 Salom va xush kelibsiz!\n\nMen sizga so'rovlarni oson yuborishda yordam berish uchun shu yerdaman.\n\nQanday davom etmoqchisiz?",
            reply_markup=markup
        )



    @bot.callback_query_handler(func=lambda call: call.data in ["submit_inquiry", "submit_anonymous"])
    def handle_submission_type(call):
        user_id = call.from_user.id
        if call.data == "submit_inquiry":
            STATE[user_id] = "awaiting_contact"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton("📱 Kontakt yuborish", request_contact=True))
            markup.add("⬅ Ortga")
            bot.send_message(
                call.message.chat.id,
                "Davom etish uchun, iltimos, kontakt ma'lumotlaringizni yuboring:",
                reply_markup=markup
            )
            logger.info(f"User {user_id} chose to submit a non-anonymous inquiry.")
        elif call.data == "submit_anonymous":
            ANONYMOUS_STATE[user_id] = "awaiting_workplace"
            markup = types.InlineKeyboardMarkup(row_width=1)
            for workplace in WORKPLACE_OPTIONS:
                markup.add(types.InlineKeyboardButton(workplace, callback_data=f"workplace_{workplace}"))
            markup.add(types.InlineKeyboardButton("⬅ Ortga", callback_data="back_to_start"))
            bot.send_message(
                call.message.chat.id,
                "Anonim so'rov uchun, iltimos, ish joyingizni tanlang:",
                reply_markup=markup
            )
            logger.info(f"User {user_id} chose to submit an anonymous inquiry.")
        bot.answer_callback_query(call.id)




    @bot.message_handler(content_types=['contact'])
    def handle_contact(message):
        user_id = message.from_user.id

        if ANONYMOUS_STATE.get(user_id) == "awaiting_contact":
            # Skip if user is submitting anonymously
            bot.send_message(
                message.chat.id,
                "Anonim so'rov uchun kontakt ma'lumotlari talab qilinmaydi.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.warning(f"User {user_id} submitted contact info during an anonymous inquiry, which is ignored.")
            return

        if STATE.get(user_id) == "awaiting_contact":
            contact = message.contact
            name = contact.first_name
            surname = contact.last_name if contact.last_name else "Ta'min etilmagan"
            phone = contact.phone_number

            # Initialize user_data for the user if not already present
            if user_id not in STATE["user_data"]:
                STATE["user_data"][user_id] = {}

            # Save the contact data
            STATE["user_data"][user_id]["name"] = name
            STATE["user_data"][user_id]["surname"] = surname
            STATE["user_data"][user_id]["phone"] = phone

            STATE[user_id] = "confirm_contact"
            logger.info(f"User {user_id} submitted a non-anonymous inquiry with contact.")

            # Create confirmation markup with an option to enter manually
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_contact"),
                types.InlineKeyboardButton("✏ O'zgartirish", callback_data="change_contact"),
                types.InlineKeyboardButton("📝 Qo'lda kiritish", callback_data="enter_manual_contact")
            )

            confirmation_message = (
                f"Quyidagi kontakt ma'lumotlari qabul qilindi:\n\n"
                f"👤 **Ism**: {name}\n"
                f"👤 **Familiya**: {surname}\n"
                f"📞 **Telefon**: {phone}\n\n"
                f"Bu ma'lumotlar to'g'rimi?"
            )

            bot.send_message(
                message.chat.id,
                confirmation_message,
                parse_mode="Markdown",
                reply_markup=markup
            )
            logger.info(f"Saved contact for user {user_id}: Name={name}, Surname={surname}, Phone={phone}")




    @bot.callback_query_handler(func=lambda call: call.data in ["confirm_contact", "change_contact", "enter_manual_contact"])
    def handle_contact_confirmation(call):
        user_id = call.from_user.id
        if call.data == "confirm_contact":
            if STATE.get(user_id) == "confirm_contact":
                STATE[user_id] = "awaiting_workplace"
                inquiry_type = "non-anonymous"
            elif ANONYMOUS_STATE.get(user_id) == "confirm_contact":
                ANONYMOUS_STATE[user_id] = "awaiting_workplace"
                inquiry_type = "anonymous"
            else:
                inquiry_type = "unknown"

            markup = types.InlineKeyboardMarkup(row_width=1)
            for workplace in WORKPLACE_OPTIONS:
                markup.add(types.InlineKeyboardButton(workplace, callback_data=f"workplace_{workplace}"))
            markup.add(types.InlineKeyboardButton("⬅ Ortga", callback_data="back_to_start"))
            bot.send_message(
                call.message.chat.id,
                "Ajoyib! Endi, iltimos, ish joyingizni tanlang:",
                reply_markup=markup
            )
            logger.info(f"User {user_id} confirmed contact for a {inquiry_type} inquiry.")
        elif call.data == "change_contact":
            if STATE.get(user_id) == "confirm_contact":
                STATE[user_id] = "awaiting_contact"
                inquiry_type = "non-anonymous"
            elif ANONYMOUS_STATE.get(user_id) == "confirm_contact":
                ANONYMOUS_STATE[user_id] = "awaiting_contact"
                inquiry_type = "anonymous"
            else:
                inquiry_type = "unknown"

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton("📱 Kontakt yuborish", request_contact=True))
            markup.add("⬅ Ortga")
            bot.send_message(
                call.message.chat.id,
                "Xo'sh, iltimos, kontakt ma'lumotlaringizni qayta yuboring:",
                reply_markup=markup
            )
            logger.info(f"User {user_id} opted to change contact for a {inquiry_type} inquiry.")
        elif call.data == "enter_manual_contact":
            if STATE.get(user_id) == "confirm_contact":
                STATE[user_id] = "enter_manual_contact_name"
                inquiry_type = "non-anonymous"
            elif ANONYMOUS_STATE.get(user_id) == "confirm_contact":
                ANONYMOUS_STATE[user_id] = "enter_manual_contact_name"
                inquiry_type = "anonymous"
            else:
                inquiry_type = "unknown"

            bot.send_message(
                call.message.chat.id,
                "Iltimos, ismingizni kiriting:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.info(f"User {user_id} chose to enter contact manually for a {inquiry_type} inquiry.")
        bot.answer_callback_query(call.id)



    @bot.message_handler(func=lambda message: STATE.get(message.from_user.id) == "enter_manual_contact_name")
    def handle_manual_contact_name(message):
        user_id = message.from_user.id
        name = message.text.strip()

        if not name:
            bot.send_message(
                message.chat.id,
                "❌ Iltimos, ismingizni kiriting:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        STATE["user_data"][user_id]["name"] = name
        STATE[user_id] = "enter_manual_contact_surname"
        bot.send_message(
            message.chat.id,
            "Iltimos, familiyangizni kiriting:"
        )
        logger.info(f"User {user_id} entered name manually: {name}")



    @bot.message_handler(func=lambda message: STATE.get(message.from_user.id) == "enter_manual_contact_surname")
    def handle_manual_contact_surname(message):
        user_id = message.from_user.id
        surname = message.text.strip()

        if not surname:
            bot.send_message(
                message.chat.id,
                "❌ Iltimos, familiyangizni kiriting:"
            )
            return

        STATE["user_data"][user_id]["surname"] = surname
        STATE[user_id] = "enter_manual_contact_phone"
        bot.send_message(
            message.chat.id,
            "Iltimos, telefon raqamingizni kiriting (format: +998XXXXXXXXX):"
        )
        logger.info(f"User {user_id} entered surname manually: {surname}")



    @bot.message_handler(func=lambda message: STATE.get(message.from_user.id) == "enter_manual_contact_phone")
    def handle_manual_contact_phone(message):
        user_id = message.from_user.id
        phone = message.text.strip()

        # Basic phone number validation
        if not phone.startswith("+998") or len(phone) != 13 or not phone[4:].isdigit():
            bot.send_message(
                message.chat.id,
                "❌ Iltimos, to'g'ri formatda telefon raqamingizni kiriting (misol: +998901234567):"
            )
            return

        STATE["user_data"][user_id]["phone"] = phone
        STATE[user_id] = "confirm_manual_contact"

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_manual_contact"),
            types.InlineKeyboardButton("✏ O'zgartirish", callback_data="change_manual_contact")
        )

        confirmation_message = (
            f"Quyidagi kontakt ma'lumotlari qabul qilindi:\n\n"
            f"👤 **Ism**: {STATE['user_data'][user_id].get('name')}\n"
            f"👤 **Familiya**: {STATE['user_data'][user_id].get('surname')}\n"
            f"📞 **Telefon**: {phone}\n\n"
            f"Bu ma'lumotlar to'g'rimi?"
        )

        bot.send_message(
            message.chat.id,
            confirmation_message,
            parse_mode="Markdown",
            reply_markup=markup
        )
        logger.info(f"User {user_id} entered phone manually: {phone}")



    @bot.callback_query_handler(func=lambda call: call.data in ["confirm_manual_contact", "change_manual_contact"])
    def handle_manual_contact_confirmation(call):
        user_id = call.from_user.id
        if call.data == "confirm_manual_contact":
            STATE[user_id] = "awaiting_workplace"
            markup = types.InlineKeyboardMarkup(row_width=1)
            for workplace in WORKPLACE_OPTIONS:
                markup.add(types.InlineKeyboardButton(workplace, callback_data=f"workplace_{workplace}"))
            markup.add(types.InlineKeyboardButton("⬅ Ortga", callback_data="back_to_start"))
            bot.send_message(
                call.message.chat.id,
                "Ajoyib! Endi, iltimos, ish joyingizni tanlang:",
                reply_markup=markup
            )
            logger.info(f"User {user_id} confirmed manual contact and is proceeding to workplace selection.")
        elif call.data == "change_manual_contact":
            STATE[user_id] = "enter_manual_contact_name"
            bot.send_message(
                call.message.chat.id,
                "Iltimos, ismingizni kiriting:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.info(f"User {user_id} opted to change manually entered contact information.")
        bot.answer_callback_query(call.id)



    @bot.callback_query_handler(func=lambda call: call.data.startswith("workplace_"))
    def handle_workplace_selection(call):
        user_id = call.from_user.id
        workplace = call.data.split("_", 1)[1]

        # Validate workplace selection
        if workplace not in WORKPLACE_OPTIONS:
            bot.answer_callback_query(
                call.id, "Noto'g'ri tanlov, iltimos qayta urinib ko'ring.", show_alert=True
            )
            logger.warning(f"User {user_id} selected an invalid workplace: {workplace}")
            return

        # Ensure user_data is initialized for the user
        if "user_data" not in STATE:
            STATE["user_data"] = {}
        if user_id not in STATE["user_data"]:
            STATE["user_data"][user_id] = {}

        # Set the workplace in the user's data
        STATE["user_data"][user_id]["workplace"] = workplace

        if ANONYMOUS_STATE.get(user_id) == "awaiting_workplace":
            # Transition to awaiting_inquiry for anonymous submissions
            ANONYMOUS_STATE[user_id] = "awaiting_inquiry"
            bot.send_message(
                call.message.chat.id,
                "Iltimos, so'rovingizni batafsil tasvirlang:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.info(f"User {user_id} selected workplace '{workplace}' for anonymous inquiry.")
        elif STATE.get(user_id) == "awaiting_workplace":
            # Non-anonymous inquiries proceed to ask for role
            STATE[user_id] = "awaiting_role"
            bot.send_message(
                call.message.chat.id,
                "Iltimos, b'olimizni kiriting (yoki o'tkazib yuborish uchun bo'lim yoq deb xabar yuboring):",
                reply_markup=types.ReplyKeyboardRemove()
            )
            logger.info(f"User {user_id} selected workplace '{workplace}' for non-anonymous inquiry.")
        else:
            logger.error(f"User {user_id} is in an unknown state during workplace selection.")

        bot.answer_callback_query(call.id)



    @bot.message_handler(func=lambda message: message.text == "⬅ Ortga")
    def handle_back(message):
        user_id = message.from_user.id
        was_in_state = False
        if user_id in STATE:
            del STATE[user_id]
            was_in_state = True
            logger.info(f"User {user_id} exited non-anonymous inquiry flow.")
        if user_id in ANONYMOUS_STATE:
            del ANONYMOUS_STATE[user_id]
            was_in_state = True
            logger.info(f"User {user_id} exited anonymous inquiry flow.")
        
        # user_data remains intact since it stores info for all users; 
        # deleting user_data[user_id] happens after inquiries are submitted.

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📋 So'rov yuborish", callback_data="submit_inquiry"),
            types.InlineKeyboardButton("🕶 Anonim yuborish", callback_data="submit_anonymous")
        )
        bot.send_message(
            message.chat.id,
            "Men sizga qanday yordam bera olaman?",
            reply_markup=markup
        )

        if not was_in_state:
            logger.warning(f"User {user_id} tried to go back but was not in any inquiry flow.")



    @bot.message_handler(func=lambda message: STATE.get(message.from_user.id) == "awaiting_role")
    def handle_role(message):
        user_id = message.from_user.id
        role = message.text.strip() if message.text.strip() else None
        # Ensure the user's entry in user_data exists
        if user_id not in STATE["user_data"]:
            STATE["user_data"][user_id] = {}
        STATE["user_data"][user_id]["role"] = role
        STATE[user_id] = "awaiting_inquiry"
        logger.info(f"User {user_id} set their role to '{role}'.")

        bot.send_message(
            message.chat.id,
            "Iltimos, so'rovingizni batafsil tasvirlang:",
            reply_markup=types.ReplyKeyboardRemove()
        )



    @bot.message_handler(func=lambda message: STATE.get(message.from_user.id) == "awaiting_inquiry")
    def handle_inquiry(message):
        user_id = message.from_user.id
        # user_data and user_id entry should exist by now
        user_data = STATE["user_data"].get(user_id, {})
        inquiry_text = message.text.strip()
        username = message.from_user.username if message.from_user.username else "Anonim"
        name = user_data.get("name")
        surname = user_data.get("surname")
        phone = user_data.get("phone")
        workplace = user_data.get("workplace")
        role = user_data.get("role")

        # Determine if it's an anonymous inquiry
        is_anonymous = False
        if ANONYMOUS_STATE.get(user_id) == "awaiting_role":
            is_anonymous = True
            username = "Anonim"

        # Log the data being submitted
        logger.info(f"Submitting inquiry for user {user_id}: "
                    f"Name={name}, Surname={surname}, Phone={phone}, "
                    f"Workplace={workplace}, Role={role}, Inquiry='{inquiry_text}', "
                    f"Username='{username}', Anonymous={is_anonymous}")

        # Submit the inquiry
        inquiry_id = submit_user_inquiry(
            user_id=user_id,
            username=username,
            name=name,
            surname=surname,
            phone=phone,
            workplace=workplace,
            role=role,
            inquiry_text=inquiry_text
        )
        logger.info(f"User {user_id} submitted inquiry ID {inquiry_id}")

        # Send confirmation to the user
        confirmation_text = (
            "✅ Sizning so'rovingiz muvaffaqiyatli yuborildi!\n\n"
            "Biz bilan bog'langaningiz uchun rahmat. Tez orada sizga javob beramiz.\n\n"
            "Yangi savol berish uchun /start comandasisni yoboring"
        )
        bot.send_message(
            message.chat.id,
            confirmation_text,
            reply_markup=types.ReplyKeyboardRemove()
        )

        # Prepare admin message
        if is_anonymous:
            admin_message = (
                "**Yangi Anonim So'rov Qabul Qilindi**\n\n"
                f"**So'rov ID**: {inquiry_id}\n"
                f"**Foydalanuvchi ID**: {user_id}\n"
                f"**Ish joyi**: {workplace}\n"
                f"**Rol**: {role}\n"
                f"**So'rov**: {inquiry_text}"
            )
        else:
            admin_message = (
                "**Yangi So'rov Qabul Qilindi**\n\n"
                f"**So'rov ID**: {inquiry_id}\n"
                f"**Foydalanuvchi ID**: {user_id}\n"
                f"**Ism**: {name}\n"
                f"**Familiya**: {surname}\n"
                f"**Telefon**: {phone}\n"
                f"**Ish joyi**: {workplace}\n"
                f"**Rol**: {role}\n"
                f"**So'rov**: {inquiry_text}"
            )

        # Send the inquiry details to the private channel
        bot.send_message(
            PRIVATE_CHANNEL_ID,
            admin_message,
            parse_mode="Markdown"
        )

        # Remove this user's data after submission
        del STATE["user_data"][user_id]
        del STATE[user_id]
        if ANONYMOUS_STATE.get(user_id):
            del ANONYMOUS_STATE[user_id]

    # Remove the duplicate handle_anon_inquiry by keeping only one function
    # The manual contact handling is integrated above


    @bot.message_handler(func=lambda message: ANONYMOUS_STATE.get(message.from_user.id) == "awaiting_inquiry")
    def handle_anonymous_inquiry(message):
        user_id = message.from_user.id
        inquiry_text = message.text.strip()
        workplace = STATE["user_data"][user_id].get("workplace")

        # Log the data being submitted
        logger.info(f"Submitting anonymous inquiry for user {user_id}: "
                    f"Workplace={workplace}, Inquiry='{inquiry_text}'")

        # Submit the inquiry to the database and get the inquiry ID
        try:
            inquiry_id = submit_user_inquiry(
                user_id=user_id,
                username="Anonim",
                name=None,
                surname=None,
                phone=None,
                workplace=workplace,
                role=None,
                inquiry_text=inquiry_text
            )
            logger.info(f"Anonymous inquiry submitted with ID {inquiry_id} for user {user_id}.")
        except Exception as e:
            logger.error(f"Failed to submit anonymous inquiry for user {user_id}: {e}")
            bot.send_message(
                message.chat.id,
                "❌ So'rovni yuborishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
            )
            return

        # Notify admin
        admin_message = (
            "**Yangi Anonim So'rov Qabul Qilindi**\n\n"
            f"**So'rov ID**: {inquiry_id}\n"
            f"**Foydalanuvchi ID**: {user_id}\n"
            f"**Ish joyi**: {workplace}\n"
            f"**So'rov**: {inquiry_text}"
        )
        bot.send_message(
            PRIVATE_CHANNEL_ID,
            admin_message,
            parse_mode="Markdown"
        )

        # Notify user
        bot.send_message(
            message.chat.id,
            "✅ Sizning anonim so'rovingiz muvaffaqiyatli yuborildi! Tez orada sizga javob beramiz.",
            reply_markup=types.ReplyKeyboardRemove()
        )

        # Clean up state
        del ANONYMOUS_STATE[user_id]
        del STATE["user_data"][user_id]




    @bot.message_handler(func=lambda message: True)
    def handle_unknown(message):
        user_id = message.from_user.id
        logger.warning(f"User {user_id} sent an unknown command or message.")
        bot.send_message(message.chat.id, "😕 Noto'g'ri komanda yoki xatolik yuz berdi. Iltimos, /start komandasini yuboring.")
