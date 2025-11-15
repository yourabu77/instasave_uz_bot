import os
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# Environment variable orqali token olish
API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Oddiy hello handler
@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Salom! Siz yozdingiz: {message.text}")

# Webhook route
async def handle(request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return web.Response()

# Web-server sozlamalari
app = web.Application()
app.router.add_post("/webhook", handle)

if __name__ == "__main__":
    import asyncio
    import logging
    logging.basicConfig(level=logging.INFO)
    
    port = int(os.getenv("PORT", 8000))  # Render-da PORT environment variable avtomatik beriladi
    logging.info(f"Starting server on port {port}")
    web.run_app(app, port=port)
