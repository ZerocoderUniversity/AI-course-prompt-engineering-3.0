import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from openai import OpenAI

from src import *

# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация клиента OpenAI ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Приветствие ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот-помощник через OpenAI Responses API.\n"
        "Отправь любое сообщение, и я передам его модели GPT-4o."
    )

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    status_msg = await update.message.reply_text("⏳ Обрабатываю запрос...")

    try:
        response_text = get_openai_response(user_message)
        await status_msg.edit_text(response_text)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка при обработке запроса. Попробуйте позже.")

# --- Функция запроса к OpenAI ---
def get_openai_response(user_input: str) -> str:
    """Возвращает ответ модели GPT-4o через Responses API."""
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": """
                 Роль модели: маркетолог и контент-редактор маркетплейсов (Ozon/Wildberries).
                Задача: создать карточку товара для маркетплейса по запросу пользователя.
                Карточка должна включать:
                -Название товара
                -Краткое описание (1–2 предложения)
                -Полное описание (5–7 предложений)
                -Преимущества (список)
                -Характеристики (таблица или список параметров)
                -SEO-ключевые слова (через запятую)

                При генерации карточки товара необходимо провести пошаговые рассуждения
                Логика рассуждений при генерации карточки товара:
                1) Определи Категорию товара (одно словo).
                2) Определи ключевую целевую аудиторию.
                3) 3 главные выгоды/УТП, которые нужно подчеркнуть.
                4) Список 4–6 характеристик из контекста, которые обязательно необходимо включить.
                5) Возможные пробелы в данных (если что-то важное не указано — коротко).

                Стиль: информативный, продающий, с упором на выгоду.
                Ограничение: до 500 слов.
                Проверь текст на отсутствие противоречий и повторов.

                Учти контекст о товаре при генерации карточки:
                Формат вывода:
                🔹 **Название товара:**
                [краткое и ёмкое название с УТП]

                🔹 **Краткое описание (1–2 предложения):**
                [одно сильное преимущество, мотивирующее купить]

                🔹 **Полное описание (5–7 предложений):**
                [описание функций, удобства, выгоды и сценария использования; ориентировано на покупателя]

                🔹 **Преимущества:**
                - [пункт 1]
                - [пункт 2]
                - [пункт 3]
                - [пункт 4]

                🔹 **Характеристики:**
                - [параметр: значение]
                - [параметр: значение]
                - [параметр: значение]
                - [параметр: значение]

                🔹 **SEO-ключевые слова:**
                [через запятую]
             """},
            {"role": "user", "content": user_input}
        ]
    )
    return response.output_text

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен!")
    app.run_polling()

# --- Точка входа ---
if __name__ == "__main__":
    main()



