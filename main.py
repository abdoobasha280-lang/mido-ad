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

# إحصائيات الجلسة الحالية
stats = {"success": 0, "failed": 0}
user_step_data = {}

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    try:
        conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT status FROM settings')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 1
    except: return 1

init_db()

# --- [ موديول الصلاة ] ---
def get_prayer_times():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
        data = requests.get(url, timeout=10).json()['data']['timings']
        res = f"🕌 مواقيت الصلاة في القاهرة:\n\n"
        res += f"الفجر: {data['Fajr']}\nالشروق: {data['Sunrise']}\n"
        res += f"الظهر: {data['Dhuhr']}\nالعصر: {data['Asr']}\n"
        res += f"المغرب: {data['Maghrib']}\nالعشاء: {data['Isha']}"
        return res
    except: return "عذراً، في مشكلة في جلب المواعيد حالياً."

# --- [ الكيبوردات - أزرار تحت بعض ] ---
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
        types.InlineKeyboardButton("رسم صورة بالذكاء الاصطناعي", callback_data="draw_image"),
        types.InlineKeyboardButton("مواقيت الصلاة", callback_data="prayer_times"),
        types.InlineKeyboardButton("العودة للقائمة الرئيسية", callback_data="main_home")
    )
    return m

def admin_menu():
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    m = types.InlineKeyboardMarkup(row_width=1)
    status_label = "إيقاف البوت" if get_bot_status() == 1 else "تشغيل البوت"
    m.add(
        types.InlineKeyboardButton(f"عدد المشتركين: {count}", callback_data="none"),
        types.InlineKeyboardButton(f"ناجح: {stats['success']} | فاشل: {stats['failed']}", callback_data="none"),
        types.InlineKeyboardButton(status_label, callback_data="toggle_bot"),
        types.InlineKeyboardButton("إرسال إذاعة (للجميع)", callback_data="broadcast_msg")
    )
    return m

# --- [ منطق أورانج ] ---
def orange_api_call(number, password, mode):
    session = requests.Session()
    try:
        login_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        login_data = {
            "appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password
        }
        r1 = session.post(login_url, json=login_data, timeout=15).json()
        if 'SignInUserResult' not in r1: return "الرقم أو الباسوورد غلط، اتأكد وجرب تاني."
        uid = r1['SignInUserResult']['UserData']['UserID']

        t_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        t_payload = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        r2 = session.post(t_url, data=t_payload, timeout=15).json()
        ctv = r2['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        if mode == "gift":
            final_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
            payload = {"Language":"ar","PromoCode":"رمضان كريم","dial":number,"password":password,"Channelname":"MobinilAndMe","ChannelPassword":"ig3yh*mk5l42@oj7QAR8yF"}
        else:
            final_url = "https://services.orange.eg/APIs/Promotions/api/Fawazeer/Solve"
            payload = {"Language":"ar","dial":number,"password":password,"Channelname":"MobinilAndMe"}

        h_final = {"_ctv": ctv, "_htv": htv, "UserId": uid, "Content-Type": "application/json"}
        r3 = session.post(final_url, headers=h_final, json=payload, timeout=15).json()
        
        desc = r3.get('ErrorDescription', 'تمت العملية')
        if desc == "Success":
            stats["success"] += 1
            return "مبروك! الطلب تم بنجاح."
        stats["failed"] += 1
        return f"رد الشركة: {desc}"
    except: return "السيرفر تقيل شوية، جرب كمان دقيقة."

# --- [ الأوامر والمعالجات ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if get_bot_status() == 0 and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "عذراً، البوت في صيانة حالياً.")
        return
    bot.send_message(message.chat.id, f"أهلاً بك في {BOT_NAME}\nاختر الخدمة اللي محتاجها من الأزرار:", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "لوحة تحكم المدير:", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    if call.data == "main_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, call.message.message_id, reply_markup=main_menu())
    elif call.data == "orange_menu":
        bot.edit_message_text("خدمات أورانج المتاحة:", cid, call.message.message_id, reply_markup=orange_menu())
    elif call.data == "extra_services":
        bot.edit_message_text("خدمات إضافية متنوعة:", cid, call.message.message_id, reply_markup=extra_menu())
    elif call.data == "prayer_times":
        bot.edit_message_text(get_prayer_times(), cid, call.message.message_id, reply_markup=extra_menu())
    elif call.data == "gift_500" or call.data == "solve_fawazeer":
        mode = "gift" if call.data == "gift_500" else "fawazeer"
        msg = bot.send_message(cid, "اكتب رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, get_num, mode)
    elif call.data == "draw_image":
        msg = bot.send_message(cid, "اكتب وصف الصورة اللي عاوز ترسمها:")
        bot.register_next_step_handler(msg, process_draw)
    elif call.data == "toggle_bot" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
        c = conn.cursor()
        new_s = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,))
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=admin_menu())
    elif call.data == "broadcast_msg" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(cid, "اكتب الرسالة اللي عاوز تبعتها لكل المشتركين:")
        bot.register_next_step_handler(msg, send_broadcast)

def get_num(message, mode):
    num = message.text.strip()
    if len(num) != 11:
        bot.send_message(message.chat.id, "الرقم غير صحيح.")
        return
    msg = bot.send_message(message.chat.id, "اكتب كلمة سر تطبيق My Orange:")
    bot.register_next_step_handler(msg, get_pass, num, mode)

def get_pass(message, num, mode):
    pwd = message.text.strip()
    wait = bot.send_message(message.chat.id, "جاري التنفيذ...")
    res = orange_api_call(num, pwd, mode)
    bot.send_message(message.chat.id, res, reply_markup=main_menu())

def process_draw(message):
    prompt = message.text
    wait = bot.reply_to(message, "جاري الرسم...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
        bot.send_photo(message.chat.id, url, caption="تم الرسم بواسطة Netmido", reply_markup=main_menu())
    except: bot.send_message(message.chat.id, "فشل في الرسم، جرب وصف تاني.")

def send_broadcast(message):
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    for u in users:
        try: bot.send_message(u[0], message.text)
        except: pass
    bot.send_message(ADMIN_ID, "تم إرسال الإذاعة بنجاح.")

if __name__ == "__main__":
    bot.infinity_polling()
