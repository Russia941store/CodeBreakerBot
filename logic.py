import random

MAX_ATTEMPTS = 3
WINNING_CODE = 8064
MAX_TOTAL_CODES = 10

game_state = {}

def generate_code_set(user_id):
    used_codes = {WINNING_CODE}
    while len(used_codes) < MAX_TOTAL_CODES:
        used_codes.add(random.randint(1000, 9999))

    code_list = list(used_codes)
    random.shuffle(code_list)
    game_state[user_id] = {
        "codes": code_list,
        "attempts": [],
        "extra_attempt_used": False,
        "win": False,
        "game_over": False,
        "final_attempt_used": False
    }
    return code_list

def build_keyboard(user_id):
    data = game_state.get(user_id)
    if not data:
        return []

    buttons = []
    for code in data["codes"]:
        if code in data["attempts"]:
            if code == WINNING_CODE:
                text = f"✅ {code} ✅"
            else:
                text = f"❌ {code} ❌"
        else:
            text = str(code)
        buttons.append({"text": text, "callback_data": f"code_{code}"})
    return buttons

def is_correct_code(user_id, code):
    data = game_state.get(user_id)
    if data and not data["game_over"] and code == WINNING_CODE:
        data["win"] = True
        data["game_over"] = True
        return True
    return False

def add_attempt(user_id, code):
    data = game_state.get(user_id)
    if not data or data["game_over"]:
        return
    if code not in data["attempts"]:
        data["attempts"].append(code)
    if len(data["attempts"]) >= MAX_ATTEMPTS + (1 if data["extra_attempt_used"] else 0):
        data["game_over"] = True
        data["final_attempt_used"] = data["extra_attempt_used"] and len(data["attempts"]) >= (MAX_ATTEMPTS + 1)

def get_remaining_attempts(user_id):
    data = game_state.get(user_id)
    if not data or data["game_over"]:
        return 0
    limit = MAX_ATTEMPTS + (1 if data["extra_attempt_used"] else 0)
    return limit - len(data["attempts"])

def reset_game(user_id):
    generate_code_set(user_id)

def grant_extra_attempt(user_id):
    data = game_state.get(user_id)
    if data and not data["extra_attempt_used"]:
        attempt_limit = MAX_ATTEMPTS + (1 if data["extra_attempt_used"] else 0)
        if len(data["attempts"]) == MAX_ATTEMPTS:
            data["extra_attempt_used"] = True
            return True
    return False

def is_game_over(user_id):
    data = game_state.get(user_id)
    return data.get("game_over", False) if data else True

def is_win(user_id):
    data = game_state.get(user_id)
    return data.get("win", False) if data else False

def is_final_attempt_used(user_id):
    data = game_state.get(user_id)
    return data.get("final_attempt_used", False) if data else False