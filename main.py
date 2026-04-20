import telebot
import requests
import hashlib
from telebot import types

# --- [ الإعدادات الأساسية ] ---
BOT_TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
ADMIN_ID = 7721807760  # المطور ميدو
bot = telebot.TeleBot(BOT_TOKEN)

# قناتك الرسمية فقط
REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

# قاعدة بيانات التحكم
db = {
    "users": set(),
    "success_count": 0,
    "status": {"orange": True, "etisalat": True, "free": True}
}

user_data = {}

# --- [ دالة التحقق من الاشتراك - الأدمن مستثنى ] ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- [ القائمة الرئيسية ] ---
def show_main_menu(chat_id):
    db['users'].add(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=1) # أزرار تحت بعض
    
    # خدمات أورانج
    o_txt = "اورانج 🟠" if db['status']['orange'] else "اورانج (صيانة 🛠)"
    o_call = "orange_menu" if db['status']['orange'] else "service_off"
    
    # خدمات اتصالات
    e_txt = "اتصالات 🟢" if db['status']['etisalat'] else "اتصالات (صيانة 🛠)"
    e_call = "etisalat_menu" if db['status']['etisalat'] else "service_off"
    
    markup.add(
        types.InlineKeyboardButton(o_txt, callback_data=o_call),
        types.InlineKeyboardButton(e_txt, callback_data=e_call),
        types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="free_menu"),
        types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG")
    )
    
    bot.send_message(chat_id, "مرحب بيك ياحب في بوت MIDO❤\nاختر القسم اللي يناسبك:", reply_markup=markup)

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start_command(message):
    uid = message.from_user.id
    if is_subscribed(uid):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("قناة المطور ميدو 📢", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
        )
        bot.send_message(message.chat.id, "🔒 ياحب لازم تشترك في القناة عشان تستخدم البوت:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        stats = f"👤 مستخدمين: {len(db['users'])} | ✅ نجاح: {db['success_count']}"
        markup.add(
            types.InlineKeyboardButton(stats, callback_data="none"),
            types.InlineKeyboardButton("📢 إذاعة (نشر للكل)", callback_data="admin_broadcast")
        )
        bot.send_message(message.chat.id, "🛠 لوحة تحكم المطور MIDO:", reply_markup=markup)

# --- [ معالجة الأزرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    # التحقق من الاشتراك
    if not is_subscribed(uid) and call.data != "check_subscription":
        bot.answer_callback_query(call.id, "⚠️ اشترك في القناة الأول ياحب!", show_alert=True)
        return

    if call.data == "check_subscription":
        if is_subscribed(uid):
            bot.delete_message(cid, call.message.message_id)
            show_main_menu(cid)
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش ياحب!", show_alert=True)

    elif call.data == "orange_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="start_fawazeer"),
            types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="start_orange500"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_to_home")
        )
        bot.edit_message_text("قسم أورانج 🟠 - اختر الخدمة:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "free_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("رصيد أورانج 💰", callback_data="check_balance"),
            types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="prayer_times"),
            types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="ai_image"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_to_home")
        )
        bot.edit_message_text("الخدمات المجانية ⚙:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "back_to_home":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid)

    elif call.data == "service_off":
        bot.answer_callback_query(call.id, "🛠 الخدمة دي في الصيانة حالياً.", show_alert=True)

# --- [ تشغيل البوت ] ---
print("✅ البوت شغال الآن - نسخة نظيفة تماماً")
bot.infinity_polling()
