import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start_command, start_game_callback, handle_code_choice, confirm_restart_callback

logging.basicConfig(level=logging.INFO)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(start_game_callback, pattern='^start_game$'))
    app.add_handler(CallbackQueryHandler(confirm_restart_callback, pattern='^confirm_restart$'))
    app.add_handler(CallbackQueryHandler(handle_code_choice, pattern='^code_'))

    print("🚀 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()

# маленькое тестовое изменение для Amvera