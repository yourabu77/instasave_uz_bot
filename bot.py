from aiogram import Bot, Dispatcher, types
from aiohttp import web
import asyncio
import instaloader
import os

API_TOKEN = "8201685441:AAEOP4pi-AbI0OmJU4O2VB_G-Zuns8GBpTo"  # Bot tokeningni shu yerga yoz
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    if message.text == "/start":
        await message.answer(
            "📸 Instagram Video Saver Bot'ga xush kelibsiz!\n\n"
            "🔗 Menga Instagram post, reel yoki video havolasini yuboring — "
            "men sizga videoni yuboraman 🎥"
        )
    elif "instagram.com" in message.text:
        await message.answer("⏳ Yuklanmoqda, biroz kuting...")
        try:
            loader = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)
            post = instaloader.Post.from_shortcode(loader.context, message.text.split("/")[-2])
            video_url = post.video_url
            await message.answer_video(video_url, caption="✅ Mana siz so‘ragan video!")
        except Exception as e:
            await message.answer("❌ Videoni yuklab bo‘lmadi. Havolani tekshirib ko‘ring.")
    else:
        await message.answer("Iltimos, faqat Instagram havolasini yuboring 🔗")

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook o‘rnatildi: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

async def handle(request):
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return web.Response()

def start():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    start()
