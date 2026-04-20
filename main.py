import telebot
import requests
import hashlib
import json
from telebot import types

# --- [ الإعدادات الأساسية ] ---
BOT_TOKEN = "7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U"
ADMIN_ID = 7721807760  # المطور ميدو
bot = telebot.TeleBot(BOT_TOKEN)

# قناتك الرسمية (تأكد أن البوت "أدمن" داخلها)
REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

# قاعدة بيانات مؤقتة
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
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # تنسيق الخدمات بناءً على الحالة (تشغيل/إيقاف)
    o_txt = "اورانج 🟠" if db['status']['orange'] else "اورانج (صيانة 🛠)"
    o_call = "orange_menu" if db['status']['orange'] else "service_off"
    
    e_txt = "اتصالات 🟢" if db['status']['etisalat'] else "اتصالات (صيانة 🛠)"
    e_call = "etisalat_menu" if db['status']['etisalat'] else "service_off"
    
    markup.add(
        types.InlineKeyboardButton(o_txt, callback_data=o_call),
        types.InlineKeyboardButton(e_txt, callback_data=e_call),
        types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="free_menu"),
        types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG")
    )
    
    bot.send_message(chat_id, "مرحب بيك ياحب في بوت MIDO❤\nاختر القسم اللي يناسبك:", reply_markup=markup)

# --- [ معالجة البداية ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if is_subscribed(uid):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("قناة المطور ميدو 📢", url=CHANNEL_LINK),
            types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="verify_sub")
        )
        bot.send_message(message.chat.id, "🔒 ياحب لازم تشترك في القناة عشان تقدر تستخدم البوت:", reply_markup=markup)

# --- [ لوحة التحكم للأدمن ] ---
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        stats = f"👤 مستخدمين: {len(db['users'])} | ✅ نجاح: {db['success_count']}"
        markup.add(
            types.InlineKeyboardButton(stats, callback_data="none"),
            types.InlineKeyboardButton("📢 إذاعة (نشر للكل)", callback_data="broadcast")
        )
        bot.send_message(message.chat.id, "🛠 لوحة تحكم المطور ميدو:", reply_markup=markup)

# --- [ معالجة الضغطات ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    if call.data == "verify_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ تم التحقق!")
            bot.delete_message(cid, call.message.message_id)
            show_main_menu(cid)
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش ياحب!", show_alert=True)
        return

    # فحص الاشتراك قبل المتابعة في أي قسم
    if not is_subscribed(uid):
        bot.answer_callback_query(call.id, "⚠️ اشترك في القناة الأول!", show_alert=True)
        return

    if call.data == "orange_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="start_fwz"),
            types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="start_500mb"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")
        )
        bot.edit_message_text("قسم أورانج 🟠 - اختر الخدمة:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "free_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("رصيد أورانج 💰", callback_data="check_bal"),
            types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="prayer"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")
        )
        bot.edit_message_text("الخدمات المجانية ⚙:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "back_home":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid)

    elif call.data == "service_off":
        bot.answer_callback_query(call.id, "🛠 الخدمة دي في الصيانة حالياً.", show_alert=True)

    # --- ربط خطوات التنفيذ (إدخال البيانات) ---
    elif call.data == "start_fwz":
        user_data[cid] = {'action': 'fawazeer'}
        bot.send_message(cid, "📱 ابعت رقم أورانج الخاص بك:")
        
    elif call.data == "check_bal":
        user_data[cid] = {'action': 'balance'}
        bot.send_message(cid, "💰 ابعت رقم أورانج لمعرفة رصيده:")

# --- [ معالجة خطوات الإدخال والـ APIs ] ---
@bot.message_handler(func=lambda m: m.chat.id in user_data)
def workflow(m):
    cid = m.chat.id
    action = user_data[cid].get('action')
    
    if action == 'balance':
        phone = m.text.strip()
        bot.send_message(cid, "⏳ جاري فحص الرصيد...")
        # تنفيذ سكريبت الرصيد الذي أرسلته سابقاً
        try:
            url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
            res = requests.post(url, json={"RecipientDial": phone, "Dial": phone}, timeout=10).json()
            balance = res.get('CreditBalance', '0')
            bot.send_message(cid, f"💰 رصيد الرقم {phone} هو: {balance} جنيه.")
        except:
            bot.send_message(cid, "❌ تعذر الفحص، تأكد من الرقم.")
        del user_data[cid]
        show_main_menu(cid)
    
    # (يمكنك إضافة بقية خطوات الفوازير والـ 500MB هنا بنفس المنطق)

print("✅ MIDO BOT IS ONLINE WITH NEW TOKEN")
bot.infinity_polling()
