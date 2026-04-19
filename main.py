import telebot
import requests
import json
import base64
import hashlib
import xml.etree.ElementTree as ET
from telebot import types

# --- [ إعدادات الهوية والتحكم ] ---
BOT_TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
ADMIN_ID = 7721807760  # معرف المطور (أنت)
bot = telebot.TeleBot(BOT_TOKEN)

# القناة الإجبارية
REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

# قاعدة بيانات مؤقتة
db = {
    "users": set(),
    "success_count": 0,
    "status": {
        "orange": True,
        "etisalat": True,
        "free": True
    }
}

user_data = {}

# --- [ وظيفة التحقق من الاشتراك ] ---
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

# --- [ القائمة الرئيسية ] ---
def show_main_menu(chat_id):
    db['users'].add(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # خدمات أورانج
    o_txt = "اورانج 🟠" if db['status']['orange'] else "اورانج (صيانة 🛠)"
    o_call = "orange_section" if db['status']['orange'] else "off"
    
    # خدمات اتصالات
    e_txt = "اتصالات 🟢" if db['status']['etisalat'] else "اتصالات (صيانة 🛠)"
    e_call = "etisalat_section" if db['status']['etisalat'] else "off"
    
    btn_free = types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="free_services")
    btn_dev = types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG")
    
    markup.add(types.InlineKeyboardButton(o_txt, callback_data=o_call),
               types.InlineKeyboardButton(e_txt, callback_data=e_call))
    markup.add(btn_free)
    markup.add(btn_dev)
    
    bot.send_message(chat_id, "مرحب بيك ياحب في بوت MIDO❤\nاختر العرض الي يناسبك:", reply_markup=markup)

# --- [ معالجة البداية والتحقق ] ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_subscribed(user_id):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك في القناة أولاً 📢", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
        bot.send_message(message.chat.id, "🔒 عذراً ياحب، لازم تشترك في قناة البوت عشان تقدر تستخدمه:", reply_markup=markup)

# --- [ معالجة الـ Callbacks ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    # التحقق من الاشتراك قبل أي عملية
    if not is_subscribed(uid) and call.data != "check_sub":
        bot.answer_callback_query(call.id, "⚠️ اشترك في القناة الأول ياحب!", show_alert=True)
        return

    if call.data == "check_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ تمام ياحب، نورت البوت!")
            bot.delete_message(cid, call.message.message_id)
            show_main_menu(cid)
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش، اشترك ودوس تاني.", show_alert=True)

    elif call.data == "orange_section":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="go_fawazeer"),
                   types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="go_caf"),
                   types.InlineKeyboardButton("⬅️ رجوع", callback_data="home"))
        bot.edit_message_text("قسم أورانج 🟠:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "off":
        bot.answer_callback_query(call.id, "🛠 الخدمة في الصيانة حالياً بطلب من المطور.", show_alert=True)

    elif call.data == "home":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid)

    # --- [ أوامر الأدمن ] ---
    elif call.data.startswith("toggle_") and uid == ADMIN_ID:
        service = call.data.split("_")[1]
        db['status'][service] = not db['status'][service]
        bot.delete_message(cid, call.message.message_id)
        # استدعاء لوحة الأدمن مرة تانية (يمكنك إضافة دالة لوحة الأدمن هنا)

# --- [ تشغيل البوت ] ---
print("✅ MIDO BOT IS READY (With Force Subscribe)...")
bot.infinity_polling()
