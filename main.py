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
CHANNEL_ID = '@midooojiokjj'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'
BOT_NAME = "MIDO"

bot = telebot.TeleBot(API_TOKEN)

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('mido.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (status INTEGER)')
    c.execute('SELECT status FROM settings')
    if not c.fetchone(): c.execute('INSERT INTO settings VALUES (1)')
    conn.commit(); conn.close()

def add_user(user_id):
    conn = sqlite3.connect('mido.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit(); conn.close()

init_db()

# --- [ التحقق ] ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_bot_status():
    conn = sqlite3.connect('mido.db'); c = conn.cursor()
    c.execute('SELECT status FROM settings'); res = c.fetchone(); conn.close()
    return res[0] if res else 1

# --- [ الأزرار العمودية ] ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("قسم أورانج 🟠", callback_data="open_orange"),
        types.InlineKeyboardButton("قسم اتصالات 🟢", callback_data="open_etisalat"),
        types.InlineKeyboardButton("الخدمات المجانية ⚙️", callback_data="open_free"),
        types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

# --- [ أوامر البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"أهلاً يا أدمن في لوحة تحكم {BOT_NAME}", reply_markup=admin_panel())
        
    if get_bot_status() == 0 and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⚠️ البوت في صيانة.")
        return

    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"مرحباً بك في بوت {BOT_NAME} 🤖\nاختر من القائمة أدناه:", reply_markup=main_markup())
    else:
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"),
              types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="verify_sub"))
        bot.send_message(message.chat.id, "يجب الاشتراك بالقناة أولاً!", reply_markup=m)

# --- [ معالج الضغطات - Callback Handler ] ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    uid = call.from_user.id

    if call.data == "verify_sub":
        if check_sub(uid): bot.edit_message_text("تم التحقق! اختر القسم:", cid, mid, reply_markup=main_markup())
        else: bot.answer_callback_query(call.id, "اشترك أولاً! ❌", show_alert=True)

    elif call.data == "open_orange":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("حل الفوازير (250MB)", callback_data="fawazeer_go"),
              types.InlineKeyboardButton("هدية (500MB)", callback_data="gift500_go"),
              types.InlineKeyboardButton("معرفة الرصيد", callback_data="balance_go"),
              types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("🟠 خدمات أورانج:", cid, mid, reply_markup=m)

    elif call.data == "open_free":
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("🖼 إنشاء صورة AI", callback_data="gen_img_go"),
              types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_go"),
              types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("⚙️ الخدمات المجانية:", cid, mid, reply_markup=m)

    elif call.data == "back_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, mid, reply_markup=main_markup())

    # --- [ أوامر الإدخال ] ---
    elif call.data == "balance_go":
        msg = bot.send_message(cid, "أرسل رقم أورانج:")
        bot.register_next_step_handler(msg, orange_bal)

    elif call.data == "prayer_go":
        msg = bot.send_message(cid, "أرسل اسم المحافظة بالإنجليزية:")
        bot.register_next_step_handler(msg, prayer_times)

    elif call.data == "gen_img_go":
        msg = bot.send_message(cid, "أرسل وصف الصورة (English Only):")
        bot.register_next_step_handler(msg, create_image)

    # --- [ لوحة التحكم ] ---
    elif call.data == "toggle_bot" and uid == ADMIN_ID:
        conn = sqlite3.connect('mido.db'); c = conn.cursor()
        new = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new,)); conn.commit(); conn.close()
        bot.edit_message_reply_markup(cid, mid, reply_markup=admin_panel())

# --- [ الدوال الفعلية ] ---

def orange_bal(message):
    num = message.text.strip()
    try:
        r = requests.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", 
                          json={"SelectedUserDial":None,"IsForAnotherRecipient":True,"RecipientDial":num,"Dial":num}, 
                          headers={"lang": "en"}).json()
        bot.reply_to(message, f"💰 الرصيد للرقم {num} هو: {r['CreditBalance']} ج.م")
    except: bot.reply_to(message, "❌ فشل، تأكد من الرقم.")

def prayer_times(message):
    city = message.text.strip()
    try:
        r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5").json()
        t = r['data']['timings']
        bot.reply_to(message, f"🕌 مواقيت {city}:\nالفجر: {t['Fajr']}\nالظهر: {t['Dhuhr']}\nالمغرب: {t['Maghrib']}\nالعشاء: {t['Isha']}")
    except: bot.reply_to(message, "❌ خطأ في الاسم.")

def create_image(message):
    p = message.text.replace(" ", "%20")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    url = f"https://pollinations.ai/p/{p}?width=1024&height=1024&nologo=true"
    bot.send_photo(message.chat.id, url, caption=f"✅ تم بواسطة {BOT_NAME}")

# --- [ لوحة الأدمن ] ---
def admin_panel():
    m = types.InlineKeyboardMarkup(row_width=1)
    s = "🟢 شغال" if get_bot_status() == 1 else "🔴 متوقف"
    m.add(types.InlineKeyboardButton(f"الحالة: {s}", callback_data="toggle_bot"),
          types.InlineKeyboardButton("📣 إذاعة جماعية", callback_data="send_all"))
    return m

print(f"✅ {BOT_NAME} Is Running...")
bot.infinity_polling()
