
from aiogram import Bot, Dispatcher, types
from aiohttp import web
import asyncio
import os
from instaloader_wrapper import InstaloaderWrapper

API_TOKEN = "👉 8201685441:AAEOP4pi-AbI0OmJU4O2VB_G-Zuns8GBpTo 👈"

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message()
async def handler(message: types.Message):
    text = message.text.strip()

    if text == "/start":
        await message.answer(
            "👋 Salom! Men Instagram video yuklab beruvchi botman 📲\n\n"
            "🎬 Menga istalgan Instagram post havolasini yuboring, men uni sizga yuklab beraman ✅\n\n"
            "📌 Masalan:\nhttps://www.instagram.com/p/XXXXXXXXXXX\n\n"
            "👨‍💻 Dasturchi: @yourabu"
        )

    elif text == "/help":
        await message.answer(
            "🆘 Yordam:\n\n"
            "1️⃣ Instagramdan post yoki reels havolasini yuboring\n"
            "2️⃣ Bot avtomatik tarzda videoni sizga yuboradi 🎥\n\n"
            "⚠️ Faqat ochiq (public) akkauntlardagi videolarni yuklab bo‘ladi!"
        )

    elif "instagram.com" in text:
        await message.answer("🔄 Yuklanmoqda, biroz kuting...")

        try:
            loader = InstaloaderWrapper()
            media_url = loader.get_post_url(text)

            if media_url.endswith(".mp4"):
                await message.answer_video(media_url, caption="🎬 Mana sizning videongiz ✅")
            else:
                await message.answer_photo(media_url, caption="📸 Mana sizning rasm(laringiz) ✅")

        except Exception as e:
            print("Xato:", e)
            await message.answer("⚠️ Videoni yuklab bo‘lmadi. Havolani tekshirib qayta urinib ko‘ring.")

    else:
        await message.answer("ℹ️ Faqat Instagram post yoki reels havolasini yuboring.")


# --- Webhook qismi ---
async def handle(request):
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return web.Response()


async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")


async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 Bot to‘xtatildi")


def start():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
