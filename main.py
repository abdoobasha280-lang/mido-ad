import telebot
import requests
import json
import sqlite3
import time
from telebot import types

# --- [ الإعدادات ] ---
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U'
CHANNEL_ID = '@midooojiokjj'
ADMIN_ID = 7721807760
BOT_NAME = "MIDO"

bot = telebot.TeleBot(API_TOKEN, threaded=True)

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('mido.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (status INTEGER)')
    c.execute('SELECT status FROM settings')
    if not c.fetchone(): c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    return conn

db_conn = init_db()

# --- [ الدوال الأساسية ] ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_status():
    c = db_conn.cursor()
    c.execute('SELECT status FROM settings')
    res = c.fetchone()
    return res[0] if res else 1

# --- [ أزرار الصاروخ ] ---
def main_markup():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🟠 قسم أورانج", callback_data="nav_orange"),
        types.InlineKeyboardButton("🟢 قسم اتصالات", callback_data="nav_eti"),
        types.InlineKeyboardButton("⚙️ خدمات مجانية", callback_data="nav_free"),
        types.InlineKeyboardButton("👨‍💻 المطور", url="https://t.me/AMI_EG")
    )
    return m

def admin_markup():
    m = types.InlineKeyboardMarkup(row_width=1)
    s = "🟢 شغال" if get_status() == 1 else "🔴 متوقف"
    m.add(
        types.InlineKeyboardButton(f"الحالة: {s}", callback_data="adm_toggle"),
        types.InlineKeyboardButton("📣 إذاعة", callback_data="adm_bc")
    )
    return m

# --- [ استقبال الرسائل ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    # إضافة المستخدم
    c = db_conn.cursor()
    c.execute('INSERT OR IGNORE INTO users VALUES (?)', (uid,))
    db_conn.commit()

    if uid == ADMIN_ID:
        return bot.send_message(message.chat.id, f"🛠 لوحة تحكم {BOT_NAME}:", reply_markup=admin_markup())

    if get_status() == 0:
        return bot.send_message(message.chat.id, "⚠️ البوت في صيانة حالياً.")

    if check_sub(uid):
        bot.send_message(message.chat.id, f"مرحباً بك في بوت {BOT_NAME} 🤖\nالخدمات جاهزة يا وحش:", reply_markup=main_markup())
    else:
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("اشترك هنا أولاً 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"),
              types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify"))
        bot.send_message(message.chat.id, "❌ لازم تشترك عشان الأزرار تشتغل:", reply_markup=m)

# --- [ معالج الأزرار (أهم جزء) ] ---
@bot.callback_query_handler(func=lambda call: True)
def callback_all(call):
    # الرد الفوري عشان الزرار ما يعلقش
    bot.answer_callback_query(call.id)
    
    cid = call.message.chat.id
    mid = call.message.message_id
    uid = call.from_user.id

    if call.data == "verify":
        if check_sub(uid):
            bot.edit_message_text("✅ تم التحقق!", cid, mid, reply_markup=main_markup())
        
    elif call.data == "nav_orange":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("🎁 حل فوازير (250MB)", callback_data="task_fawazeer"),
              types.InlineKeyboardButton("🎁 هدية (500MB)", callback_data="task_500"),
              types.InlineKeyboardButton("💰 رصيد أورانج", callback_data="task_bal"),
              types.InlineKeyboardButton("🔙 رجوع", callback_data="nav_home"))
        bot.edit_message_text("🟠 قسم أورانج:", cid, mid, reply_markup=m)

    elif call.data == "nav_free":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("🖼 إنشاء صورة AI", callback_data="task_img"),
              types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="task_prayer"),
              types.InlineKeyboardButton("🔙 رجوع", callback_data="nav_home"))
        bot.edit_message_text("⚙️ الخدمات المجانية:", cid, mid, reply_markup=m)

    elif call.data == "nav_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, mid, reply_markup=main_markup())

    # --- [ أوامر الأدمن ] ---
    elif call.data == "adm_toggle" and uid == ADMIN_ID:
        c = db_conn.cursor()
        new_s = 0 if get_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,))
        db_conn.commit()
        bot.edit_message_reply_markup(cid, mid, reply_markup=admin_markup())

    # --- [ طلبات الإدخال ] ---
    elif call.data == "task_bal":
        msg = bot.send_message(cid, "ارسل الرقم:")
        bot.register_next_step_handler(msg, orange_bal_action)
    elif call.data == "task_img":
        msg = bot.send_message(cid, "ارسل وصف الصورة بالإنجليزي:")
        bot.register_next_step_handler(msg, image_action)
    elif call.data == "task_prayer":
        msg = bot.send_message(cid, "ارسل اسم المدينة (Cairo):")
        bot.register_next_step_handler(msg, prayer_action)

# --- [ تنفيذ الدوال ] ---
def orange_bal_action(message):
    num = message.text.strip()
    try:
        r = requests.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", 
                          json={"SelectedUserDial":None,"IsForAnotherRecipient":True,"RecipientDial":num,"Dial":num}, 
                          headers={"lang": "en"}).json()
        bot.reply_to(message, f"💰 رصيدك: {r['CreditBalance']} ج.م")
    except: bot.reply_to(message, "❌ فشل، جرب تاني.")

def image_action(message):
    p = message.text.replace(" ", "%20")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    url = f"https://pollinations.ai/p/{p}?width=1024&height=1024&seed=42"
    bot.send_photo(message.chat.id, url, caption=f"✅ تم بواسطة {BOT_NAME}")

def prayer_action(message):
    city = message.text.strip()
    try:
        r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5").json()
        t = r['data']['timings']
        bot.reply_to(message, f"🕌 {city}:\nالفجر: {t['Fajr']}\nالمغرب: {t['Maghrib']}")
    except: bot.reply_to(message, "❌ اسم المدينة غلط.")

# --- [ تشغيل ] ---
if __name__ == '__main__':
    print(f"✅ Bot {BOT_NAME} is Running on Railway/Replit...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
