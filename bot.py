import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import instaloader

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# /start
@dp.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Salom! Bu bot orqali siz Instagram videolarini yuklab olishingiz mumkin.\n"
        "📌 Faqat video postlarni yuboring (havola bilan)."
    )

# Har qanday xabar
@dp.message()
async def handle_message(message: types.Message):
    if "instagram.com" in message.text:
        try:
            await message.answer("⏳ Yuklab olinmoqda...")
            loader = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)
            shortcode = message.text.rstrip("/").split("/")[-1]
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            video_url = post.video_url
            await message.answer_video(video_url, caption="✅ Yuklab olindi!")
        except Exception as e:
            await message.answer("❌ Xato! Faqat jamoatchilikka ochiq videolarni yuboring.")
            print(e)
    else:
        await message.answer("📩 Iltimos, Instagram video havolasini yuboring.")

# Webhook handler
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

def start():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    start()
