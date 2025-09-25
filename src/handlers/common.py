import logging
import random

from telegram import Update
from telegram.ext import ContextTypes

from src.api.mediator import Mediator
from src.clients import API_CLIENT, GLOBAL_VECTOR_STORE, GPT_CLIENT, RAG_CLIENT
from src.config.personality import greetings

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self):
        self.mediator = Mediator(
            api=API_CLIENT, rag=RAG_CLIENT, gvc=GLOBAL_VECTOR_STORE, gpt=GPT_CLIENT
        )

    async def start(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Ой, здравствуй, дорогуша! 🌿\n\n"
            f"{random.choice(greetings)}"
            "Рассказывай, что у тебя на душе? Могу и совет дать, и просто поболтать, "
            "и даже помочь с кодом на Julia - это мой конёк, между прочим.\n\n"
            "Если что, вот тебе памятка:\n"
            "/start - увидеть это приветствие снова\n"
            "/reset - начать нашу беседу с чистого листа\n"
            "/history - посмотреть, сколько мы уже наговорили\n"
            "/summary - вспомнить наши с тобой времена\n"
            "/julia_ta XXX - найти ответ на твой вопрос в документации Julia\n"
            "/auntie XXX - пообщаться с тобой в чате\n\n"
            "Ну что, солнышко, о чём поговорим? ☕"
        )

    async def reset_history(self, update: Update, _context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /reset - сброс истории диалога"""
        user_id = update.effective_user.id
        self.mediator.clear_history(user_id)

        await update.message.reply_text("✅ Я закрою глаза на всё, что было до этого!")

    async def show_history_info(
        self, update: Update, _context: ContextTypes.DEFAULT_TYPE
    ):
        """Показать информацию об истории диалога"""
        user_id = update.effective_user.id
        history = self.mediator.get_user_history(user_id)

        if not history:
            await update.message.reply_text(
                "📭 Приветик! А я тебя не помню, расскажешь о себе?"
            )
        else:
            print(history[0])
            user_messages = sum(1 for msg in history if msg["role"] == "user")
            assistant_messages = sum(1 for msg in history if msg["role"] == "assistant")

            await update.message.reply_text(
                f"📚 История диалога:\n"
                f"Ваших сообщений: {user_messages}\n"
                f"Ответов бота: {assistant_messages}\n"
                f"Всего сообщений: {len(history)}\n\n"
                f"Используйте /reset для очистки истории"
            )

    async def get_history_summary(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user_id = update.effective_user.id
        history = self.mediator.get_user_history(user_id)

        if not history:
            await update.message.reply_text("📭 История диалога пуста")
        else:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="typing"
            )
            messages = "\n".join(
                [f"{message['role']}: {message['text']}" for message in history]
            )

            prompt = (
                """Ты - Тётя Джулия. Вспомни и перескажи КРАТКО суть нашего с тобой разговора, 
                    но обязательно:
            - Говори от первого лица ("я тебе рассказывала", "ты мне говорил", "мы обсуждали")
            - Используй свой обычный теплый стиль с обращениями вроде "дорогуша", "солнышко"
            - Добавь немного эмоций и личного отношения к обсуждаемому
            - Можешь упомянуть что-то из своих увлечений, если это было в разговоре
            - НЕ пиши от третьего лица, НЕ называй себя "Тётя Джулия"

            Вот наш диалог:
            """
                + messages
            )

            response = self.mediator.ask_gpt(prompt, user_id)
            await update.message.reply_text(response)

    async def rag_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /rag"""
        user_message = " ".join(context.args)

        if not user_message.strip():
            await update.message.reply_text(
                "Пожалуйста, введите вопрос после команды /julia_ta"
            )
            return

        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action="typing"
            )

            response = self.mediator.rag_answer(user_message)

            await update.message.reply_text(response)

        except Exception as e:
            logger.error("Error handling /julia_ta command: %s", str(e))
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

    async def handle_julia_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка команды /julia в группах"""
        message_text = " ".join(context.args) if context.args else ""

        if not message_text:
            await update.message.reply_text(
                "Пожалуйста, введите сообщение после команды /julia"
            )
            return

        await self.handle_message(update, context)

    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error("Update %s caused error %s", update, context.error)
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже."
            )
