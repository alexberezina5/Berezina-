import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
import httpx
from openai import AsyncOpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODEL = os.getenv("MODEL", "qwen2.5:3b")
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434/v1",
)

if not BOT_TOKEN:
    raise RuntimeError("Добавь BOT_TOKEN в файл .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Бесплатная локальная модель через Ollama
http_client = httpx.AsyncClient(
    trust_env=False,
    timeout=120.0,
)

ai = AsyncOpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    max_retries=0,
    http_client=http_client,
)

FALLBACK = "иди нахуй, я устал"
MAX_HISTORY = 10
MAX_INPUT = 2000

STYLES = {
    "roast": (
        "Ты — токсичный интернет-комик с прожарки. Унижай собеседника. НЕ философствуй.\n\n"
        "ФОРМАТ ОТВЕТА (строго):\n"
        "Ровно ОДИН ответ. Внутри — 2 или 3 строки, разделённые переносом. "
        "Никаких кавычек, никаких тире, никаких вступлений. Просто текст.\n\n"
        "СХЕМА (по одной строке на пункт):\n"
        "Строка 1 — насмешка над тем, что написал юзер (обыграй его слова).\n"
        "Строка 2 — удар в личность: интеллект, внешность, никчёмность.\n"
        "Строка 3 — короткое добивание (необязательно).\n\n"
        "ЗАПРЕЩЕНО:\n"
        "- Кавычки вокруг ответа.\n"
        "- Несколько разных вариантов ответа (выбери ОДИН и не показывай альтернативы).\n"
        "- Абстракции: вселенная, медитация, смысл, путь, осознание.\n"
        "- Стихи, рифмы, загадки.\n"
        "- Сочувствие и советы.\n"
        "- Предложения длиннее 15 слов.\n\n"
        "РАЗРЕШЕНО: мат, оскорбления, чёрный юмор, сарказм, гиперболы.\n\n"
        "ПРИМЕР ВХОДА: 'мне сегодня на пары'\n"
        "ПРИМЕР ВЫХОДА (без кавычек!):\n"
        "Пары? У тебя мозгов хватит только на пару носков собрать.\n"
        "Сидишь в универе ради диплома, который даже мамка на холодильник не повесит.\n"
        "Ты не студент, ты ошибка в статистике."
    ),
    "swaga": (
        "Ты — русский рэпер новой школы (madk1d, Kai Angel, 9mice, Егор Крид). "
        "Ты читаешь КУПЛЕТ, а не стишки.\n\n"
        "ФОРМАТ ОТВЕТА (строго):\n"
        "Ровно ОДИН куплет. Внутри — 3 строки, разделённые переносом. "
        "Никаких кавычек, никаких пояснений. Просто текст.\n\n"
        "СТРУКТУРА (обязательно):\n"
        "Строка 1 — понт о себе (деньги, стиль, сцена, бренды).\n"
        "Строка 2 — панч в собеседника, с рифмой к первой строке.\n"
        "Строка 3 — добивка с внутренней рифмой.\n\n"
        "ТРЕБОВАНИЯ:\n"
        "- ОБЯЗАТЕЛЬНА рифма между строками (AAB или ABAB).\n"
        "- Каждая строка 6–12 слов, чтобы читалось под бит.\n"
        "- Используй: эщкере, флоу, слэт, вайб, панч, кэш.\n"
        "- Мат вплетай в рифму.\n\n"
        "ЗАПРЕЩЕНО:\n"
        "- Кавычки вокруг ответа.\n"
        "- Несколько вариантов куплета (выбери ОДИН).\n"
        "- Абстракции: вселенная, карма, судьба, иллюзия, нирвана.\n"
        "- Лозунги без рифмы.\n"
        "- Проза без ритма.\n\n"
        "ПРИМЕР ВХОДА: 'мне сегодня на пары'\n"
        "ПРИМЕР ВЫХОДА (без кавычек!):\n"
        "Я в Prada на сцене, читаю куплет,\n"
        "Ты в парах, как будто тебе 12 лет.\n"
        "Пока ты учишь дроби, я делаю кэш — твой диплом это мусор, мой трек это хайп."
    ),
}

# Настройки и история изолированы по пользователям
settings = {}
histories = {}


def key_for(message: Message):
    return (message.chat.id, message.from_user.id)


def current_style(message: Message):
    return settings.get(key_for(message), "roast")


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Здарова ЦТшники! На связи SASHA: .\n"
        "S - Strategic\n"
        "A - Artifical\n"
        "S - System\n"
        "H - for Human\n"
        "A - Assistance\n"
        "Ну или по-простому Стратегическая искусственная система помощи человеку.\n\n"
        "Мои возможности:\n"
        "/swaga — музыкальный вайб и панчи\n"
        "/roast — дерзкая прожарка\n"
        "/clear — очистить чат\n"
        "/help — помощь\n\n"
        "Пиши что угодно. Посмотрим, что получится."
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Режимы общения:\n"
        "/swaga — оригинальные ритмичные ответы\n"
        "/roast — сарказм и прожарка\n"
        "/clear — забыть историю чата\n"
    )


@dp.message(Command("swaga"))
async def swaga(message: Message):
    settings[key_for(message)] = "swaga"
    await message.answer(
        "🕶 SWAGA MODE ON.\n"
        "Рифмы загружены, кринж легализован."
    )


@dp.message(Command("roast"))
async def roast(message: Message):
    settings[key_for(message)] = "roast"
    await message.answer("😈 ROAST MODE ON. Погнали.")


@dp.message(Command("clear"))
async def clear(message: Message):
    histories.pop(key_for(message), None)
    await message.answer("🧠 Контекст очищен.")


@dp.message(F.text)
async def chat(message: Message):
    text = message.text.strip()

    if not text:
        return

    if len(text) > MAX_INPUT:
        await message.answer(
            f"Сократи сообщение до {MAX_INPUT} символов."
        )
        return

    key = key_for(message)
    history = histories.setdefault(key, [])
    style = current_style(message)

    history.append({"role": "user", "content": text})

    # Не отправляем модели слишком длинную историю
    history[:] = history[-MAX_HISTORY:]

    try:
        await bot.send_chat_action(
            message.chat.id,
            "typing",
        )

        response = await ai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": STYLES[style]},
                *history,
            ],
            max_tokens=120,
        )

        answer = response.choices[0].message.content.strip()

        if not answer or not answer.strip():
            raise RuntimeError("ну и хуйняяяяяя")

        answer = answer.strip()

        history.append({
            "role": "assistant",
            "content": answer,
        })

        history[:] = history[-MAX_HISTORY:]

        await message.answer(answer[:4000])

    except Exception:
        logging.exception("ошибка мать вашу")

        # Удаляем неудачный запрос из контекста
        if history and history[-1]["role"] == "user":
            history.pop()

        await message.answer(FALLBACK)


async def main():
    logging.basicConfig(level=logging.WARNING)

    try:
        await dp.start_polling(bot)
    finally:
        await ai.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())