from aiogram import Bot, Dispatcher, types
from aiohttp import web
import os
import instaloader
import asyncio

API_TOKEN = os.getenv("API_TOKEN")  # tokenni Environment variable dan oling

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# /start komandasi
@dp.message()
async def start_handler(message: types.Message):
    if message.text == "/start":
        await message.answer(
            "👋 Salom! Bu bot orqali siz Instagram'dan videolarni yuklab olishingiz mumkin.\n\n"
            "📌 Faqat video postlarni yuboring (havola bilan):\n\n"
            "Masalan:\n"
            "https://www.instagram.com/reel/xxxxx\n\n"
            "👨‍💻 Dasturchi: @yourabu"
        )
    elif "instagram.com" in message.text:
        await download_instagram_video(message)
    else:
        await message.answer("📩 Iltimos, Instagram video havolasini yuboring.")

# Video yuklab olish funksiyasi
async def download_instagram_video(message: types.Message):
    try:
        await message.answer("⏳ Yuklab olinmoqda... Iltimos, kuting...")
        loader = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)
        shortcode = message.text.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        video_url = post.video_url
        await message.answer_video(video_url, caption="✅ Yuklab olindi!")
    except Exception as e:
        await message.answer("❌ Xato yuz berdi! Faqat jamoatchilikka ochiq videolarni yuboring.")
        print(e)

# Webhook handler
async def handle(request):
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return web.Response()

# Webhook o‘rnatish va server ishga tushirish
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

def start():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    start()
