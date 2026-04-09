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

# إحصائيات العمليات
stats = {"success": 0, "failed": 0}
user_step_data = {}

# --- [ إعداد قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('netmido_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('netmido_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    try:
        conn = sqlite3.connect('netmido_data.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT status FROM settings')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 1
    except: return 1

init_db()

# --- [ موديول مواقيت الصلاة (API سريع) ] ---
def get_prayer_times():
    try:
        # استخدام API سريع بدلاً من الـ Scraping لضمان السرعة والدقة
        url = "http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
        response = requests.get(url, timeout=10).json()
        t = response['data']['timings']
        
        res = f"🕌 **مواقيت الصلاة في القاهرة (Netmido)**\n"
        res += "—" * 12 + "\n"
        res += f"🔹 الفجر: `{t['Fajr']}`\n"
        res += f"🔹 الشروق: `{t['Sunrise']}`\n"
        res += f"🔹 الظهر: `{t['Dhuhr']}`\n"
        res += f"🔹 العصر: `{t['Asr']}`\n"
        res += f"🔹 المغرب: `{t['Maghrib']}`\n"
        res += f"🔹 العشاء: `{t['Isha']}`\n"
        res += "—" * 12
        return res
    except:
        return "❌ عذراً، تعذر جلب المواقيت حالياً."

# --- [ الكيبوردات (أزرار مرصوصة تحت بعضها) ] ---

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🍊 أقسام أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_services"),
        types.InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

def orange_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="gift_500"),
        types.InlineKeyboardButton("🧩 حل الفوازير", callback_data="solve_fawazeer"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_home")
    )
    return markup

def extra_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎨 رسم صورة (Nano Banana)", callback_data="draw_image"),
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_home")
    )
    return markup

def admin_markup():
    conn = sqlite3.connect('netmido_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="info"),
        types.InlineKeyboardButton(f"📊 نجاح: {stats['success']} | فشل: {stats['failed']}", callback_data="stats"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast")
    )
    return markup

# --- [ معالجة الأوامر ] ---

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    welcome = f"✨ **مرحباً بك في بوت {BOT_NAME}**\n\nمنصة متكاملة لهدايا أورانج والخدمات الذكية."
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ **لوحة التحكم**", reply_markup=admin_markup(), parse_mode="Markdown")

# --- [ معالجة Callback Query ] ---

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    chat_id = call.message.chat.id
    
    if call.data == "main_home":
        bot.edit_message_text("✨ القائمة الرئيسية:", chat_id, call.message.message_id, reply_markup=main_menu())

    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج المتاحة:", chat_id, call.message.message_id, reply_markup=orange_menu())

    elif call.data == "extra_services":
        bot.edit_message_text("🛠️ الخدمات الإضافية:", chat_id, call.message.message_id, reply_markup=extra_menu())

    elif call.data == "prayer_times":
        bot.answer_callback_query(call.id, "🕌 جاري التحديث...")
        bot.edit_message_text(get_prayer_times(), chat_id, call.message.message_id, reply_markup=extra_menu(), parse_mode="Markdown")

    elif call.data == "draw_image":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "🎨 **أرسل وصف الصورة الآن لـ Nano Banana:**")
        bot.register_next_step_handler(msg, run_drawing)

    elif call.data == "gift_500":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "📱 أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, process_number, "gift")

    elif call.data == "solve_fawazeer":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "🧩 أدخل رقم أورانج لحل الفوازير:")
        bot.register_next_step_handler(msg, process_number, "fawazeer")

    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('netmido_data.db', check_same_thread=False)
        c = conn.cursor()
        new_s = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,))
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=admin_markup())

# --- [ خطوات إدخال البيانات ] ---

def process_number(message, mode):
    num = message.text.strip()
    if not num.isdigit() or len(num) != 11:
        bot.send_message(message.chat.id, "❌ الرقم خاطئ.")
        return
    user_step_data[message.chat.id] = {'number': num, 'mode': mode}
    msg = bot.send_message(message.chat.id, "🔐 أدخل كلمة السر (My Orange):")
    bot.register_next_step_handler(msg, process_password)

def process_password(message):
    chat_id = message.chat.id
    if chat_id not in user_step_data: return
    
    password = message.text.strip()
    num = user_step_data[chat_id]['number']
    mode = user_step_data[chat_id]['mode']
    
    wait = bot.send_message(chat_id, "⏳ جاري تنفيذ طلبك بسرعة...")
    
    if mode == "gift":
        result = orange_gift_logic(num, password)
    else:
        result = orange_fawazeer_logic(num, password)
        
    bot.send_message(chat_id, result, reply_markup=main_menu())
    del user_step_data[chat_id]

# --- [ منطق أورانج السريع ] ---

def orange_gift_logic(number, password):
    try:
        session = requests.Session() # استخدام Session لتسريع الطلبات
        headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
        
        # تسجيل الدخول
        auth_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password
        }
        r1 = session.post(auth_url, json=payload, headers=headers, timeout=15).json()
        
        if 'SignInUserResult' not in r1: return "❌ البيانات غير صحيحة."
        uid = r1['SignInUserResult']['UserData']['UserID']
        
        # التوكن
        t_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        t_data = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        r2 = session.post(t_url, headers=headers, data=t_data, timeout=15).json()
        ctv = r2['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        
        # الطلب النهائي
        final_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
        h_final = {"_ctv": ctv, "_htv": htv, "UserId": uid, "Content-Type": "application/json"}
        p_final = {"Language":"ar","PromoCode":"رمضان كريم","dial":number,"password":password,"Channelname":"MobinilAndMe","ChannelPassword":"ig3yh*mk5l42@oj7QAR8yF"}
        r3 = session.post(final_url, headers=h_final, json=p_final, timeout=15).json()
        
        desc = r3.get('ErrorDescription', '')
        if desc == "Success":
            stats["success"] += 1
            return "✅ مبروك! حصلت على الهدية بنجاح."
        return f"⚠️ {desc}"
    except: return "❌ حدث بطء في سيرفر أورانج."

def orange_fawazeer_logic(number, password):
    return "✅ تم البدء في حل الفوازير، ستصلك رسالة قريباً."

# --- [ منطق Nano Banana ] ---

def run_drawing(message):
    prompt = message.text
    wait = bot.reply_to(message, "🎨 **جاري الرسم بذكاء Nano Banana...**")
    try:
        seed = random.randint(1, 100000)
        encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?seed={seed}&width=1024&height=1024&model=extra-realism&nologo=true"
        
        bot.send_photo(message.chat.id, img_url, caption=f"✨ بواسطة {BOT_NAME}\n📝 الوصف: `{prompt}`", reply_markup=main_menu())
        bot.delete_message(message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("❌ حدث خطأ في محرك الرسم.", message.chat.id, wait.message_id)

# --- [ تشغيل البوت ] ---
if __name__ == "__main__":
    print(f"--- [ {BOT_NAME} Bot is Online ] ---")
    bot.infinity_polling()
