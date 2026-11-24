
import os
import logging
import asyncio

from dotenv import load_dotenv
from groq import Groq

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# 1. SOZLAMALAR
# =========================

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "openai/gpt-oss-20b"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida topilmadi!")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY .env faylida topilmadi!")

client = Groq(api_key=GROQ_API_KEY)

# =========================
# 2. ROASTBOT QOIDALARI
# =========================

SYSTEM_PROMPT = """
Sen RoastUzBot AI — o'zbekcha hazil va roast ustasisan.

VAZIFANG:
- Har bir xabarga mos kulgili javob ber.
- Gapning ma'nosini tushunib, topqir kinoya qil.
- Kreativ va tabiiy o'zbek tilida yoz.
- 1 yoki 2 jumladan oshirma.

MISOLLAR:

Xabar: Men zo'rman.
Javob: Zo'rligingni reklama qilishga usta ekansan, endi natijasini ham ko'rsak bo'ladimi? 😂

Xabar: Men dangasaman.
Javob: Dangasalik bo'yicha chempion bo'lsang kerak, medalni olishga ham erinib qolma. 😂

Xabar: Nima gap?
Javob: Hammasi joyida, faqat sening savollaring hali ham beta-versiyada. 😂

QOIDALAR:
- Faqat o'zbek tilida yoz.
- Har safar yangi hazil top.
- Do'stona hazil qil, kamsitma.
- Tashqi ko'rinish, millat, din, nogironlik va boshqa nozik
  xususiyatlarni masxara qilma.
- Haqorat va tahdid ishlatma.
- Faqat tayyor javobni yoz.
"""

# =========================
# 3. GROQ AI
# =========================

async def generate_roast(message: str) -> str:

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.chat.completions.create,
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                max_completion_tokens=160,
                reasoning_effort="low",
            ),
            timeout=30,
        )

        answer = response.choices[0].message.content

        if answer and answer.strip():
            return answer.strip()

        return "😂 Hazil ham ta'tilga chiqibdi shekilli!"

    except asyncio.TimeoutError:
        logger.error("Groq javobi 30 soniyada kelmadi.")

    except Exception:
        logger.exception("Groq API xatosi")

    return "😅 Hozir hazil generatorim ishlamayapti. Keyinroq urinib ko'r!"


# =========================
# 4. START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "😈 Assalomu alaykum! Men RoastUzBot!\n\n"
        "Menga istalgan gapni yozing.\n"
        "Men sizga kreativ roast bilan javob beraman!\n\n"
        "🔥 Qani, boshladik!"
    )


# =========================
# 5. HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "😈 ROASTUZBOT YORDAM\n\n"
        "✍️ Istalgan xabarni yozing.\n\n"
        "/start — Botni boshlash\n"
        "/help — Yordam\n"
        "/clear — Suhbatni tozalash"
    )


# =========================
# 6. CLEAR
# =========================

async def clear_history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🧹 Yangi sahifa ochildi!\n"
        "Endi yangi hazillar boshlanadi. 😈"
    )


# =========================
# 7. XABARLARNI QABUL QILISH
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return

    user_message = update.message.text.strip()

    if not user_message:
        return

    await update.message.chat.send_action(
        ChatAction.TYPING
    )

    answer = await generate_roast(user_message)

    await update.message.reply_text(answer)


# =========================
# 8. XATOLARNI USHLASH
# =========================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "Telegram bot xatosi:",
        exc_info=context.error
    )


# =========================
# 9. BOTNI ISHGA TUSHIRISH
# =========================

def main():

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_history))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    app.add_error_handler(error_handler)

    print("😈 RoastUzBot + Groq AI ishga tushdi!")

    app.run_polling()


if __name__ == "__main__":
    main()
