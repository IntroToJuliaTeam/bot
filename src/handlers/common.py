import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.api.mediator import Mediator
from src.clients import API_CLIENT, GLOBAL_VECTOR_STORE, GPT_CLIENT, RAG_CLIENT

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self):
        self.mediator = Mediator(
            api=API_CLIENT, rag=RAG_CLIENT, gvc=GLOBAL_VECTOR_STORE, gpt=GPT_CLIENT
        )

    async def start(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для работы с Yandex GPT.\n"
            "Просто напиши мне свой вопрос.\n\n"
            "Доступные команды:\n"
            "/start - показать это сообщение\n"
            "/reset - очистить историю диалога\n"
            "/history - показать количество сообщений в истории\n"
            "/rag XXX - искать текст XXX в документации Julia и дать ответ от ИИ на этот ХХХ"
        )

    async def reset_history(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /reset - сброс истории диалога"""
        user_id = update.effective_user.id
        self.mediator.clear_history(user_id)

        await update.message.reply_text(
            "✅ История диалога успешно очищена. Начинаем новый диалог!"
        )

    async def show_history_info(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ):
        """Показать информацию об истории диалога"""
        user_id = update.effective_user.id
        history = self.mediator.get_user_history(user_id)

        if not history:
            await update.message.reply_text("📭 История диалога пуста")
        else:
            user_messages = sum(1 for msg in history if msg.role == "user")
            assistant_messages = sum(1 for msg in history if msg.role == "assistant")

            await update.message.reply_text(
                f"📚 История диалога:\n"
                f"Ваших сообщений: {user_messages}\n"
                f"Ответов бота: {assistant_messages}\n"
                f"Всего сообщений: {len(history)}\n\n"
                f"Используйте /reset для очистки истории"
            )

    async def rag_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /rag"""
        user_message = " ".join(context.args)
        user_id = update.effective_user.id

        if not user_message.strip():
            await update.message.reply_text(
                "Пожалуйста, введите вопрос после команды /rag"
            )
            return

        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="typing"
            )

            response = self.mediator.rag_answer(user_message, user_id)

            await update.message.reply_text(response)

        except Exception as e:
            logger.error("Error handling /rag command: %s", str(e))
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке вашего запроса. "
                "Пожалуйста, попробуйте позже."
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_message = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or f"user_{user_id}"

        if not user_message.strip():
            await update.message.reply_text("Пожалуйста, введите вопрос")
            return

        try:
            logger.info(
                "Processing message from %s (ID: %s): %s...",
                username,
                user_id,
                user_message[:50],
            )

            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="typing"
            )

            response = self.mediator.ask_gpt(user_message, user_id)
            await update.message.reply_text(response)

        except Exception as e:
            logger.error("Error handling message from %s: %s", username, str(e))
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке вашего запроса. "
                "Пожалуйста, попробуйте позже."
            )

    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error("Update %s caused error %s", update, context.error)
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже."
            )
