from aiogram import Bot, Dispatcher, types
from aiohttp import web
import asyncio
import os
import instaloader

API_TOKEN = "8201685441:AAEOP4pi-AbI0OmJU4O2VB_G-Zuns8GBpTo"

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message()
async def handler(message: types.Message):
    if message.text == "/start":
        await message.answer(
            "👋 Salom! Bu bot orqali siz Instagram'dan videolarni yuklab olishingiz mumkin.\n\n"
            "📌 Faqat video postlarni yuboring (havola bilan):\n\n"
            "Masalan:\n"
            "https://www.instagram.com/reel/xxxxx\n\n"
            "👨‍💻 Dasturchi: @yourabu"
        )
    elif "instagram.com" in message.text:
        try:
            await message.answer("⏳ Yuklab olinmoqda... Iltimos, kuting...")
            loader = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)
            post = instaloader.Post.from_shortcode(loader.context, message.text.split("/")[-2])
            video_url = post.video_url
            await message.answer_video(video_url, caption="✅ Yuklab olindi!")
        except Exception as e:
            await message.answer("❌ Xato yuz berdi! Faqat jamoatchilikka ochiq videolarni yuboring.")
            print(e)
    else:
        await message.answer("📩 Iltimos, Instagram video havolasini yuboring.")


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
