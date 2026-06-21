import os
import sys
import asyncio
import threading
import re
import base64
from flask import Flask
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameNotOccupied

# ==========================================
# ФИКС EVENT LOOP
# ==========================================
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# ==========================================
# КОНФИГ
# ==========================================
API_ID = int(os.environ.get("API_ID", 35509519))
API_HASH = os.environ.get("API_HASH", "e4880e5a9e196645600b3ce9d10b0f45")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+375295620114")
SESSION_STRING = os.environ.get("SESSION_STRING", None)  # ВАЖНО!

# ==========================================
# ВЕБ-СЕРВЕР ДЛЯ RENDER
# ==========================================
app_web = Flask(__name__)

@app_web.route('/')
@app_web.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

threading.Thread(target=run_web, daemon=True).start()

# ==========================================
# СОЗДАНИЕ СЕССИИ
# ==========================================
if SESSION_STRING:
    # Используем сохраненную сессию
    app = Client(
        name="my_account",
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER,
        session_string=SESSION_STRING
    )
    print("✅ Использую сохраненную сессию")
else:
    # Создаем новую сессию (при первом запуске)
    app = Client(
        name="my_account",
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER
    )
    print("🆕 Создаю новую сессию")

# ==========================================
# АВТООТВЕТЫ
# ==========================================
AUTO_RESPONSES = {
    ("привет", "здравствуйте", "добрый день", "hi", "hello", "пр", "прив", "здарова", "салют"): 
        "Привет! 👋 @v_s_o3 скоро ответит!",
    
    ("как дела", "как жизнь", "как ты", "чё как", "как сам"): 
        "У меня всё отлично! 🤖 @v_s_o3 ответит позже.",
    
    ("срочно", "важно", "горит", "немедленно", "asap"): 
        "🚨 Передал @v_s_o3!",
    
    ("спасибо", "благодарю", "спс", "thanks", "thx"): 
        "Всегда рад помочь! 👍",
    
    ("пока", "до свидания", "удачи", "goodbye", "bye"): 
        "Всего хорошего! 👋",
    
    ("кто ты", "что ты", "бот", "ты бот"): 
        "Я бот-ассистент @v_s_o3 🤖",
    
    ("круто", "класс", "супер", "топ", "ого"): 
        "Ага, согласен! 😎 @v_s_o3 тоже оценит!",
    
    ("ок", "окей", "хорошо", "понял", "ясно"): 
        "Ок! 🔥 Я передам @v_s_o3!",
    
    ("братан", "брат", "бро", "друг", "чувак", "чел"): 
        "Йо, бро! 🤙 @v_s_o3 скоро будет!",
}

# ==========================================
# ОБРАБОТЧИК СООБЩЕНИЙ
# ==========================================
@app.on_message(filters.text & filters.private)
async def handle_messages(client, message):
    if message.from_user.id == client.me.id:
        return
    
    text = message.text.lower()
    print(f"📩 {message.from_user.first_name}: {text[:50]}")
    
    # === КОМАНДА РАССЫЛКИ (только @v_s_o3) ===
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
        
        msg_text = match.group(1)
        users_raw = match.group(2).split()
        users = [u.replace("@", "").strip() for u in users_raw if u.strip()]
        
        if not users:
            await message.reply("❌ Укажите получателей!")
            return
        
        status = await message.reply(f"⏳ Рассылка {len(users)} пользователям...")
        success = 0
        failed = []
        
        for user in users:
            try:
                await client.send_message(user, msg_text)
                success += 1
                await asyncio.sleep(1)
            except Exception as e:
                failed.append(f"@{user}")
                print(f"❌ Ошибка @{user}: {e}")
        
        report = f"✅ Готово!\n✅ Успешно: {success}\n❌ Ошибок: {len(failed)}"
        if failed:
            report += f"\n❌ Не удалось: {', '.join(failed[:5])}"
        await status.edit(report)
        return
    
    # === АВТООТВЕТЫ ===
    for keywords, reply in AUTO_RESPONSES.items():
        if any(k in text for k in keywords):
            try:
                await message.reply(reply)
                print(f"✅ Ответ: {reply[:30]}...")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            break

# ==========================================
# KEEP ALIVE
# ==========================================
async def keep_alive():
    while True:
        try:
            await asyncio.sleep(300)
            await app.send_message("me", "/ping")
            print("💓 Бот жив!")
        except:
            pass

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 ЮЗЕРБОТ НА RENDER")
    print("="*60)
    print("📌 Команда: /рассылка \"Текст\" @user1 @user2")
    print("📌 Keep-alive: каждые 5 минут")
    print("="*60 + "\n")
    
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(keep_alive())
        app.run()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
