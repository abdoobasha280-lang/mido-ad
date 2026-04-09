import telebot
import requests
import json
import sqlite3
import time
import hashlib
import random
import urllib.parse
from telebot import types
from bs4 import BeautifulSoup

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'
bot = telebot.TeleBot(API_TOKEN)

# إحصائيات
stats = {"success": 0, "failed": 0}
user_step_data = {}

# --- [ إعداد قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('mido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('mido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    try:
        conn = sqlite3.connect('mido_ultra.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT status FROM settings')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 1
    except: return 1

init_db()

# --- [ موديول مواقيت الصلاة ] ---
def get_prayer_times():
    try:
        url = "https://www.masrawy.com/islameyat/prayer-times"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        prayer_section = soup.find('div', {'class': 'allTimes'})
        if not prayer_section: return "❌ المصدر غير متاح حالياً."
        
        times_divs = prayer_section.find_all('div', {'class': 'time'})
        prayers = ['الفجر', 'الشروق', 'الظهر', 'العصر', 'المغرب', 'العشاء']
        extracted = [t.get_text(strip=True) for t in times_divs if ":" in t.get_text()]
        
        result = "🕌 **مواقيت الصلاة اليوم:**\n"
        for p, t in zip(prayers, extracted):
            result += f"🔹 {p}: `{t}`\n"
        return result
    except: return "❌ فشل جلب المواقيت."

# --- [ الكيبوردات (تحت بعض) ] ---

def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1) # مرصوصة تحت بعض
    markup.add(
        types.InlineKeyboardButton("🍊 أقسام أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_services"),
        types.InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

def orange_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="gift_500"),
        types.InlineKeyboardButton("🧩 حل الفوازير", callback_data="solve_fawazeer"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_home")
    )
    return markup

def extra_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎨 رسم صورة (Nano Banana)", callback_data="draw_image"),
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_home")
    )
    return markup

def admin_markup():
    conn = sqlite3.connect('mido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="admin_count"),
        types.InlineKeyboardButton(f"📊 نجاح: {stats['success']} | فشل: {stats['failed']}", callback_data="admin_stats"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast")
    )
    return markup

# --- [ الأوامر الرئيسية ] ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_user(message.from_user.id)
    welcome = "✨ **أهلاً بك في بوت Mido AI المطوّر**\n\nالبوت الآن يدعم خدمات أورانج، مواقيت الصلاة، وتوليد الصور بتقنية **Nano Banana**."
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu_markup(), parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ **لوحة التحكم السرية**", reply_markup=admin_markup(), parse_mode="Markdown")

# --- [ معالجة Callback ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    
    if call.data == "main_home":
        bot.edit_message_text("✨ القائمة الرئيسية:", chat_id, call.message.message_id, reply_markup=main_menu_markup())
    
    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج:", chat_id, call.message.message_id, reply_markup=orange_menu_markup())
        
    elif call.data == "extra_services":
        bot.edit_message_text("🛠️ الخدمات الإضافية:", chat_id, call.message.message_id, reply_markup=extra_menu_markup())

    elif call.data == "prayer_times":
        bot.answer_callback_query(call.id, "🕌 جاري جلب المواقيت...")
        bot.edit_message_text(get_prayer_times(), chat_id, call.message.message_id, reply_markup=extra_menu_markup(), parse_mode="Markdown")

    elif call.data == "draw_image":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "🎨 **أرسل وصف الصورة التي تريد رسمها الآن:**\n(يفضل بالإنجليزية لنتائج أفضل)")
        bot.register_next_step_handler(msg, process_draw)

    elif call.data == "gift_500":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "📱 أدخل رقم أورانج:")
        bot.register_next_step_handler(msg, process_number, "gift")

    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        # تبديل حالة البوت
        pass

# --- [ منطق Nano Banana ] ---

def process_draw(message):
    prompt = message.text
    if not prompt: return
    
    wait_msg = bot.reply_to(message, "🎨 **جاري استخدام Nano Banana لرسم خيالك...**")
    try:
        seed = random.randint(1, 999999)
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&model=extra-realism&nologo=true"
        
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.send_photo(
            message.chat.id, 
            image_url, 
            caption=f"✨ **تم التوليد بواسطة Nano Banana**\n📝 الوصف: `{prompt}`",
            reply_markup=main_menu_markup()
        )
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except:
        bot.edit_message_text("❌ حدث خطأ، جرب لاحقاً.", message.chat.id, wait_msg.message_id)

# --- [ باقي الوظائف ] ---
def process_number(message, mode):
    # نفس منطق أورانج السابق (رقم ثم باسوورد)
    pass

if __name__ == "__main__":
    print("Mido AI is Online with Nano Banana...")
    bot.infinity_polling()
