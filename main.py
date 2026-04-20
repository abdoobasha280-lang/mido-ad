import telebot
import requests
import hashlib
import json
from telebot import types

# --- [ الإعدادات الأساسية ] ---
BOT_TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
ADMIN_ID = 7721807760  # معرف المطور (ميدو)
bot = telebot.TeleBot(BOT_TOKEN)

# قناتك الوحيدة
REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

# قاعدة بيانات مؤقتة للتحكم
db = {
    "users": set(),
    "success_count": 0,
    "status": {"orange": True, "etisalat": True, "free": True}
}

user_data = {}

# --- [ وظيفة التحقق (تخطي الأدمن) ] ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True  # الأدمن يتخطى الاشتراك
    try:
        status = bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- [ القوائم الرئيسية ] ---
def show_main_menu(chat_id):
    db['users'].add(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # تنسيق الأزرار حسب حالة التشغيل
    o_txt = "اورانج 🟠" if db['status']['orange'] else "اورانج (صيانة 🛠)"
    o_call = "orange_section" if db['status']['orange'] else "off"
    e_txt = "اتصالات 🟢" if db['status']['etisalat'] else "اتصالات (صيانة 🛠)"
    e_call = "etisalat_section" if db['status']['etisalat'] else "off"
    
    markup.add(types.InlineKeyboardButton(o_txt, callback_data=o_call),
               types.InlineKeyboardButton(e_txt, callback_data=e_call))
    markup.add(types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="free_services"))
    markup.add(types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG"))
    
    bot.send_message(chat_id, "مرحب بيك ياحب في بوت MIDO❤\nاختر القسم اللي يناسبك:", reply_markup=markup)

# --- [ معالجة الرسائل ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if is_subscribed(uid):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton("قناة الاشتراك 📢", url=CHANNEL_LINK)
        btn_check = types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        markup.add(btn_link)
        markup.add(btn_check)
        bot.send_message(message.chat.id, "🔒 عذراً ياحب، لازم تشترك في القناة عشان تستخدم البوت:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton(f"👥 مستخدمين: {len(db['users'])}", callback_data="none"),
                   types.InlineKeyboardButton(f"✅ نجاح: {db['success_count']}", callback_data="none"))
        
        o_t = "أورانج ✅" if db['status']['orange'] else "أورانج ❌"
        e_t = "اتصالات ✅" if db['status']['etisalat'] else "اتصالات ❌"
        
        markup.add(types.InlineKeyboardButton(o_t, callback_data="toggle_orange"),
                   types.InlineKeyboardButton(e_t, callback_data="toggle_etisalat"))
        markup.add(types.InlineKeyboardButton("📢 إذاعة (نشر)", callback_data="admin_broadcast"))
        bot.send_message(message.chat.id, "🛠 لوحة تحكم المطور:", reply_markup=markup)

# --- [ الردود والتفاعلات ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    if not is_subscribed(uid) and call.data != "check_sub":
        bot.answer_callback_query(call.id, "⚠️ اشترك في القناة أولاً!", show_alert=True)
        return

    if call.data == "check_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ نورت البوت ياحب!")
            bot.delete_message(cid, call.message.message_id)
            show_main_menu(cid)
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش في القناة!", show_alert=True)

    elif call.data == "orange_section":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="go_fawazeer"),
                   types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="go_caf"),
                   types.InlineKeyboardButton("⬅️ رجوع", callback_data="home"))
        bot.edit_message_text("قسم أورانج 🟠:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "free_services":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("رصيد أورانج 💰", callback_data="step_balance"),
                   types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="step_prayer"),
                   types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="step_image"),
                   types.InlineKeyboardButton("⬅️ رجوع", callback_data="home"))
        bot.edit_message_text("الخدمات المجانية ⚙:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "home":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid)

    elif call.data == "off":
        bot.answer_callback_query(call.id, "🛠 الخدمة في الصيانة حالياً.", show_alert=True)

    # تحكم الأدمن
    elif call.data.startswith("toggle_") and uid == ADMIN_ID:
        svc = call.data.split("_")[1]
        db['status'][svc] = not db['status'][svc]
        bot.delete_message(cid, call.message.message_id)
        admin_panel(call.message)

print("✅ MIDO BOT IS ONLINE - NO ERRORS")
bot.infinity_polling()
