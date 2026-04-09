import telebot
import requests
import json
import sqlite3
import time
import hashlib
import urllib.parse
import random
from telebot import types 

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk' 
ADMIN_ID = 7721807760             
DEV_USER = '@AMI_EG'              
BOT_NAME = "Mido AI"
bot = telebot.TeleBot(API_TOKEN) 

# إحصائيات الجلسة للأدمن
stats = {"success": 0, "failed": 0}

# --- [ إعداد قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT status FROM settings')
    res = c.fetchone()
    conn.close()
    return res[0] if res else 1 

init_db()

# --- [ جلب مواقيت الصلاة ] ---
def get_prayer_times():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
        data = requests.get(url, timeout=10).json()['data']['timings']
        res = "🕌 مواقيت الصلاة (القاهرة):\n\n"
        res += f"الفجر: {data['Fajr']}\nالشروق: {data['Sunrise']}\n"
        res += f"الظهر: {data['Dhuhr']}\nالعصر: {data['Asr']}\n"
        res += f"المغرب: {data['Maghrib']}\nالعشاء: {data['Isha']}"
        return res
    except: return "⚠️ تعذر جلب المواقيت حالياً."

# --- [ الكيبوردات الشفافة ] ---
def user_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🍊 خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_menu"),
        types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup 

def orange_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="get_500mb"),
        types.InlineKeyboardButton("🧩 حل الفوازير", callback_data="solve_fawazeer"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_home")
    )
    return markup

def extra_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_show"),
        types.InlineKeyboardButton("🎨 رسم صورة AI", callback_data="draw_ai"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_home")
    )
    return markup

def admin_markup():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(f"👥 مستخدمين البوت: {count}", callback_data="count"),
        types.InlineKeyboardButton(f"✅ نجاح: {stats['success']} | ❌ فشل: {stats['failed']}", callback_data="stats"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast"),
        types.InlineKeyboardButton("🚀 تشغيل البوت لنفسي", callback_data="back_home")
    )
    return markup 

# --- [ منطق خدمات أورانج بالأكواد الأصلية ] ---
def run_fawazeer(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري فحص الحساب وحل الفوازير...")
    session = requests.Session()
    headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"} 
    try:
        auth_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        auth_payload = {"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        res = session.post(auth_url, json=auth_payload, headers=headers).json()
        if 'SignInUserResult' not in res:
            stats["failed"] += 1
            bot.edit_message_text("❌ بيانات الدخول خطأ.", chat_id, loading.message_id); return

        acc_token = res['SignInUserResult']['AccessToken']
        gen_url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        headers['Token'] = acc_token
        token_res = session.post(gen_url, json={"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}, headers=headers).json()
        token = token_res.get("Token")

        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_data = session.post(q_url, json={"Dial": number, "Language": "ar", "Token": token}, headers=headers).json() 
        if q_data.get('ErrorCode') == 1:
            bot.edit_message_text("❌ شاركت اليوم بالفعل.", chat_id, loading.message_id); return 

        answers = [{"QuestionId": q["Answers"][0]["QuestionId"], "AnswerId": next(a["Id"] for a in q["Answers"] if a["IsCorrect"])} for q in q_data.get("Questions", [])]
        submit_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        submit_res = session.post(submit_url, json={"Dial": number, "Language": "ar", "Token": token, "Answers": answers}, headers=headers).json() 

        if submit_res.get('ErrorDescription') == "FawazeerSuccess":
            stats["success"] += 1
            bot.edit_message_text("✅ تم حل الفوازير بنجاح!", chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            bot.edit_message_text(f"⚠️ رد النظام: {submit_res.get('ErrorDescription')}", chat_id, loading.message_id)
    except: bot.edit_message_text("❌ حدث خطأ غير متوقع.", chat_id, loading.message_id)

def run_500mb(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري معالجة طلب الـ 500 ميجا...")
    try:
        session = requests.Session()
        headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
        login_res = session.post("https://services.orange.eg/SignIn.svc/SignInUser", json={"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}, headers=headers).json()
        
        if 'SignInUserResult' not in login_res:
            bot.edit_message_text("❌ البيانات خطأ.", chat_id, loading.message_id); return
        
        user_id = login_res['SignInUserResult']['UserData']['UserID']
        token_res = session.post("https://services.orange.eg/GetToken.svc/GenerateToken", headers={"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9"}, data='{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}').json()
        ctv = token_res['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        
        res4 = session.post("https://services.orange.eg/APIs/Promotions/api/CAF/Redeem", headers={"_ctv": ctv, "_htv": htv, "UserId": user_id, "Content-Type": "application/json"}, json={"Language": "ar", "PromoCode": "رمضان كريم", "dial": number, "password": password, "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"}).json()
        
        error = res4.get('ErrorDescription', '')
        if error == "Success":
            stats["success"] += 1
            bot.edit_message_text("✅ مبروك! استلمت الـ 500 ميجا بنجاح.", chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            bot.edit_message_text(f"⚠️ رد الشركة: {error}", chat_id, loading.message_id)
    except: bot.edit_message_text("❌ حدث خطأ في النظام.", chat_id, loading.message_id)

# --- [ معالجة الأوامر والرسائل ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ لوحة تحكم الأدمن:", reply_markup=admin_markup())
        return
    if get_bot_status() == 0:
        bot.send_message(message.chat.id, "⚠️ البوت في وضع الصيانة حالياً.", reply_markup=user_main_markup())
        return 
    # الدخول مباشر بدون اشتراك اجباري
    bot.send_message(message.chat.id, f"🌟 أهلاً بك في {BOT_NAME}\nاختر الخدمة المطلوبة من القائمة أدناه:", reply_markup=user_main_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid, mid = call.message.chat.id, call.message.message_id
    if call.data == "back_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, mid, reply_markup=user_main_markup())
    elif call.data == "orange_menu":
        bot.edit_message_text("قسم خدمات أورانج:", cid, mid, reply_markup=orange_markup())
    elif call.data == "extra_menu":
        bot.edit_message_text("قسم الخدمات الإضافية:", cid, mid, reply_markup=extra_markup())
    elif call.data == "prayer_show":
        bot.edit_message_text(get_prayer_times(), cid, mid, reply_markup=extra_markup())
    elif call.data == "draw_ai":
        msg = bot.send_message(cid, "🎨 أرسل وصف الصورة (بالإنجليزي):")
        bot.register_next_step_handler(msg, process_draw)
    elif call.data in ["get_500mb", "solve_fawazeer"]:
        msg = bot.send_message(cid, "📱 أرسل رقم الهاتف:")
        bot.register_next_step_handler(msg, get_phone_step, call.data)
    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('users.db')
        c = conn.cursor(); new_s = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,)); conn.commit(); conn.close()
        bot.edit_message_reply_markup(cid, mid, reply_markup=admin_markup())
    elif call.data == "broadcast" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(cid, "📣 أرسل رسالة الإذاعة:")
        bot.register_next_step_handler(msg, do_broadcast)

def get_phone_step(message, mode):
    phone = message.text.strip()
    msg = bot.send_message(message.chat.id, "🔐 أرسل كلمة السر:")
    bot.register_next_step_handler(msg, get_pass_step, phone, mode)

def get_pass_step(message, phone, mode):
    pwd = message.text.strip()
    if mode == "get_500mb": run_500mb(message.chat.id, phone, pwd)
    else: run_fawazeer(message.chat.id, phone, pwd)

def process_draw(message):
    prompt = message.text
    bot.reply_to(message, "⏳ جاري الرسم...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
        bot.send_photo(message.chat.id, url, caption=f"✨ تم الرسم بواسطة {BOT_NAME}", reply_markup=user_main_markup())
    except: bot.send_message(message.chat.id, "❌ فشل الرسم.")

def do_broadcast(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor(); c.execute('SELECT user_id FROM users'); users = c.fetchall(); conn.close()
    for user in users:
        try: bot.send_message(user[0], message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ تمت الإذاعة بنجاح.")

if __name__ == "__main__":
    bot.infinity_polling()
