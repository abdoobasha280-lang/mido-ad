import telebot
import requests
import json
import sqlite3
import hashlib
import urllib.parse
import random
import time
from telebot import types 

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk' 
ADMIN_ID = 7721807760             
DEV_USER = '@AMI_EG'              
BOT_NAME = "Mido AI"
bot = telebot.TeleBot(API_TOKEN) 

stats = {"success": 0, "failed": 0}

# --- [ قاعدة البيانات ] ---
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

# --- [ دالة تعريب الردود ] ---
def translate_res(text):
    translations = {
        "Success": "✅ تمت العملية بنجاح!",
        "Success With Grace": "✅ مبروك! تم تفعيل عرض خصم 50% على فلكس بنجاح.",
        "User is redeemed before": "⚠️ استلمت الهدية دي قبل كدة يا نجم.",
        "Invalid phone number or password": "❌ الرقم أو الباسوورد غلط.",
        "FawazeerSuccess": "✅ مبروك! حليت الفزورة واستلمت الجائزة.",
        "ErrorCode 1": "⚠️ شاركت في الفوازير النهاردة فعلاً.",
        "invalid_grant": "❌ بيانات الدخول (الرقم أو الباسوورد) غير صحيحة.",
    }
    return translations.get(text, f"النتيجة: {text}")

# --- [ واجهات الأزرار ] ---
def user_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔴 خدمات فودافون", callback_data="vf_menu"),
        types.InlineKeyboardButton("🍊 خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_menu"),
        types.InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup 

def vf_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📉 خصم 50% فلكس 300", callback_data="vf_flex_50"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_home")
    )
    return markup

def orange_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💰 معرفة الرصيد", callback_data="check_balance"),
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
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users'); count = c.fetchone()[0]; conn.close()
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 البوت شغال" if get_bot_status() == 1 else "🔴 البوت متوقف"
    markup.add(
        types.InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="none"),
        types.InlineKeyboardButton(f"✅ نجاح: {stats['success']} | ❌ فشل: {stats['failed']}", callback_data="none"),
        types.InlineKeyboardButton(status_text, callback_data="toggle_status"),
        types.InlineKeyboardButton("📣 إذاعة رسالة", callback_data="broadcast"),
        types.InlineKeyboardButton("🚀 تشغيل البوت لنفسي", callback_data="back_home")
    )
    return markup 

# --- [ منطق فودافون (كودك الأصلي) ] ---
def run_vf_flex(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري محاولة تفعيل العرض...")
    try:
        # Step 1: Login
        auth_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
          'grant_type': "password",
          'username': number,
          'password': password,
          'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a",
          'client_id': "ana-vodafone-app"
        }
        headers_auth = {
          'User-Agent': "okhttp/4.11.0",
          'clientId': "AnaVodafoneAndroid",
          'Accept-Language': "ar"
        }
        auth_res = requests.post(auth_url, data=payload, headers=headers_auth).json()
        
        if 'access_token' not in auth_res:
            bot.edit_message_text(translate_res(auth_res.get('error', 'invalid_grant')), chat_id, loading.message_id)
            return

        tok = auth_res['access_token']

        # Step 2: Order Migration
        order_url = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
        order_payload = {
          "channel": {"name": "MobileApp"},
          "orderItem": [{
            "action": "add",
            "id": "Flex_2024_633",
            "itemPrice": [
              {"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "", "value": "150.0"}}},
              {"name": "MigrationFees", "price": {"taxIncludedAmount": {"unit": "LE", "value": "0.0"}}}
            ],
            "product": {
              "characteristic": [
                {"name": "TariffRank", "value": "2"},
                {"name": "TariffID", "value": "633"},
                {"name": "Quota"}, {"name": "Validity"},
                {"name": "MaxAdjustmentNumber", "value": ""},
                {"name": "offerRank", "value": "1"},
                {"name": "MigrationDesc", "value": "Intervention Offer Migration"},
                {"name": "CohortId", "value": "11"}
              ],
              "productSpecification": [
                {"id": "Migrations", "name": "Category"},
                {"id": "Upon Migration", "name": "MigrationRule"},
                {"id": "0", "name": "RatePlanType"},
                {"id": "Flex Family", "name": "BundleType"}
              ],
              "relatedParty": [
                {"id": number, "name": "MSISDN", "@referredType": "prepaid", "role": "Subscriber"},
                {"id": "470", "name": "TariffID", "@referredType": "prepaid", "role": "TariffID"}
              ]
            },
            "@type": "Migration Fees",
            "eCode": 0
          }],
          "@type": "InterventionTariff"
        }

        order_headers = {
          'User-Agent': "okhttp/4.11.0",
          'Authorization': f"Bearer {tok}",
          'clientId': "AnaVodafoneAndroid",
          'msisdn': number,
          'Content-Type': "application/json; charset=UTF-8"
        }

        order_res = requests.post(order_url, data=json.dumps(order_payload), headers=order_headers).json()
        reason = order_res.get('reason', 'Unknown Error')
        
        if reason == "Success With Grace":
            stats["success"] += 1
            bot.edit_message_text(translate_res(reason), chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            stats["failed"] += 1
            bot.edit_message_text(f"❌ لم يتم التفعيل: {reason}", chat_id, loading.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ تقني: {str(e)}", chat_id, loading.message_id)

# --- [ وظيفة معرفة الرصيد (أورانج) ] ---
def check_orange_balance(chat_id, phone):
    loading = bot.send_message(chat_id, "⏳ جاري الاستعلام...")
    url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
    data = {"SelectedUserDial": None, "IsForAnotherRecipient": True, "RecipientDial": phone, "Dial": phone}
    try:
        res = requests.post(url, headers={"lang": "en"}, json=data, timeout=15).json()
        if 'CreditBalance' in res:
            bot.edit_message_text(f"💰 رصيدك في أورانج هو: {res['CreditBalance']} جنيه.", chat_id, loading.message_id, reply_markup=orange_markup())
        else:
            bot.edit_message_text("❌ لم يتم العثور على بيانات لهذا الرقم.", chat_id, loading.message_id)
    except: bot.edit_message_text("❌ خطأ في الاتصال بالسيرفر.", chat_id, loading.message_id)

# --- [ وظائف أورانج الأصلية ] ---
def run_fawazeer(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري حل الفوازير...")
    try:
        session = requests.Session()
        headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json"}
        auth_res = session.post("https://services.orange.eg/SignIn.svc/SignInUser", json={"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}, headers=headers).json()
        acc_token = auth_res['SignInUserResult']['AccessToken']
        headers['Token'] = acc_token
        token_res = session.post("https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate", json={"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}, headers=headers).json()
        token = token_res.get("Token")
        q_data = session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions", json={"Dial": number, "Language": "ar", "Token": token}, headers=headers).json() 
        answers = [{"QuestionId": q["Answers"][0]["QuestionId"], "AnswerId": next(a["Id"] for a in q["Answers"] if a["IsCorrect"])} for q in q_data.get("Questions", [])]
        submit_res = session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit", json={"Dial": number, "Language": "ar", "Token": token, "Answers": answers}, headers=headers).json() 
        bot.edit_message_text(translate_res(submit_res.get('ErrorDescription', '')), chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ حدث خطأ.", chat_id, loading.message_id)

def run_500mb(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري طلب الهدية...")
    try:
        session = requests.Session()
        headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json"}
        login_res = session.post("https://services.orange.eg/SignIn.svc/SignInUser", json={"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}, headers=headers).json()
        user_id = login_res['SignInUserResult']['UserData']['UserID']
        token_res = session.post("https://services.orange.eg/GetToken.svc/GenerateToken", data='{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}', headers={"Content-Type": "application/json"}).json()
        ctv = token_res['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        res4 = session.post("https://services.orange.eg/APIs/Promotions/api/CAF/Redeem", headers={"_ctv": ctv, "_htv": htv, "UserId": user_id, "Content-Type": "application/json"}, json={"Language": "ar", "PromoCode": "رمضان كريم", "dial": number, "password": password, "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"}).json()
        bot.edit_message_text(translate_res(res4.get('ErrorDescription', '')), chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ حدث خطأ.", chat_id, loading.message_id)

# --- [ معالجة الأحداث ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ لوحة الأدمن:", reply_markup=admin_markup())
        return
    if get_bot_status() == 0:
        bot.send_message(message.chat.id, "⚠️ الصيانة جارية...")
        return 
    bot.send_message(message.chat.id, f"🌟 أهلاً بك في {BOT_NAME}\nاختر شركتك أو خدمتك:", reply_markup=user_main_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid, mid = call.message.chat.id, call.message.message_id
    if call.data == "back_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, mid, reply_markup=user_main_markup())
    elif call.data == "vf_menu":
        bot.edit_message_text("🔴 خدمات فودافون:", cid, mid, reply_markup=vf_menu_markup())
    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج:", cid, mid, reply_markup=orange_markup())
    elif call.data == "extra_menu":
        bot.edit_message_text("🛠️ خدمات إضافية:", cid, mid, reply_markup=extra_markup())
    elif call.data == "vf_flex_50":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون:")
        bot.register_next_step_handler(msg, get_phone_step, "vf_flex")
    elif call.data == "check_balance":
        msg = bot.send_message(cid, "💰 أرسل رقم أورانج:")
        bot.register_next_step_handler(msg, lambda m: check_orange_balance(cid, m.text.strip()))
    elif call.data == "prayer_show":
        try:
            d = requests.get("http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5").json()['data']['timings']
            res = f"🕌 مواقيت الصلاة:\nالفجر: {d['Fajr']}\nالظهر: {d['Dhuhr']}\nالعصر: {d['Asr']}\nالمغرب: {d['Maghrib']}\nالعشاء: {d['Isha']}"
            bot.edit_message_text(res, cid, mid, reply_markup=extra_markup())
        except: bot.answer_callback_query(call.id, "خطأ في السيرفر.")
    elif call.data == "draw_ai":
        msg = bot.send_message(cid, "🎨 أرسل وصف الصورة (إنجليزي):")
        bot.register_next_step_handler(msg, process_draw)
    elif call.data in ["get_500mb", "solve_fawazeer"]:
        msg = bot.send_message(cid, "📱 أرسل رقم أورانج:")
        bot.register_next_step_handler(msg, get_phone_step, call.data)
    elif call.data == "toggle_status" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        new_s = 0 if get_bot_status() == 1 else 1
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
    if mode == "vf_flex": run_vf_flex(message.chat.id, phone, pwd)
    elif mode == "get_500mb": run_500mb(message.chat.id, phone, pwd)
    else: run_fawazeer(message.chat.id, phone, pwd)

def process_draw(message):
    prompt = message.text
    bot.reply_to(message, "⏳ جاري الرسم...")
    try:
        url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={random.randint(1,999)}&model=flux"
        bot.send_photo(message.chat.id, url, caption=f"✨ تم الرسم بواسطة {BOT_NAME}", reply_markup=user_main_markup())
    except: bot.send_message(message.chat.id, "❌ السيرفر مشغول.")

def do_broadcast(message):
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    c.execute('SELECT user_id FROM users'); users = c.fetchall(); conn.close()
    for u in users:
        try: bot.send_message(u[0], message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ تم الإرسال.")

if __name__ == "__main__":
    bot.infinity_polling()
