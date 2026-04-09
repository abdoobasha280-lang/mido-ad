import telebot
import requests
import json
import sqlite3
import time
import hashlib
import random
import urllib.parse
from telebot import types

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'
BOT_NAME = "Netmido"
bot = telebot.TeleBot(API_TOKEN)

# إحصائيات
stats = {"success": 0, "failed": 0}

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('netmido_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('netmido_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    try:
        conn = sqlite3.connect('netmido_system.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT status FROM settings')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 1
    except: return 1

init_db()

# --- [ ترجمة ردود النظام ] ---
def translate_response(text):
    responses = {
        "Success": "تمت العملية بنجاح.",
        "Invalid Password": "كلمة المرور غير صحيحة.",
        "Invalid Mobile Number": "رقم الهاتف غير صحيح.",
        "You have already redeemed this promo": "لقد حصلت على هذه الهدية من قبل.",
        "Internal Server Error": "خطأ في سيرفر الشركة، جرب لاحقاً.",
        "User is not allowed to perform this action": "غير مسموح لهذا الرقم بتنفيذ الطلب."
    }
    return responses.get(text, f"رد النظام: {text}")

# --- [ مواقيت الصلاة ] ---
def get_prayer_times():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
        data = requests.get(url, timeout=10).json()['data']['timings']
        res = "🕌 مواقيت الصلاة في القاهرة:\n\n"
        res += f"الفجر: {data['Fajr']}\n"
        res += f"الشروق: {data['Sunrise']}\n"
        res += f"الظهر: {data['Dhuhr']}\n"
        res += f"العصر: {data['Asr']}\n"
        res += f"المغرب: {data['Maghrib']}\n"
        res += f"العشاء: {data['Isha']}"
        return res
    except: return "عذراً، فشل جلب المواقيت."

# --- [ لوحات التحكم ] ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("خدمات إضافية", callback_data="extra_services"),
        types.InlineKeyboardButton("المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return m

def orange_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("هدية 500 ميجا", callback_data="gift_500"),
        types.InlineKeyboardButton("حل فوازير شريهان", callback_data="solve_fawazeer"),
        types.InlineKeyboardButton("العودة للقائمة الرئيسية", callback_data="main_home")
    )
    return m

def extra_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("رسم صورة ذكاء اصطناعي", callback_data="draw_image"),
        types.InlineKeyboardButton("مواقيت الصلاة", callback_data="prayer_times"),
        types.InlineKeyboardButton("العودة للقائمة الرئيسية", callback_data="main_home")
    )
    return m

def admin_menu():
    conn = sqlite3.connect('netmido_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    m = types.InlineKeyboardMarkup(row_width=1)
    status_txt = "تعطيل البوت" if get_bot_status() == 1 else "تفعيل البوت"
    m.add(
        types.InlineKeyboardButton(f"عدد المستخدمين: {count}", callback_data="none"),
        types.InlineKeyboardButton(f"العمليات الناجحة: {stats['success']}", callback_data="none"),
        types.InlineKeyboardButton(status_txt, callback_data="toggle_bot"),
        types.InlineKeyboardButton("إرسال إذاعة عامة", callback_data="admin_broadcast")
    )
    return m

# --- [ تنفيذ خدمات أورانج ] ---
def run_orange_task(num, pwd, mode):
    session = requests.Session()
    try:
        login_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": num, "isAndroid": True, "lang": "ar", "password": pwd
        }
        r1 = session.post(login_url, json=payload, timeout=15).json()
        if 'SignInUserResult' not in r1: return "البيانات المدخلة غير صحيحة."
        uid = r1['SignInUserResult']['UserData']['UserID']

        t_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        t_pay = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        r2 = session.post(t_url, data=t_pay, timeout=15).json()
        ctv = r2['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        if mode == "gift":
            final_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
            p = {"Language":"ar","PromoCode":"رمضان كريم","dial":num,"password":pwd,"Channelname":"MobinilAndMe","ChannelPassword":"ig3yh*mk5l42@oj7QAR8yF"}
        else:
            final_url = "https://services.orange.eg/APIs/Promotions/api/Fawazeer/Solve"
            p = {"Language":"ar","dial":num,"password":pwd,"Channelname":"MobinilAndMe"}

        h = {"_ctv": ctv, "_htv": htv, "UserId": uid, "Content-Type": "application/json"}
        r3 = session.post(final_url, headers=h, json=p, timeout=15).json()
        
        raw_res = r3.get('ErrorDescription', '')
        if raw_res == "Success": stats["success"] += 1
        return translate_response(raw_res)
    except: return "فشل الاتصال بسيرفر الشركة."

# --- [ المعالجات ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if get_bot_status() == 0 and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "البوت متوقف حالياً للصيانة.")
        return
    bot.send_message(message.chat.id, f"مرحباً بك في {BOT_NAME}\nيرجى اختيار القسم المطلوب:", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "إعدادات المدير:", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    cid = call.message.chat.id
    if call.data == "main_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, call.message.message_id, reply_markup=main_menu())
    elif call.data == "orange_menu":
        bot.edit_message_text("قائمة خدمات أورانج:", cid, call.message.message_id, reply_markup=orange_menu())
    elif call.data == "extra_services":
        bot.edit_message_text("قائمة الخدمات الإضافية:", cid, call.message.message_id, reply_markup=extra_menu())
    elif call.data == "prayer_times":
        bot.edit_message_text(get_prayer_times(), cid, call.message.message_id, reply_markup=extra_menu())
    elif call.data in ["gift_500", "solve_fawazeer"]:
        mode = "gift" if call.data == "gift_500" else "fawazeer"
        msg = bot.send_message(cid, "أدخل رقم الهاتف (11 رقم):")
        bot.register_next_step_handler(msg, step_get_num, mode)
    elif call.data == "draw_image":
        msg = bot.send_message(cid, "أدخل وصف الصورة (باللغة الإنجليزية):")
        bot.register_next_step_handler(msg, step_draw)
    elif call.data == "toggle_bot" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('netmido_system.db', check_same_thread=False)
        c = conn.cursor()
        new_val = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_val,))
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=admin_menu())
    elif call.data == "admin_broadcast" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(cid, "أدخل الرسالة المراد إرسالها للجميع:")
        bot.register_next_step_handler(msg, step_broadcast)

def step_get_num(message, mode):
    num = message.text.strip()
    if len(num) != 11:
        bot.send_message(message.chat.id, "الرقم غير صحيح.")
        return
    msg = bot.send_message(message.chat.id, "أدخل كلمة السر الخاصة بالتطبيق:")
    bot.register_next_step_handler(msg, step_get_pass, num, mode)

def step_get_pass(message, num, mode):
    pwd = message.text.strip()
    wait = bot.send_message(message.chat.id, "جاري معالجة الطلب...")
    result = run_orange_task(num, pwd, mode)
    # إرسال النتيجة بدون لوحة الأزرار كما طلبت
    bot.send_message(message.chat.id, result)

def step_draw(message):
    prompt = message.text
    bot.reply_to(message, "جاري رسم الصورة...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
        bot.send_photo(message.chat.id, url, caption="تم التوليد بواسطة Netmido")
    except: bot.send_message(message.chat.id, "حدث خطأ أثناء الرسم.")

def step_broadcast(message):
    conn = sqlite3.connect('netmido_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    for u in users:
        try: bot.send_message(u[0], message.text)
        except: pass
    bot.send_message(ADMIN_ID, "تمت الإذاعة بنجاح.")

if __name__ == "__main__":
    bot.infinity_polling()
