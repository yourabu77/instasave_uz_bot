# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # Render-da Environment variable sifatida BOT_TOKEN o'rnatilsin
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Oddiy /start buyrug‘i handleri
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Salom! Bot ishlayapti ✅")

# Oddiy matn handleri
@dp.message()
async def echo(message: Message):
    await message.answer(f"Siz yozdingiz: {message.text}")

# Aiohttp web serverni sozlash
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.add_routes([web.post(WEBHOOK_PATH, SimpleRequestHandler(dispatcher=dp))])
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
