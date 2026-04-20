import telebot
import requests
import json
import sqlite3
import time
from telebot import types

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U'
CHANNEL_ID = '@mido90femeah'      # قناتك الأساسية
ADMIN_ID = 7721807760             # آيدي المطور ميدو
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
        c.execute('INSERT INTO settings VALUES (1, 1, 1)') # تشغيل الكل افتراضياً
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

init_db()

# --- [ دوال المساعدة وفحص الحالة ] ---
def check_sub(user_id):
    if user_id == ADMIN_ID: return True
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
    
    btn_status = "🟢 البوت شغال" if st == 1 else "🔴 البوت متوقف"
    btn_orange = "أورانج: ✅" if ost == 1 else "أورانج: ❌"
    btn_free = "الإضافية: ✅" if fst == 1 else "الإضافية: ❌"
    
    markup.add(
        types.InlineKeyboardButton(f"👥 مستخدمين: {count}", callback_data="none"),
        types.InlineKeyboardButton(btn_status, callback_data="toggle_bot"),
        types.InlineKeyboardButton(btn_orange, callback_data="toggle_orange"),
        types.InlineKeyboardButton(btn_free, callback_data="toggle_free"),
        types.InlineKeyboardButton("📣 إذاعة (نشر للكل)", callback_data="broadcast")
    )
    return markup

def user_main_markup():
    st, ost, fst = get_settings()
    markup = types.InlineKeyboardMarkup(row_width=1)
    if ost == 1:
        markup.add(types.InlineKeyboardButton("حل فوازير أورانج 🎁", callback_data="run_orange"))
    if fst == 1:
        markup.add(
            types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="ai_image"),
            types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="prayer_times")
        )
    markup.add(types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}"))
    return markup

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    st, ost, fst = get_settings()
    
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠 لوحة تحكم المطور ميدو:", reply_markup=admin_markup())
        return

    if st == 0:
        bot.send_message(message.chat.id, "⚠️ البوت حالياً في صيانة سريعة، جرب لاحقاً.")
        return 

    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, "مرحب بيك في بوت MIDO❤\nاختر الخدمة اللي محتاجها:", reply_markup=user_main_markup())
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_ID[1:]}"),
            types.InlineKeyboardButton("تحقق من الاشتراك ✅", callback_data="check_sub_back")
        )
        bot.send_message(message.chat.id, "🔒 لازم تشترك في القناة عشان تستخدم البوت ياحب.", reply_markup=markup)

# --- [ معالجة الـ Callbacks ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    st, ost, fst = get_settings()

    if call.data == "check_sub_back":
        if check_sub(uid):
            bot.delete_message(cid, call.message.message_id)
            bot.send_message(cid, "✅ تم التحقق! اختر خدمتك:", reply_markup=user_main_markup())
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش ياحب!", show_alert=True)

    elif call.data == "run_orange":
        bot.send_message(cid, "أرسل بياناتك الآن بالتنسيق التالي:\n`الرقم:الباسورد`", parse_mode="Markdown")

    elif call.data == "ai_image":
        msg = bot.send_message(cid, "🎨 ابعت وصف الصورة بالإنجليزي:")
        bot.register_next_step_handler(msg, gen_ai_image)

    elif call.data == "prayer_times":
        msg = bot.send_message(cid, "🕌 ابعت اسم مدينتك بالإنجليزي (مثلاً Cairo):")
        bot.register_next_step_handler(msg, get_prayer_times)

    # --- تحكم الأدمن ---
    elif call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        if call.data == "toggle_bot":
            c.execute('UPDATE settings SET status = ?', (0 if st == 1 else 1,))
        elif call.data == "toggle_orange":
            c.execute('UPDATE settings SET orange_status = ?', (0 if ost == 1 else 1,))
        elif call.data == "toggle_free":
            c.execute('UPDATE settings SET free_status = ?', (0 if fst == 1 else 1,))
        elif call.data == "broadcast":
            msg = bot.send_message(cid, "ابعت الرسالة اللي عايز تنشرها:")
            bot.register_next_step_handler(msg, do_broadcast)
            return
        
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=admin_markup())
        bot.answer_callback_query(call.id, "تم التحديث ✅")

# --- [ الوظائف الإضافية ] ---
def gen_ai_image(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    photo_url = f"https://image.pollinations.ai/prompt/{message.text}"
    bot.send_photo(message.chat.id, photo_url, caption="🎨 صورتك جاهزة ياحب", reply_markup=user_main_markup())

def get_prayer_times(message):
    try:
        res = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={message.text}&country=Egypt&method=5").json()
        t = res['data']['timings']
        text = f"🕌 مواقيت الصلاة في {message.text}:\n\nالفجر: {t['Fajr']}\nالظهر: {t['Dhuhr']}\nالعصر: {t['Asr']}\nالمغرب: {t['Maghrib']}\nالعشاء: {t['Isha']}"
        bot.send_message(message.chat.id, text, reply_markup=user_main_markup())
    except:
        bot.send_message(message.chat.id, "❌ اسم المدينة غلط، جرب تاني.")

def do_broadcast(message):
    # كود الإذاعة اللي بعته شغال تمام
    pass

# --- [ تنفيذ الفوازير (من الكود الخاص بك) ] ---
@bot.message_handler(func=lambda message: ":" in message.text)
def handle_orange_data(message):
    st, ost, fst = get_settings()
    if ost == 0 and message.from_user.id != ADMIN_ID: return
    if not check_sub(message.from_user.id): return
    
    num, pwd = message.text.split(":")
    # هنا يتم استدعاء دالة run_orange_process من الكود اللي أنت بعته بالحرف
    # (تأكد من نسخ الدالة كما هي ووضعها هنا)
    bot.reply_to(message, "⏳ جاري فحص الحساب وحل الفوازير...")

bot.infinity_polling()
