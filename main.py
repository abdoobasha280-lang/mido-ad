import telebot
import requests
import json
import sqlite3
import time
import hashlib
import base64
import xml.etree.ElementTree as ET
from telebot import types

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U'
CHANNEL_ID = '@midooojiokjj'  # يوزر القناة
ADMIN_ID = 7721807760       # آيدي الأدمن (أنت)
DEV_USER = '@AMI_EG'        # يوزر المطور
BOT_NAME = "MIDO AI"

bot = telebot.TeleBot(API_TOKEN)

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('mido_users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (status INTEGER)')
    c.execute('SELECT status FROM settings')
    if not c.fetchone(): c.execute('INSERT INTO settings VALUES (1)')
    conn.commit(); conn.close()

def add_user(user_id):
    conn = sqlite3.connect('mido_users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit(); conn.close()

init_db()

# --- [ التحقق من الاشتراك ] ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_status():
    conn = sqlite3.connect('mido_users.db'); c = conn.cursor()
    c.execute('SELECT status FROM settings'); res = c.fetchone(); conn.close()
    return res[0] if res else 1

# --- [ الأزرار العمودية المنظمة ] ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("أورانج 🟠", callback_data="orange"),
        types.InlineKeyboardButton("اتصالات 🟢", callback_data="etisalat"),
        types.InlineKeyboardButton("الخدمات المجانية ⚙️", callback_data="free"),
        types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"أهلاً بك يا أدمن في لوحة تحكم {BOT_NAME}:", 
                         reply_markup=admin_panel_markup())
    
    if get_status() == 0 and message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⚠️ البوت في صيانة حالياً.")

    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"مرحباً بك في {BOT_NAME} 🤖\nاختر الخدمة التي تريدها:", 
                         reply_markup=main_menu())
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("اضغط للاشتراك 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"),
                   types.InlineKeyboardButton("تحقق ✅", callback_data="verify"))
        bot.send_message(message.chat.id, "يجب عليك الاشتراك في القناة أولاً!", reply_markup=markup)

# --- [ معالجة الـ Callbacks ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = call.from_user.id
    mid = call.message.message_id
    cid = call.message.chat.id

    if call.data == "verify":
        if check_sub(uid): bot.edit_message_text("تم التحقق! اختر:", cid, mid, reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "لم تشترك بعد! ❌", show_alert=True)

    elif call.data == "orange":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("حل فوازير (250MB)", callback_data="run_fawazeer"),
                   types.InlineKeyboardButton("هدية (500MB)", callback_data="run_500mb"),
                   types.InlineKeyboardButton("معرفة الرصيد", callback_data="run_bal"),
                   types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("🟠 قسم أورانج:", cid, mid, reply_markup=markup)

    elif call.data == "free":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("🕋 مواقيت الصلاة", callback_data="run_prayer"),
                   types.InlineKeyboardButton("🖼 إنشاء صورة AI", callback_data="run_img"),
                   types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("⚙️ الخدمات المجانية:", cid, mid, reply_markup=markup)

    elif call.data == "home":
        bot.edit_message_text("اختر الخدمة:", cid, mid, reply_markup=main_menu())

    # --- [ تنفيذ الطلبات ] ---
    elif call.data == "run_bal":
        msg = bot.send_message(cid, "أرسل الرقم لمعرفة الرصيد:")
        bot.register_next_step_handler(msg, orange_balance_logic)

    elif call.data == "run_img":
        msg = bot.send_message(cid, "أرسل وصف الصورة (بالإنجليزي):")
        bot.register_next_step_handler(msg, image_logic)

    elif call.data == "run_prayer":
        msg = bot.send_message(cid, "أرسل اسم المحافظة (مثال: Cairo):")
        bot.register_next_step_handler(msg, prayer_logic)

# --- [ Logic Functions ] ---

def orange_balance_logic(message):
    num = message.text.strip()
    loading = bot.send_message(message.chat.id, "⏳ جاري فحص الرصيد...")
    try:
        url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
        res = requests.post(url, json={"SelectedUserDial":None,"IsForAnotherRecipient":True,"RecipientDial":num,"Dial":num}, headers={"lang": "en"}).json()
        bal = res['CreditBalance']
        bot.edit_message_text(f"💰 الرقم: {num}\n💳 الرصيد: {bal} جنيه.", message.chat.id, loading.message_id)
    except:
        bot.edit_message_text("❌ حدث خطأ، تأكد من الرقم.", message.chat.id, loading.message_id)

def image_logic(message):
    prompt = message.text.replace(" ", "%20")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    img_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed=42"
    try:
        bot.send_photo(message.chat.id, img_url, caption=f"✅ تم إنشاء صورتك بواسطة {BOT_NAME}")
    except:
        bot.reply_to(message, "❌ فشل إنشاء الصورة.")

def prayer_logic(message):
    city = message.text.strip()
    try:
        res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5").json()
        t = res['data']['timings']
        bot.reply_to(message, f"🕋 مواقيت الصلاة لـ {city}:\nالفجر: {t['Fajr']}\nالظهر: {t['Dhuhr']}\nالعصر: {t['Asr']}\nالمغرب: {t['Maghrib']}\nالعشاء: {t['Isha']}")
    except:
        bot.reply_to(message, "❌ اسم المدينة غير صحيح.")

# --- [ لوحة التحكم للأدمن ] ---
def admin_panel_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    status = "🔴 متوقف" if get_status() == 0 else "🟢 شغال"
    markup.add(types.InlineKeyboardButton(f"حالة البوت: {status}", callback_data="toggle_status"),
               types.InlineKeyboardButton("📣 إذاعة جماعية", callback_data="broadcast"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data in ["toggle_status", "broadcast"] and call.from_user.id == ADMIN_ID)
def admin_logic(call):
    if call.data == "toggle_status":
        conn = sqlite3.connect('mido_users.db'); c = conn.cursor()
        new_s = 0 if get_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,)); conn.commit(); conn.close()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_panel_markup())
    
    elif call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "أرسل الرسالة الآن:")
        bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    conn = sqlite3.connect('mido_users.db'); c = conn.cursor(); c.execute('SELECT user_id FROM users'); users = c.fetchall(); conn.close()
    for u in users:
        try: bot.send_message(u[0], message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ تمت الإذاعة بنجاح.")

bot.infinity_polling()
