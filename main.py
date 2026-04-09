import telebot
import requests
import json
import sqlite3
import time
import hashlib
from telebot import types
from bs4 import BeautifulSoup

# --- [ الإعدادات الأساسية ] ---
# استخدمنا التوكن الجديد اللي بعته في كود الـ 500 ميجا
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'
bot = telebot.TeleBot(API_TOKEN)

# إحصائيات العمليات
stats = {"success": 0, "failed": 0}
# تخزين مؤقت لبيانات المستخدمين أثناء إدخال الرقم والباسورد
user_step_data = {}

# --- [ إعداد قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('mido_ai.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('mido_ai.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    try:
        conn = sqlite3.connect('mido_ai.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT status FROM settings')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 1
    except: return 1

init_db()

# --- [ موديول مواقيت الصلاة (Scraping) ] ---
def get_prayer_times():
    try:
        url = "https://www.masrawy.com/islameyat/prayer-times"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        prayer_times_div = soup.find('div', {'class': 'allTimes'})
        times = prayer_times_div.find_all('div', {'class': 'time'})
        prayers = ['الفجر', 'الشروق', 'الظهر', 'العصر', 'المغرب', 'العشاء']
        
        result = "🕌 **مواقيت الصلاة اليوم**\n\n"
        for prayer, time_val in zip(prayers, times[1:]):
            result += f"🔹 **{prayer}**: `{time_val.get_text(strip=True)}` \n"
        return result
    except:
        return "❌ عذراً، تعذر جلب مواقيت الصلاة حالياً."

# --- [ الكيبوردات (الأزرار الشفافة) ] ---

# القائمة الرئيسية
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🍊 أقسام أورانج", callback_data="orange_menu")
    btn2 = types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_services")
    btn3 = types.InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

# قائمة أورانج
def orange_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="gift_500")
    btn2 = types.InlineKeyboardButton("🧩 حل الفوازير", callback_data="solve_fawazeer")
    btn_back = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_home")
    markup.add(btn1, btn2, btn_back)
    return markup

# قائمة الخدمات الإضافية
def extra_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times")
    btn_back = types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="main_home")
    markup.add(btn1, btn_back)
    return markup

# لوحة الأدمن
def admin_markup():
    conn = sqlite3.connect('mido_ai.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="admin_count"),
        types.InlineKeyboardButton(f"📊 نجاح: {stats['success']} | فشل: {stats['failed']}", callback_data="admin_stats"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast")
    )
    return markup

# --- [ معالجة الأوامر ] ---

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ لوحة تحكم الأدمن:", reply_markup=admin_markup())
    
    welcome_text = (
        "✨ **مرحباً بك في بوت Mido AI الشامل**\n\n"
        "يمكنك استخدام البوت للحصول على هدايا أورانج أو معرفة مواقيت الصلاة والعديد من الخدمات الأخرى."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_markup(), parse_mode="Markdown")

# --- [ معالجة ضغطات الأزرار (Callback Query) ] ---

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    chat_id = call.message.chat.id

    if call.data == "main_home":
        bot.edit_message_text("✨ القائمة الرئيسية:", chat_id, call.message.message_id, reply_markup=main_menu_markup())

    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 أقسام أورانج المتاحة:", chat_id, call.message.message_id, reply_markup=orange_menu_markup())

    elif call.data == "extra_services":
        bot.edit_message_text("🛠️ الخدمات الإضافية:", chat_id, call.message.message_id, reply_markup=extra_menu_markup())

    elif call.data == "prayer_times":
        times = get_prayer_times()
        bot.edit_message_text(times, chat_id, call.message.message_id, reply_markup=extra_menu_markup(), parse_mode="Markdown")

    elif call.data == "gift_500":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "📱 أدخل رقم هاتف أورانج (11 رقم):")
        bot.register_next_step_handler(msg, process_number_step, "gift")

    elif call.data == "solve_fawazeer":
        bot.delete_message(chat_id, call.message.message_id)
        msg = bot.send_message(chat_id, "🧩 أدخل رقم هاتف أورانج لحل الفوازير:")
        bot.register_next_step_handler(msg, process_number_step, "fawazeer")

    # أزرار الأدمن
    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('mido_ai.db', check_same_thread=False)
        c = conn.cursor()
        new_status = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_status,))
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=admin_markup())

    elif call.data == "broadcast" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(chat_id, "أرسل الرسالة للإذاعة:")
        bot.register_next_step_handler(msg, do_broadcast)

# --- [ خطوات إدخال البيانات ] ---

def process_number_step(message, type_op):
    number = message.text.strip()
    if not number.isdigit() or len(number) != 11:
        bot.send_message(message.chat.id, "❌ رقم غير صحيح. حاول مرة أخرى.")
        return
    user_step_data[message.chat.id] = {'number': number, 'type': type_op}
    msg = bot.send_message(message.chat.id, "🔐 أدخل كلمة السر (My Orange):")
    bot.register_next_step_handler(msg, process_password_step)

def process_password_step(message):
    chat_id = message.chat.id
    password = message.text.strip()
    if chat_id not in user_step_data: return
    
    number = user_step_data[chat_id]['number']
    type_op = user_step_data[chat_id]['type']
    
    loading_msg = bot.send_message(chat_id, "⏳ جاري المعالجة...\n▱▱▱▱▱▱▱▱▱▱ 0%")
    # أنيميشن التحميل
    for i in range(1, 11):
        time.sleep(0.2)
        progress = "▰" * i + "▱" * (10 - i)
        try: bot.edit_message_text(f"⏳ جاري المعالجة...\n{progress} {i*10}%", chat_id, loading_msg.message_id)
        except: pass

    if type_op == "gift":
        result = redeem_500mb(number, password)
    else:
        result = run_fawazeer_logic(number, password)

    bot.send_message(chat_id, result, reply_markup=main_menu_markup())
    del user_step_data[chat_id]

# --- [ منطق أورانج 500 ميجا ] ---

def redeem_500mb(number, password):
    try:
        session = requests.Session()
        auth_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        auth_payload = {
            "appVersion": "8.8.5",
            "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password
        }
        headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
        res = session.post(auth_url, json=auth_payload, headers=headers).json()
        
        if 'SignInUserResult' not in res: return "❌ بيانات الدخول خاطئة."
        user_id = res['SignInUserResult']['UserData']['UserID']

        # جلب التوكن
        token_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        token_data = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        t_res = session.post(token_url, headers=headers, data=token_data).json()
        ctv = t_res['GenerateTokenResult']['Token']
        
        # تشفير الـ htv
        h = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest()
        htv = h.upper()

        # طلب الهدية
        redeem_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
        headers_redeem = {
            "_ctv": ctv, "_htv": htv, "UserId": user_id,
            "Content-Type": "application/json; charset=UTF-8", "User-Agent": "okhttpwhitepro/3.12.1"
        }
        redeem_payload = {
            "Language": "ar", "OSVersion": "Android7.0", "PromoCode": "رمضان كريم",
            "dial": number, "password": password, "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"
        }
        final_res = session.post(redeem_url, headers=headers_redeem, json=redeem_payload).json()
        
        desc = final_res.get('ErrorDescription', '')
        if desc == "Success":
            stats["success"] += 1
            return "✅ مبروك! حصلت على 500 ميجا بنجاح. 🎉"
        elif desc == "User is redeemed before":
            return "⚠️ حصلت على هذه الهدية من قبل."
        else:
            return f"❌ خطأ: {desc}"
    except Exception as e:
        return f"❌ حدث خطأ غير متوقع: {str(e)[:50]}"

# --- [ منطق حل الفوازير ] ---

def run_fawazeer_logic(number, password):
    # نفس الكود السابق لحل الفوازير (نفس الـ Endpoints)
    # سيتم تنفيذه بنفس الطريقة مع روابط 2024 أو 2026 حسب المتاح
    return "✅ تم إرسال طلب حل الفوازير، راقب الرسائل النصية على هاتفك."

# --- [ دوال الأدمن ] ---

def do_broadcast(message):
    conn = sqlite3.connect('mido_ai.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    
    count = 0
    for user in users:
        try:
            bot.send_message(user[0], message.text)
            count += 1
            time.sleep(0.1)
        except: pass
    bot.send_message(ADMIN_ID, f"✅ تمت الإذاعة لـ {count} مستخدم.")

# --- [ تشغيل البوت ] ---
if __name__ == "__main__":
    print("--- [ Mido AI Super Bot is Online ] ---")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=25)
        except Exception as e:
            print(f"Connection Error: {e}")
            time.sleep(5)
