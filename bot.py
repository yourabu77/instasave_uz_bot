import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
import instaloader

API_TOKEN = os.getenv("API_TOKEN")

WEBHOOK_PATH = "/webhook"
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if not HOSTNAME:
    raise RuntimeError("RENDER_EXTERNAL_HOSTNAME topilmadi!")

WEBHOOK_URL = f"https://{HOSTNAME}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


def extract_shortcode(url: str) -> str:
    url = url.split("?")[0]          # ?dan keyingi parametrlardan tozalash
    url = url.rstrip("/")            # oxirgi / ni olib tashlash
    return url.split("/")[-1]        # shortcode


@dp.message()
async def download_instagram_video(message: types.Message):
    text = message.text.strip()

    if text == "/start":
        await message.answer(
            "👋 Salom! Instagram video yuklab beruvchi bot!\n\n"
            "📌 Menga Instagram video havolasini yuboring.\n"
            "Masalan:\nhttps://www.instagram.com/reel/xxxx"
        )
        return

    if "instagram.com" not in text:
        await message.answer("📩 Iltimos, Instagram video havolasini yuboring.")
        return

    try:
        await message.answer("⏳ Yuklab olinmoqda, biroz kuting...")

        loader = instaloader.Instaloader(
            dirname_pattern="downloads",
            save_metadata=False,
            download_comments=False,
            post_metadata_txt_pattern=""
        )

        shortcode = extract_shortcode(text)
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        video_url = post.video_url

        await message.answer_video(video_url, caption="✅ Yuklab olindi!")

    except Exception as e:
        print("Xato:", e)
        await message.answer("❌ Xato! Faqat ochiq videolarni yuboring.")


async def handle(request):
    data = await request.json()
    update = types.Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response()


async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"🚀 Webhook ishga tushdi: {WEBHOOK_URL}")


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
