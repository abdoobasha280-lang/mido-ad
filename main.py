import telebot
import requests
import hashlib
import json
from telebot import types

# --- [ الإعدادات الأساسية ] ---
BOT_TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
ADMIN_ID = 7721807760  # المطور ميدو
bot = telebot.TeleBot(BOT_TOKEN)

# قناتك الوحيدة
REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

# قاعدة بيانات التحكم (Users ستبقى في الذاكرة، يفضل حفظها في ملف لاحقاً)
db = {
    "users": set(),
    "success_count": 0,
    "status": {"orange": True, "etisalat": True, "free": True}
}

# --- [ وظيفة التحقق - الأدمن مستثنى ] ---
def is_subscribed(user_id):
    if str(user_id) == str(ADMIN_ID): 
        return True  # الأدمن بيدخل علطول
    try:
        member = bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- [ القوائم الرئيسية ] ---
def show_main_menu(chat_id):
    db['users'].add(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=1) # أزرار تحت بعض
    
    # تنسيق الخدمات
    o_txt = "اورانج 🟠" if db['status']['orange'] else "اورانج (صيانة 🛠)"
    o_call = "orange_section" if db['status']['orange'] else "off"
    
    e_txt = "اتصالات 🟢" if db['status']['etisalat'] else "اتصالات (صيانة 🛠)"
    e_call = "etisalat_section" if db['status']['etisalat'] else "off"
    
    markup.add(
        types.InlineKeyboardButton(o_txt, callback_data=o_call),
        types.InlineKeyboardButton(e_txt, callback_data=e_call),
        types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="free_services"),
        types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG")
    )
    
    bot.send_message(chat_id, "مرحب بيك ياحب في بوت MIDO❤\nاختر القسم اللي يناسبك:", reply_markup=markup)

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if is_subscribed(uid):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("قناة المطور ميدو 📢", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        )
        bot.send_message(message.chat.id, "🔒 ياحب لازم تشترك في القناة عشان تستخدم البوت:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        markup = types.InlineKeyboardMarkup(row_width=1)
        stats = f"👤 مستخدمين: {len(db['users'])} | ✅ نجاح: {db['success_count']}"
        
        o_t = "أورانج ✅" if db['status']['orange'] else "أورانج ❌"
        e_t = "اتصالات ✅" if db['status']['etisalat'] else "اتصالات ❌"
        
        markup.add(
            types.InlineKeyboardButton(stats, callback_data="none"),
            types.InlineKeyboardButton(f"تبديل {o_t}", callback_data="toggle_orange"),
            types.InlineKeyboardButton(f"تبديل {e_t}", callback_data="toggle_etisalat"),
            types.InlineKeyboardButton("📢 إذاعة (نشر للكل)", callback_data="admin_broadcast")
        )
        bot.send_message(message.chat.id, "🛠 لوحة تحكم المطور MIDO:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ الأمر ده للمطور بس ياحب.")

# --- [ الردود والتفاعلات ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    if not is_subscribed(uid) and call.data != "check_sub":
        bot.answer_callback_query(call.id, "⚠️ اشترك في القناة الأول!", show_alert=True)
        return

    if call.data == "check_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ نورت البوت!")
            bot.delete_message(cid, call.message.message_id)
            show_main_menu(cid)
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش ياحب!", show_alert=True)

    elif call.data == "orange_section":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="run_fawazeer"),
            types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="run_caf"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="home")
        )
        bot.edit_message_text("قسم أورانج 🟠:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "home":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid)

    elif call.data.startswith("toggle_") and str(uid) == str(ADMIN_ID):
        svc = call.data.split("_")[1]
        db['status'][svc] = not db['status'][svc]
        bot.delete_message(cid, call.message.message_id)
        admin_panel(call.message)

print("✅ MIDO BOT IS READY - FIXED 100%")
bot.infinity_polling()
