import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage

from src import TELEGRAM_TOKEN, GIGACHAT_CREDENTIALS

# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация клиента GigaChat ---
giga = GigaChat(
    model="GigaChat-2-Max",
    credentials=GIGACHAT_CREDENTIALS,
    scope='GIGACHAT_API_PERS',
    verify_ssl_certs=False,
    profanity_check=True
)

# --- Предзагруженный файл с контекстом ---
with open(r"./data/Full_instruction_Create_Cards_WB_RDV_Market.pdf", "rb") as f:
    uploaded_file = giga.upload_file(f)

FILE_ID = uploaded_file.id_ 
print("ID предзагруженного файла:", FILE_ID)

# --- Приветственное сообщение ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот-помощник через GigaChat.\n"
        "Отправь любое сообщение, и я создам карточку товара с учётом предзагруженного контекста."
    )

# --- Основная логика ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    status_msg = await update.message.reply_text("⏳ Обрабатываю запрос через GigaChat...")

    try:
        messages = [
            ("system", """
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
            """),
            HumanMessage(
                content=user_message,
                additional_kwargs={
                    "attachments": [FILE_ID] 
                }
            )
        ]

       
        resp = giga.invoke(messages, request_kwargs={"timeout": 180})  
        response_text = resp.content if resp else "Нет ответа от GigaChat."

        await status_msg.edit_text(response_text)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка при обработке запроса. Попробуйте позже.")

# --- Запуск бота ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()

