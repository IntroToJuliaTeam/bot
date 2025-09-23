import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.gpt import test
from src.handlers.common import BotHandlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.environ["BOT_TOKEN"]


def main():
    """Основная функция"""

    test()

    try:
        logger.info("Инициализация компонентов...")

        handlers = BotHandlers()

        application = Application.builder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", handlers.start))
        application.add_handler(CommandHandler("reset", handlers.reset_history))
        application.add_handler(CommandHandler("history", handlers.show_history_info))
        application.add_handler(CommandHandler("rag", handlers.rag_command))

        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message)
        )

        application.add_error_handler(BotHandlers.error_handler)

        logger.info("Бот запускается...")
        application.run_polling()

    except KeyError as e:
        logger.error("Отсутствует необходимая переменная окружения: %s", str(e))
    except Exception as e:
        logger.error("Failed to start bot: %s", str(e))


if __name__ == "__main__":
    main()
