# keyboard.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_keyboard(codes, selected_codes=None, correct_code=None):
    selected_codes = selected_codes or []
    keyboard = []

    for code in codes:
        if code in selected_codes:
            if code == correct_code:
                btn = InlineKeyboardButton(f"✅ {code} ✅", callback_data="noop")
            else:
                btn = InlineKeyboardButton(f"❌ {code} ❌", callback_data="noop")
        else:
            btn = InlineKeyboardButton(code, callback_data=f"code_{code}")
        keyboard.append([btn])

    return InlineKeyboardMarkup(keyboard)