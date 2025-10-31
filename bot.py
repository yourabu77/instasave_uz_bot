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

# --- Start komandasi ---
@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if text == "/start":
        await message.answer(
            "👋 <b>Salom!</b>\n\n"
            "Bu bot sizga Instagram’dan video yoki rasm yuklab beradi.\n"
            "Faqat havolani yuboring:\n\n"
            "🔗 Masalan: https://www.instagram.com/reel/xxxxx/",
            parse_mode="HTML"
        )
        return

    if "instagram.com" in text:
        await message.answer("⏳ Yuklanmoqda... biroz kuting")

        try:
            loader = instaloader.Instaloader(dirname_pattern="downloads", save_metadata=False)
            post = instaloader.Post.from_shortcode(loader.context, text.split("/")[-2])
            file_path = f"downloads/{post.shortcode}.mp4"

            loader.download_post(post, target="downloads")

            video_file = None
            for file in os.listdir("downloads"):
                if file.endswith(".mp4"):
                    video_file = f"downloads/{file}"
                    break

            if video_file:
                await message.answer_video(video=open(video_file, "rb"))
                await message.answer("✅ Video yuborildi!")
            else:
                await message.answer("⚠️ Faqat video postlarni yuklab bo‘ladi.")

        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")

    else:
        await message.answer("🔗 Iltimos, Instagram havolasini yuboring.")


# --- Webhook funksiyalar ---
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")


async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 Bot to‘xtatildi")


async def handle(request):
    update = await request.json()
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return web.Response()


# --- Asosiy ishga tushirish ---
def start():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    start()
