import telebot
import requests
import json
import sqlite3
import time
from telebot import types 

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U' 
CHANNEL_ID = '@midooojiokjj'      # قناتك الجديدة
ADMIN_ID = 7721807760             # آيدي ميدو
DEV_USER = '@AMI_EG'              # يوزر المطور
bot = telebot.TeleBot(API_TOKEN) 

# --- [ إعداد قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER, orange_status INTEGER, free_status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1, 1, 1)')
    conn.commit()
    conn.close() 

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close() 

init_db() 

# --- [ دوال المساعدة ] ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True # ميدو يتخطى الاشتراك
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False 

def get_settings():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT status, orange_status, free_status FROM settings')
    res = c.fetchone()
    conn.close()
    return res if res else (1, 1, 1)

# --- [ الكيبوردات الشفافة ] ---
def admin_markup():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    st, ost, fst = get_settings()
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if st == 1 else "🔴 البوت متوقف"
    o_text = "🟠 أورانج: تشغيل" if ost == 1 else "🟠 أورانج: إيقاف"
    f_text = "⚙️ الإضافية: تشغيل" if fst == 1 else "⚙️ الإضافية: إيقاف"
    
    markup.add(
        types.InlineKeyboardButton(f"👥 مستخدمين البوت: {count}", callback_data="none"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_bot"),
        types.InlineKeyboardButton(o_text, callback_data="toggle_orange"),
        types.InlineKeyboardButton(f_text, callback_data="toggle_free"),
        types.InlineKeyboardButton("📣 إذاعة رسالة للكل", callback_data="broadcast")
    )
    return markup 

def user_main_markup():
    st, ost, fst = get_settings()
    markup = types.InlineKeyboardMarkup(row_width=1)
    if ost == 1:
        markup.add(types.InlineKeyboardButton("حل فوازير أورانج 🎁", callback_data="orange_flow"))
    if fst == 1:
        markup.add(
            types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="ai_image"),
            types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="prayer_times")
        )
    markup.add(types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}"))
    return markup 

# --- [ معالجة الأوامر والرسائل ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    add_user(uid)
    st, ost, fst = get_settings()

    if uid == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً بك يا ميدو في لوحة التحكم:", reply_markup=admin_markup())
        # إرسال قائمة المستخدم أيضاً للأدمن ليجرب البوت
        bot.send_message(message.chat.id, "قائمة المستخدم (للتجربة):", reply_markup=user_main_markup())
        return 

    if st == 0:
        bot.send_message(message.chat.id, "⚠️ البوت حالياً في صيانة سريعة.")
        return 

    if check_sub(uid):
        bot.send_message(message.chat.id, "✅ تم التحقق! اختر الخدمة:", reply_markup=user_main_markup())
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("قناة البوت 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"),
            types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub")
        )
        bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القناة أولاً.", reply_markup=markup) 

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    st, ost, fst = get_settings()

    if call.data == "check_sub":
        if check_sub(uid):
            bot.edit_message_text("✅ تم الاشتراك! اختر خدمتك:", cid, call.message.message_id, reply_markup=user_main_markup())
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشتركتش!", show_alert=True)
            
    elif call.data == "orange_flow":
        bot.send_message(cid, "ابعت بياناتك كدا: `الرقم:الباسورد`", parse_mode="Markdown")

    elif call.data == "ai_image":
        msg = bot.send_message(cid, "🎨 ابعت وصف الصورة بالإنجليزي:")
        bot.register_next_step_handler(msg, process_ai_image)

    elif call.data == "prayer_times":
        msg = bot.send_message(cid, "🕌 ابعت اسم مدينتك بالإنجليزي (Cairo):")
        bot.register_next_step_handler(msg, process_prayer)

    # --- تحكم الأدمن ---
    elif uid == ADMIN_ID:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        if call.data == "toggle_bot":
            c.execute('UPDATE settings SET status = ?', (0 if st == 1 else 1,))
        elif call.data == "toggle_orange":
            c.execute('UPDATE settings SET orange_status = ?', (0 if ost == 1 else 1,))
        elif call.data == "toggle_free":
            c.execute('UPDATE settings SET free_status = ?', (0 if fst == 1 else 1,))
        elif call.data == "broadcast":
            msg = bot.send_message(cid, "ابعت رسالة الإذاعة:")
            bot.register_next_step_handler(msg, do_broadcast)
            conn.close()
            return
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=admin_markup())

# --- [ الوظائف المدمجة ] ---
def process_ai_image(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, f"https://image.pollinations.ai/prompt/{message.text}", caption="🎨 صورتك جاهزة ياحب")

def process_prayer(message):
    try:
        res = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={message.text}&country=Egypt&method=5").json()
        t = res['data']['timings']
        bot.send_message(message.chat.id, f"🕌 مواقيت الصلاة في {message.text}:\nالفجر: {t['Fajr']}\nالظهر: {t['Dhuhr']}\nالمغرب: {t['Maghrib']}\nالعشاء: {t['Isha']}")
    except: bot.send_message(message.chat.id, "❌ خطأ في الاسم.")

def do_broadcast(message):
    # كود الإذاعة الخاص بك
    pass

# --- [ تشغيل سكريبت أورانج ] ---
@bot.message_handler(func=lambda message: ":" in message.text)
def handle_orange(message):
    if not check_sub(message.from_user.id): return
    # هنا يتم استدعاء منطق run_orange_process اللي في كودك
    bot.reply_to(message, "⏳ جاري تنفيذ سكريبت أورانج...")

bot.infinity_polling()
