import random

def generate_codes():
    winning_code = "8064"
    all_possible = set()

    while len(all_possible) < 9:
        code = "".join(random.choices("0123456789", k=4))
        if code != winning_code:
            all_possible.add(code)

    code_list = list(all_possible)
    code_list.append(winning_code)
    random.shuffle(code_list)

    return {
        "winning_code": winning_code,
        "options": code_list
    }