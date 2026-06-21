import os
import asyncio
import re
from flask import Flask
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid

# ==========================================
# ИНИЦИАЛИЗАЦИЯ
# ==========================================
API_ID = int(os.environ.get("API_ID", 35509519))
API_HASH = os.environ.get("API_HASH", "e4880e5a9e196645600b3ce9d10b0f45")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+375295620114")
SESSION_STRING = os.environ.get("SESSION_STRING", None)

# Веб-сервер для Render
app_web = Flask(__name__)

@app_web.route('/')
@app_web.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port, debug=False)

import threading
threading.Thread(target=run_web, daemon=True).start()

# Клиент Pyrogram
if SESSION_STRING:
    app = Client("my_account", api_id=API_ID, api_hash=API_HASH, 
                 phone_number=PHONE_NUMBER, session_string=SESSION_STRING)
else:
    app = Client("my_account", api_id=API_ID, api_hash=API_HASH, 
                 phone_number=PHONE_NUMBER)

# ==========================================
# АВТООТВЕТЫ
# ==========================================
RESPONSES = {
    ("привет", "здравствуйте", "hi", "hello", "пр", "прив"): 
        "Привет! 👋 @v_s_o3 скоро ответит!",
    ("как дела", "как жизнь", "как ты"): 
        "У меня всё отлично! 🤖 @v_s_o3 ответит позже.",
    ("срочно", "важно", "горит"): 
        "🚨 Передал @v_s_o3!",
    ("спасибо", "благодарю", "спс"): 
        "Всегда рад помочь! 👍",
}

# ==========================================
# ОБРАБОТЧИК
# ==========================================
@app.on_message(filters.private & filters.text)
async def handle(client, message):
    if message.from_user.id == client.me.id:
        return
    
    text = message.text.lower()
    print(f"📩 {message.from_user.first_name}: {text[:30]}")
    
    # Рассылка (только для @v_s_o3)
    if message.text.startswith("/рассылка"):
        try:
            owner = await client.get_users("v_s_o3")
            if message.from_user.id != owner.id:
                await message.reply("❌ Только для @v_s_o3!")
                return
        except:
            await message.reply("❌ Не найден @v_s_o3")
            return
        
        match = re.search(r'/рассылка\s+"([^"]+)"\s+(.*)', message.text)
        if not match:
            await message.reply('❌ Формат: /рассылка "Текст" @user1 @user2')
            return
        
        msg = match.group(1)
        users = [u.replace("@", "").strip() for u in match.group(2).split() if u.strip()]
        
        if not users:
            await message.reply("❌ Укажите получателей!")
            return
        
        status = await message.reply(f"⏳ Рассылка {len(users)} пользователям...")
        ok, fail = 0, []
        
        for user in users:
            try:
                await client.send_message(user, msg)
                ok += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                fail.append(f"@{user}")
                print(f"❌ Ошибка @{user}: {e}")
        
        report = f"✅ Готово!\n✅ Успешно: {ok}\n❌ Ошибок: {len(fail)}"
        if fail:
            report += f"\n❌ Не удалось: {', '.join(fail[:5])}"
        await status.edit(report)
        return
    
    # Автоответы
    for words, reply in RESPONSES.items():
        if any(w in text for w in words):
            await message.reply(reply)
            break

# ==========================================
# KEEP-ALIVE
# ==========================================
async def keep_alive():
    while True:
        await asyncio.sleep(300)
        try:
            await app.send_message("me", "/ping")
            print("💓 Жив")
        except:
            pass

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    print("🤖 Бот запускается...")
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(keep_alive())
        app.run()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
