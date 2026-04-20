import telebot
import requests
import json
import sqlite3
import hashlib
import time
import base64
import xml.etree.ElementTree as ET
from telebot import types

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U' 
CHANNEL_ID = '@midooojiokjj'  # يوزر قناة الاشتراك الإجباري
ADMIN_ID = 7721807760        # آيدي الأدمن الأساسي
DEV_USER = '@AMI_EG'        # يوزر المطور
bot = telebot.TeleBot(API_TOKEN)

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('mido_ai.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('mido_ai.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

init_db()

# --- [ الدوال المساعدة ] ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

def get_bot_status():
    conn = sqlite3.connect('mido_ai.db')
    c = conn.cursor()
    c.execute('SELECT status FROM settings')
    res = c.fetchone()
    conn.close()
    return res[0] if res else 1

# --- [ الكيبوردات (الأزرار الشفافة) ] ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("قسم أورانج 🟠", callback_data="orange_dept"),
        types.InlineKeyboardButton("قسم اتصالات 🟢", callback_data="etisalat_dept"),
        types.InlineKeyboardButton("الخدمات المجانية ⚙️", callback_data="free_services"),
        types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

def orange_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("حل الفوازير (250MB) 🧩", callback_data="orange_fawazir"),
        types.InlineKeyboardButton("هدية رمضان (500MB) 🎁", callback_data="orange_500mb"),
        types.InlineKeyboardButton("معرفة الرصيد 💰", callback_data="orange_balance"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def admin_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast"),
        types.InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_main")
    )
    return markup

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    
    if not check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك هنا أولاً 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        markup.add(types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub"))
        bot.send_message(message.chat.id, "⚠️ عذراً، يجب الاشتراك في القناة لاستخدام البوت.", reply_markup=markup)
        return

    welcome_text = "مرحباً بك في بوت MIDO  🚀\nاختر القسم الذي تريده من الأسفل:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup())

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠 لوحة تحكم الأدمن:", reply_markup=admin_markup())

# --- [ معالجة ضغطات الأزرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "check_sub":
        if check_sub(call.from_user.id):
            bot.edit_message_text("✅ تم التحقق! أهلاً بك.", call.message.chat.id, call.message.message_id, reply_markup=main_markup())
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

    elif call.data == "orange_dept":
        bot.edit_message_text("🟠 قسم خدمات أورانج:", call.message.chat.id, call.message.message_id, reply_markup=orange_markup())

    elif call.data == "orange_fawazir":
        msg = bot.send_message(call.message.chat.id, "أرسل بياناتك بصيغة (الرقم:الباسورد) لحل الفوازير:")
        bot.register_next_step_handler(msg, process_orange_fawazir)

    elif call.data == "orange_500mb":
        msg = bot.send_message(call.message.chat.id, "أرسل بياناتك بصيغة (الرقم:الباسورد) للحصول على 500MB:")
        bot.register_next_step_handler(msg, process_orange_500)

    elif call.data == "orange_balance":
        msg = bot.send_message(call.message.chat.id, "أرسل رقم أورانج لمعرفة الرصيد:")
        bot.register_next_step_handler(msg, process_orange_balance)

    elif call.data == "etisalat_dept":
        msg = bot.send_message(call.message.chat.id, "أرسل بيانات اتصالات بصيغة (الإيميل:الباسورد):")
        bot.register_next_step_handler(msg, process_etisalat)

    elif call.data == "free_services":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="prayer_times"))
        markup.add(types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="gen_image"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text("⚙️ قسم الخدمات المجانية:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_main":
        bot.edit_message_text("اختر القسم الذي تريده من الأسفل:", call.message.chat.id, call.message.message_id, reply_markup=main_markup())

    # --- [ أوامر الأدمن ] ---
    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        # تغيير حالة البوت (كود التغيير في قاعدة البيانات هنا)
        bot.answer_callback_query(call.id, "تم تحديث الحالة.")

# --- [ تنفيذ العمليات (Logic) ] ---

def process_orange_balance(message):
    num = message.text.strip()
    url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
    data = {"SelectedUserDial":None, "IsForAnotherRecipient":True, "RecipientDial":num, "Dial":num}
    try:
        res = requests.post(url, headers={"lang": "en"}, json=data).json()
        balance = res.get('CreditBalance', 'غير معروف')
        bot.reply_to(message, f"💰 الرصيد الحالي للرقم هو: {balance}")
    except:
        bot.reply_to(message, "❌ فشل في جلب الرصيد.")

def process_orange_500(message):
    if ":" not in message.text:
        bot.reply_to(message, "❌ التنسيق خاطئ.")
        return
    num, pwd = message.text.split(":")
    # هنا تضع كود الـ Redeem الخاص بالـ 500MB الذي أرفقته في طلبك
    bot.reply_to(message, "⏳ جاري محاولة إرسال الـ 500 ميجا...")
    # (سيتم تنفيذ طلب الـ POST هنا بناءً على كودك)

def process_etisalat(message):
    if ":" not in message.text: return
    email, pwd = message.text.split(":")
    bot.reply_to(message, "⏳ جاري محاولة جلب هدية اتصالات...")
    # تنفيذ كود اتصالات XML هنا

def process_orange_fawazir(message):
    # تنفيذ كود حل الفوازير هنا
    bot.reply_to(message, "⏳ جاري حل فوازير أورانج...")

# --- [ تشغيل البوت ] ---
print("✅ Mido AI Bot is Running...")
bot.infinity_polling()
