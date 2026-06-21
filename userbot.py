# ==========================================
# ИСПРАВЛЕНИЕ ДЛЯ PYTHON 3.10+
# ==========================================
import asyncio
import sys

if sys.version_info >= (3, 10):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ==========================================
# ⚙️ КОНФИГУРАЦИЯ
# ==========================================
import os
from flask import Flask
import threading
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameNotOccupied
import re

API_ID = int(os.environ.get("API_ID", 35509519))
API_HASH = os.environ.get("API_HASH", "e4880e5a9e196645600b3ce9d10b0f45")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "+375295620114")

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
    app_web.run(host='0.0.0.0', port=port, debug=False)

threading.Thread(target=run_web, daemon=True).start()

# ==========================================
# БАЗА ОТВЕТОВ
# ==========================================
AUTO_RESPONSES = {
    ("привет", "здравствуйте", "добрый день", "hi", "hello"): 
        "Привет! 👋 @v_s_o3 сейчас занят, я зафиксировал твое сообщение!",
    
    ("как дела", "как жизнь", "как ты"): 
        "У меня всё отлично! 🤖 @v_s_o3 скоро ответит.",
    
    ("срочно", "важно", "горит"): 
        "🚨 Передал уведомление @v_s_o3!",
    
    ("спасибо", "благодарю", "спс"): 
        "Всегда рад помочь! 👍",
    
    ("пока", "до свидания", "удачи"): 
        "Всего хорошего! 👋",
}

# ==========================================
# ИНИЦИАЛИЗАЦИЯ
# ==========================================
app = Client(
    name="my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER
)

# ==========================================
# АВТООТВЕТЧИК
# ==========================================
@app.on_message(filters.private & filters.incoming & filters.text)
async def auto_responder(client, message):
    if message.from_user.id == client.me.id:
        return
    
    text_lower = message.text.lower()
    print(f"📩 Сообщение от {message.from_user.first_name}: {message.text[:50]}...")
    
    for keywords, reply_text in AUTO_RESPONSES.items():
        if any(keyword in text_lower for keyword in keywords):
            try:
                await asyncio.sleep(1)
                await message.reply(reply_text)
                print(f"✅ Отправлен ответ")
                break
            except FloodWait as e:
                print(f"⏳ Флуд: ждем {e.value} сек")
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"❌ Ошибка: {e}")

# ==========================================
# РАССЫЛКА
# ==========================================
@app.on_message(filters.text)
async def broadcast_command(client, message):
    if not message.text.startswith("/рассылка"):
        return
    
    try:
        owner = await client.get_users("v_s_o3")
        if message.from_user.id != owner.id:
            return
    except:
        return
    
    match = re.search(r'/рассылка\s+"([^"]+)"\s+(.*)', message.text)
    if not match:
        await message.reply("❌ Формат: /рассылка \"Текст\" @user1 @user2")
        return
    
    text_to_send = match.group(1)
    usernames_raw = match.group(2).split()
    usernames = [u.replace("@", "").strip() for u in usernames_raw if u.strip()]
    
    if not usernames:
        await message.reply("❌ Укажите получателей!")
        return
    
    status = await message.reply(f"⏳ Рассылка для {len(usernames)} пользователей...")
    success = 0
    failed = 0
    failed_list = []
    
    for username in usernames:
        try:
            await client.send_message(username, text_to_send)
            success += 1
            await asyncio.sleep(1.5)
        except Exception as e:
            failed += 1
            failed_list.append(f"@{username}")
    
    report = f"✅ Рассылка завершена!\n\n✅ Успешно: {success}\n❌ Ошибок: {failed}"
    if failed_list:
        report += f"\n\n❌ Не удалось: {', '.join(failed_list)}"
    await status.edit(report)

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 ЗАПУСК ЮЗЕРБОТА НА RENDER.COM")
    print("="*60)
    print(f"\n📊 Всего категорий автоответов: {len(AUTO_RESPONSES)}")
    print("\n📌 КОМАНДА ДЛЯ РАССЫЛКИ (только @v_s_o3):")
    print('  /рассылка "Текст сообщения" @user1 @user2')
    print("\n" + "="*60 + "\n")
    
    try:
        app.run()
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
