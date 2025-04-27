from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from logic import (
    generate_code_set,
    build_keyboard,
    is_correct_code,
    add_attempt,
    grant_extra_attempt,
    reset_game,
    game_state,
)

def wrap_buttons(keyboard):
    return [[InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"])] for btn in keyboard]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    generate_code_set(user_id)
    keyboard = build_keyboard(user_id)
    await update.message.reply_photo(
        photo="https://i.imgur.com/LtN1KxJ.jpeg",
        caption=(
            "🔐 Привет! Перед тобой *сейф с секретным кодом*.\n"
            "Угадай правильный *4-значный код* из списка. У тебя есть *3 попытки*! 💥\n\n"
            "_Если выиграешь — заберёшь подарок из сейфа!_"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(wrap_buttons(keyboard))
    )

async def handle_code_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = game_state.get(user_id)
    if not data:
        await query.edit_message_text("❗️ Сначала нажми /start.")
        return
    if data.get("game_over", False):
        return
    if not query.data.startswith("code_"):
        return

    code = int(query.data.split("_")[1])

    if is_correct_code(user_id, code):
        msg = f"🥳 *Поздравляем, код `{code}` подошёл!*\n\n🎁 От нашей команды сертификат на 1000 рублей и скидка 20% на все Беспроводные зарядки (скидка действует 3 дня).\n\n💬 Покажи это сообщение менеджеру и забирай свой приз, агент!"
        data["game_over"] = True
        await update_photo_message(query, msg, photo="https://i.imgur.com/TOk27xV.jpeg")
        return

    add_attempt(user_id, code)
    attempts = len(data["attempts"])

    if attempts < 3:
        remaining = 3 - attempts
        msg = f"🚫 Код *{code}* не сработал - лазеры всё ещё активны.\n\n🔢 Вводите следующий код! Осталось попыток: *{remaining}*."
        await update_photo_message(query, msg, photo="https://i.imgur.com/kFspFsU.jpeg", keyboard=build_keyboard_markup(user_id))
        return

    if attempts == 3 and not data.get("extra_attempt_used", False):
        text = (
            "🚨 К сожалению, вы не угадали код за 3 попытки - охрана уже выехала на место.\n\n"
            "🔔 Подпишитесь скорее на канал `@store941_ekb`, чтобы активировать экстренный протокол и получить 4-ю попытку."
        )
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Подписаться на канал", url="https://t.me/store941_ekb")],
            [InlineKeyboardButton("✅ Я подписался", callback_data="confirm_restart")]
        ])
        await update_photo_message(query, text, photo="https://i.imgur.com/zr43TCd.jpeg", keyboard=markup)
        return

    msg = (
        f"🐕‍🦺 Код *{code}* оказался неверным. На место приехала злая охрана — миссия провалена.\n\n"
        "🎁 Но перед побегом, вы захватили 500 бонусов на аксессуары в 9:41 Store!\n\n"
        "💬 Покажите данное сообщение менеджеру!"
    )
    data["game_over"] = True
    await update_photo_message(query, msg, photo="https://i.imgur.com/OyKepEO.jpeg")

async def confirm_restart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = game_state.get(user_id)
    if not data or len(data["attempts"]) != 3 or data.get("extra_attempt_used", False):
        await query.message.reply_text("⚠️ Дополнительная попытка недоступна.")
        return

    granted = grant_extra_attempt(user_id)
    if not granted:
        await query.message.reply_text("⚠️ Доп. попытка уже была использована.")
        return

    data["game_over"] = False
    await query.message.reply_photo(
        photo="https://i.imgur.com/bOEtJD6.jpeg",
        caption="🚨 Экстренный протокол активирован!\n\n🎧 У вас последняя — 4-я попытка взломать сейф. Удачи, агент!",
        parse_mode="Markdown",
        reply_markup=build_keyboard_markup(user_id)
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    reset_game(user_id)

    welcome_text = (
        "Агент, добро пожаловать в «Миссию Взлом» от 9:41 Store!\n\n"
        "🔍 Правила:\n\n"
        "— 3 попытки на взлом кода.\n"
        "— После 3 ошибок — можно запросить 4‑ю попытку.\n"
        "— За успешный взлом — награда!\n\n"
        "Нажмите «▶️ Начать миссию», чтобы приступить."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Начать миссию", callback_data="start_game")]
    ])

    await update.message.reply_photo(
        photo="https://i.imgur.com/HEPSIpi.jpeg",
        caption=welcome_text,
        reply_markup=keyboard
    )

async def start_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    reset_game(user_id)
    generate_code_set(user_id)

    await query.message.reply_photo(
        photo="https://i.imgur.com/kFspFsU.jpeg",
        caption="🎧 Агент, протокол запущен.\n\n🔢 Перед вами 10 кодовых вариаций — приступайте к взлому!",
        reply_markup=build_keyboard_markup(user_id)
    )

# Вспомогательные функции

def build_keyboard_markup(user_id):
    raw = build_keyboard(user_id)
    buttons = [InlineKeyboardButton(item["text"], callback_data=item["callback_data"]) for item in raw]
    rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(rows)

async def update_photo_message(query, text, photo=None, keyboard=None):
    if photo:
        await query.edit_message_media(
            media={"type": "photo", "media": photo, "caption": text, "parse_mode": "Markdown"},
            reply_markup=keyboard
        )
    else:
        if query.message.photo:
            await query.edit_message_caption(caption=text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)