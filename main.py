import telebot
import requests
import hashlib
import json
from telebot import types

# --- [ الإعدادات الأساسية ] ---
BOT_TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
ADMIN_ID = 7721807760  # معرف المطور (ميدو)
bot = telebot.TeleBot(BOT_TOKEN)

# قناتك الوحيدة والأساسية
REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

# قاعدة بيانات التحكم
db = {
    "users": set(),
    "success_count": 0,
    "status": {"orange": True, "etisalat": True, "free": True}
}

user_data = {}

# --- [ وظيفة التحقق وتخطي الأدمن ] ---
def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True  # المطور يتخطى الاشتراك دائماً
    try:
        status = bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- [ القائمة الرئيسية ] ---
def show_main_menu(chat_id):
    db['users'].add(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=1) # رص الأزرار تحت بعض
    
    # تنسيق حالة الأزرار
    o_txt = "اورانج 🟠" if db['status']['orange'] else "اورانج (صيانة 🛠)"
    o_call = "orange_section" if db['status']['orange'] else "off"
    
    e_txt = "اتصالات 🟢" if db['status']['etisalat'] else "اتصالات (صيانة 🛠)"
    e_call = "etisalat_section" if db['status']['etisalat'] else "off"
    
    btn_orange = types.InlineKeyboardButton(o_txt, callback_data=o_call)
    btn_etisalat = types.InlineKeyboardButton(e_txt, callback_data=e_call)
    btn_free = types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="free_services")
    btn_dev = types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG")
    
    markup.add(btn_orange, btn_etisalat, btn_free, btn_dev)
    
    bot.send_message(chat_id, "مرحب بيك ياحب في بوت MIDO❤\nاختر القسم اللي يناسبك:", reply_markup=markup)

# --- [ معالجة الرسائل والأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if is_subscribed(uid):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_link = types.InlineKeyboardButton("اشترك في القناة هنا 📢", url=CHANNEL_LINK)
        btn_check = types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        markup.add(btn_link, btn_check)
        bot.send_message(message.chat.id, "🔒 عذراً ياحب، لازم تشترك في القناة عشان تقدر تستخدم البوت:", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_stats = types.InlineKeyboardButton(f"👥 مستخدمين: {len(db['users'])} | ✅ نجاح: {db['success_count']}", callback_data="none")
        
        o_t = "أورانج ✅" if db['status']['orange'] else "أورانج ❌"
        e_t = "اتصالات ✅" if db['status']['etisalat'] else "اتصالات ❌"
        
        btn_tog_o = types.InlineKeyboardButton(f"تبديل حالة {o_t}", callback_data="toggle_orange")
        btn_tog_e = types.InlineKeyboardButton(f"تبديل حالة {e_t}", callback_data="toggle_etisalat")
        btn_bc = types.InlineKeyboardButton("📢 إذاعة لكل المستخدمين", callback_data="admin_broadcast")
        
        markup.add(btn_stats, btn_tog_o, btn_tog_e, btn_bc)
        bot.send_message(message.chat.id, "🛠 لوحة تحكم المطور ميدو:", reply_markup=markup)

# --- [ معالجة الضغطات (Callbacks) ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    # منع غير المشتركين من أي أكشن
    if not is_subscribed(uid) and call.data != "check_sub":
        bot.answer_callback_query(call.id, "⚠️ اشترك الأول ياحب!", show_alert=True)
        return

    if call.data == "check_sub":
        if is_subscribed(uid):
            bot.answer_callback_query(call.id, "✅ نورت ياحب!")
            bot.delete_message(cid, call.message.message_id)
            show_main_menu(cid)
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش ياحب!", show_alert=True)

    elif call.data == "orange_section":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="run_fawazeer"),
                   types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="run_caf"),
                   types.InlineKeyboardButton("⬅️ رجوع", callback_data="home"))
        bot.edit_message_text("قسم أورانج 🟠 - اختر خدمتك:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "free_services":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("معرفة رصيد أورانج 💰", callback_data="step_balance"),
                   types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="step_prayer"),
                   types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="step_image"),
                   types.InlineKeyboardButton("⬅️ رجوع", callback_data="home"))
        bot.edit_message_text("الخدمات المجانية ⚙:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "home":
        bot.delete_message(cid, call.message.message_id)
        show_main_menu(cid)

    elif call.data == "off":
        bot.answer_callback_query(call.id, "🛠 الخدمة في الصيانة حالياً.", show_alert=True)

    # أوامر الإدارة
    elif call.data.startswith("toggle_") and uid == ADMIN_ID:
        svc = call.data.split("_")[1]
        db['status'][svc] = not db['status'][svc]
        bot.delete_message(cid, call.message.message_id)
        admin_panel(call.message)

print("✅ MIDO BOT IS ONLINE | CLEAN CODE")
bot.infinity_polling()
