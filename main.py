import telebot
import requests
import json
import sqlite3
import time
from telebot import types 

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk' 
ADMIN_ID = 7721807760             
DEV_USER = '@AMI_EG'              
bot = telebot.TeleBot(API_TOKEN) 

stats = {"success": 0, "failed": 0}

# --- [ إعداد قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

init_db()

# --- [ الكيبوردات ] ---
def user_main_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("المطور 👨‍💻", url=f"https://t.me/{DEV_USER[1:]}"))
    return markup 

def admin_markup():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="count"),
        types.InlineKeyboardButton(f"✅ نجاح: {stats['success']} | ❌ فشل: {stats['failed']}", callback_data="stats"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast"),
        types.InlineKeyboardButton("🚀 تجربة التفعيل", callback_data="start_use")
    )
    return markup 

def get_bot_status():
    try:
        conn = sqlite3.connect('users.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT status FROM settings')
        res = c.fetchone()
        conn.close()
        return res[0] if res else 1
    except: return 1

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً بك يا أدمن في لوحة التحكم:", reply_markup=admin_markup())
        return

    if get_bot_status() == 0:
        bot.send_message(message.chat.id, "⚠️ البوت حالياً في وضع الصيانة.", reply_markup=user_main_markup())
        return 

    msg = bot.send_message(message.chat.id, "✅ أهلاً بك!\n\nأرسل الآن **رقم الهاتف** الخاص بك:", reply_markup=user_main_markup(), parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_phone)

# --- [ استقبال البيانات ] ---
def get_phone(message):
    if not message.text: return
    phone = message.text
    msg = bot.send_message(message.chat.id, f"الرقم: `{phone}`\nأرسل الآن **كلمة السر**:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_password, phone)

def get_password(message, phone):
    if not message.text: return
    password = message.text
    run_orange_process(message.chat.id, phone.strip(), password.strip())

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "start_use":
        msg = bot.send_message(call.message.chat.id, "أرسل **رقم الهاتف** للبدء:")
        bot.register_next_step_handler(msg, get_phone)
            
    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('users.db', check_same_thread=False)
        c = conn.cursor()
        new_status = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_status,))
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_markup())
        bot.answer_callback_query(call.id, "تم تغيير الحالة.")

    elif call.data == "broadcast" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(call.message.chat.id, "أرسل الرسالة للإذاعة:")
        bot.register_next_step_handler(msg, do_broadcast) 

def do_broadcast(message):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    
    success = 0
    for user in users:
        try:
            bot.send_message(user[0], message.text)
            success += 1
            time.sleep(0.05)
        except: pass
    bot.send_message(ADMIN_ID, f"✅ تمت الإذاعة لـ {success} مستخدم.") 

# --- [ المحرك الأساسي ] ---
def run_orange_process(chat_id, number, password):
    loading_msg = bot.send_message(chat_id, "⏳ جاري فحص الحساب ومحاولة حل الفوازير...")
    session = requests.Session()
    headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"} 

    try:
        # 1. تسجيل الدخول
        auth_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        auth_payload = {
            "appVersion": "9.0.1",
            "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password
        }
        res = session.post(auth_url, json=auth_payload, headers=headers, timeout=15).json()
        
        if 'SignInUserResult' not in res or 'AccessToken' not in res['SignInUserResult']:
            stats["failed"] += 1
            bot.edit_message_text("❌ فشل تسجيل الدخول. تأكد من البيانات.", chat_id, loading_msg.message_id)
            return

        acc_token = res['SignInUserResult']['AccessToken']
        headers['Token'] = acc_token

        # 2. توليد توكن العملية
        gen_url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        gen_payload = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}
        token_res = session.post(gen_url, json=gen_payload, headers=headers, timeout=15).json()
        token = token_res.get("Token")

        # 3. سحب الأسئلة (روابط 2024 قد تكون متوقفة)
        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_data = session.post(q_url, json={"Dial": number, "Language": "ar", "Token": token}, headers=headers, timeout=15).json() 

        if q_data.get('ErrorCode') == 1:
            bot.edit_message_text("❌ لقد شاركت اليوم بالفعل أو العرض متوقف حالياً.", chat_id, loading_msg.message_id)
            return 

        if "Questions" in q_data:
            answers = []
            for q in q_data.get("Questions", []):
                for a in q["Answers"]:
                    if a["IsCorrect"]:
                        answers.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                        break 

            # 4. إرسال الحل
            submit_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
            submit_res = session.post(submit_url, json={"Dial": number, "Language": "ar", "Token": token, "Answers": answers}, headers=headers, timeout=15).json() 

            if submit_res.get('ErrorDescription') == "FawazeerSuccess":
                stats["success"] += 1
                bot.edit_message_text("✅ مبروك! تم حل الفوازير بنجاح.", chat_id, loading_msg.message_id)
            else:
                bot.edit_message_text(f"⚠️ رد النظام: {submit_res.get('ErrorDescription')}", chat_id, loading_msg.message_id)
        else:
            bot.edit_message_text("⚠️ لا توجد فوازير نشطة لهذا الرقم (تأكد من روابط 2026).", chat_id, loading_msg.message_id)

    except Exception as e:
        print(f"DEBUG ERROR: {e}") # الخطأ هيظهر هنا في الكونسول
        stats["failed"] += 1
        bot.edit_message_text(f"❌ حدث خطأ: {str(e)[:50]}...", chat_id, loading_msg.message_id)

print("البوت شغال.. راقب الكونسول لو فيه أخطاء.")
bot.infinity_polling()
