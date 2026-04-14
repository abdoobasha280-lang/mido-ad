import telebot
import requests
import json
import sqlite3
import hashlib
import urllib.parse
import random
import time
import os
import base64
import xml.etree.ElementTree as ET
from telebot import types 

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk' 
ADMIN_ID = 7721807760             
DEV_USER = '@AMI_EG'              
BOT_NAME = "Mido AI"
bot = telebot.TeleBot(API_TOKEN) 

stats = {"success": 0, "failed": 0}
user_data_steps = {} # لتخزين خطوات الإدخال

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
        "invalid_grant": "❌ بيانات الدخول (الرقم أو الباسوورد) غير صيحة.",
    }
    return translations.get(text, f"النتيجة: {text}")

# --- [ واجهات الأزرار ] ---
def user_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔴 خدمات فودافون", callback_data="vf_menu"),
        types.InlineKeyboardButton("🍊 خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🟢 خدمات اتصالات", callback_data="etisalat_main"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_menu"),
        types.InlineKeyboardButton("👨‍💻 المطور يا أخويا", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup 

def etisalat_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎬 500 استريمنج", callback_data="use_streaming"),
        types.InlineKeyboardButton("📱 500 سوشيال", callback_data="use_social"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_home")
    )
    return markup

def vf_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📉 خصم 50% فلكس 300", callback_data="vf_flex_50"),
        types.InlineKeyboardButton("🎁 عرض Vodafone Plus", callback_data="vf_plus_promo"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_home")
    )
    return markup

def orange_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💰 معرفة الرصيد", callback_data="check_balance"),
        types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="get_500mb"),
        types.InlineKeyboardButton("🧩 حل الفوازير", callback_data="solve_fawazeer"),
        types.InlineKeyboardButton("🎡 عجلة الحظ", callback_data="spin_wheel_action"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="back_home")
    )
    return markup

def extra_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_show"),
        types.InlineKeyboardButton("🎨 رسم صورة Nano Banana", callback_data="draw_ai"),
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

# --- [ سكريبت عرض فودافون بلس الجديد ] ---
def redeem_vodafone_plus_discount(number, password, chat_id):
    loading = bot.send_message(chat_id, "⏳ جاري فحص وتفعيل عرض Vodafone Plus...")
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
            'username': number,
            'password': password,
            'grant_type': 'password',
            'client_secret': 'a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3',
            'client_id': 'my-vodafone-app'
        }
        headers = {
            'User-Agent': "okhttp/4.9.3",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip",
            'x-agent-operatingsystem': "android",
            'clientId': "my-vodafone-app",
            'x-agent-version': "2024.10.1"
        }

        response = requests.post(url, data=payload, headers=headers)
        auth_data = response.json()

        if 'access_token' not in auth_data:
            bot.edit_message_text("❌ فشل تسجيل الدخول. يرجى التحقق من الرقم أو كلمة المرور.", chat_id, loading.message_id)
            return

        tok = auth_data['access_token']
        url_promo = "https://web.vodafone.com.eg/services/dxl/promo/promotion?%40type=Promo&%24.context.type=scratchCoupon"
        
        headers_promo = headers.copy()
        headers_promo['Authorization'] = f"Bearer {tok}"
        headers_promo['channel'] = "MOBILE"
        headers_promo['useCase'] = "Promo"
        headers_promo['Content-Type'] = "application/json"
        headers_promo['msisdn'] = number
        headers_promo['Accept-Language'] = "ar"

        response_promo = requests.get(url_promo, headers=headers_promo)

        if "No Data Found" in response_promo.text:
            bot.edit_message_text("⚠️ لا يوجد عرض متاح لك حاليًا.", chat_id, loading.message_id)
        elif "Promo_TX_ID" in response_promo.text:
            bot.edit_message_text("✅ تم تفعيل العرض مسبقًا.", chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            bot.edit_message_text("✅ تم تفعيل العرض بنجاح!", chat_id, loading.message_id, reply_markup=user_main_markup())
            
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", chat_id, loading.message_id)

# --- [ سكريبت عجلة حظ أورانج ] ---
def spin_wheel(number, password, chat_id):
    loading = bot.send_message(chat_id, "⏳ جاري تشغيل عجلة الحظ...")
    try:
        url2 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        headers2 = {"Content-Type": "application/json; charset=UTF-8", 'Accept-Encoding': "gzip", 'User-Agent': "okhttp/3.14.9"}
        data2 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        response = requests.post(url2, headers=headers2, data=data2).json()
        ctv = response["GenerateTokenResult"]["Token"]
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin"
        payload = json.dumps({"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "en", "Password": password, "ServiceClassId": "1033"})
        headers = {'User-Agent': "okhttp/3.14.9", '_ctv': ctv, '_htv': htv, 'Content-Type': "application/json; charset=UTF-8"}
        res_spin = requests.post(url, data=payload, headers=headers).json()
        
        if "ErrorDescription" in res_spin:
            bot.edit_message_text("⚠️ لقد استهلكت المحاولات الثلاث اليومية لعجلة الحظ", chat_id, loading.message_id); return
        
        offer = res_spin["OfferDetails"]["OfferId"]
        CategoryId = res_spin["SecondryButtonDetails"]["CategoryId"]
        offer_name = res_spin["OfferDetails"]["OfferName"]

        time.sleep(2)
        response_new = requests.post(url2, headers=headers2, data=data2).json()
        ctv_n = response_new["GenerateTokenResult"]["Token"]
        htv_n = hashlib.sha256((ctv_n + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        url_f = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
        payload_f = json.dumps({"CategoryId": CategoryId, "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "en", "OfferId": offer, "Password": password, "ServiceClassId": "1033"})
        headers_n = headers.copy(); headers_n['_ctv'] = ctv_n; headers_n['_htv'] = htv_n
        res_f = requests.post(url_f, data=payload_f, headers=headers_n).json()
        
        msg_res = f"🎡 عجلة الحظ:\n{offer_name}\n"
        msg_res += "⚠️ أنت مشترك بالفعل" if "Already opted in" in str(res_f) else "✅ تم الاشتراك بنجاح"
        bot.edit_message_text(msg_res, chat_id, loading.message_id, reply_markup=user_main_markup())
    except Exception as e: bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, loading.message_id)

# --- [ سكريبتات اتصالات ] ---
def run_social_script(email, password):
    try:
        token = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {'User-Agent': "okhttp/5.0.0-alpha.11", 'Content-Type': "text/xml; charset=UTF-8", 'Authorization': f"Basic {token}"}
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", data="<?xml version='1.0' encoding='UTF-8'?><loginRequest><platform>Android</platform></loginRequest>", headers=headers, timeout=15)
        number = ET.fromstring(r.text).find("dial").text
        requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", data=f"<?xml version='1.0' encoding='UTF-8'?> <submitOrderRequest> <msisdn>{number}</msisdn> <operation>REDEEM</operation> <productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName> </submitOrderRequest>", headers=headers, timeout=15)
        return f"✅ تم بنجاح!\n📱 الرقم: {number}"
    except: return "❌ حصل خطأ، تأكد من البيانات"

def run_streaming_script(email, password):
    try:
        token = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {'User-Agent': "okhttp/5.0.0-alpha.11", 'Content-Type': "text/xml; charset=UTF-8", 'Authorization': f"Basic {token}"}
        res = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", data="<?xml version='1.0' encoding='UTF-8'?><loginRequest><platform>Android</platform></loginRequest>", headers=headers, timeout=15)
        if res.status_code == 200:
            number = ET.fromstring(res.text).find("dial").text
            requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", data=f"<?xml version='1.0' encoding='UTF-8'?> <submitOrderRequest> <msisdn>{number}</msisdn> <operation>REDEEM</operation> <productName>DOWNLOAD_GIFT_2_STREAMING_UNITS</productName> </submitOrderRequest>", headers=headers, timeout=15)
            return f"✅ تم بنجاح!\n📱 الرقم: {number}"
        return "❌ خطأ في البيانات"
    except: return "❌ حدث خطأ"

# --- [ وظائف فودافون الأصلية ] ---
def run_vf_flex(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري محاولة تفعيل عرض الـ 50%...")
    try:
        auth_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {'grant_type': "password", 'username': number, 'password': password, 'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a", 'client_id': "ana-vodafone-app"}
        headers_auth = {'User-Agent': "okhttp/4.11.0", 'clientId': "AnaVodafoneAndroid", 'Accept-Language': "ar"}
        auth_res = requests.post(auth_url, data=payload, headers=headers_auth).json()
        if 'access_token' not in auth_res:
            bot.edit_message_text(translate_res(auth_res.get('error', 'invalid_grant')), chat_id, loading.message_id); return
        tok = auth_res['access_token']
        order_payload = {"channel": {"name": "MobileApp"}, "orderItem": [{"action": "add", "id": "Flex_2024_633", "itemPrice": [{"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "", "value": "150.0"}}}, {"name": "MigrationFees", "price": {"taxIncludedAmount": {"unit": "LE", "value": "0.0"}}}], "product": {"characteristic": [{"name": "TariffRank", "value": "2"}, {"name": "TariffID", "value": "633"}, {"name": "offerRank", "value": "1"}, {"name": "MigrationDesc", "value": "Intervention Offer Migration"}, {"name": "CohortId", "value": "11"}], "productSpecification": [{"id": "Migrations", "name": "Category"}, {"id": "Flex Family", "name": "BundleType"}], "relatedParty": [{"id": number, "name": "MSISDN", "role": "Subscriber"}]}, "@type": "Migration Fees", "eCode": 0}], "@type": "InterventionTariff"}
        order_headers = {'User-Agent': "okhttp/4.11.0", 'Authorization': f"Bearer {tok}", 'clientId': "AnaVodafoneAndroid", 'msisdn': number, 'Content-Type': "application/json; charset=UTF-8"}
        order_res = requests.post("https://mobile.vodafone.com.eg/services/dxl/pom/productOrder", data=json.dumps(order_payload), headers=order_headers).json()
        reason = order_res.get('reason', 'Unknown Error')
        if reason == "Success With Grace":
            stats["success"] += 1
            bot.edit_message_text(translate_res(reason), chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            stats["failed"] += 1
            bot.edit_message_text(f"❌ الرد: {reason}", chat_id, loading.message_id)
    except Exception as e: bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, loading.message_id)

# --- [ وظائف أورانج الأصلية ] ---
def check_orange_balance(chat_id, phone):
    loading = bot.send_message(chat_id, "⏳ جاري الاستعلام...")
    try:
        res = requests.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", headers={"lang": "en"}, json={"IsForAnotherRecipient": True, "RecipientDial": phone, "Dial": phone}, timeout=15).json()
        if 'CreditBalance' in res:
            bot.edit_message_text(f"💰 رصيد الرقم {phone} هو: {res['CreditBalance']} جنيه.", chat_id, loading.message_id, reply_markup=orange_markup())
        else: bot.edit_message_text("❌ لم يتم جلب الرصيد.", chat_id, loading.message_id)
    except: bot.edit_message_text("❌ خطأ في الاتصال.", chat_id, loading.message_id)

def run_fawazeer(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري حل فوازير أورانج...")
    try:
        session = requests.Session(); h = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json"}
        auth = session.post("https://services.orange.eg/SignIn.svc/SignInUser", json={"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "password": password}, headers=h).json()
        token = session.post("https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate", json={"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Password": password}, headers={'Token': auth['SignInUserResult']['AccessToken'], **h}).json()['Token']
        qs = session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions", json={"Dial": number, "Token": token}, headers=h).json()
        ans = [{"QuestionId": q["Answers"][0]["QuestionId"], "AnswerId": next(a["Id"] for a in q["Answers"] if a["IsCorrect"])} for q in qs.get("Questions", [])]
        res = session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit", json={"Dial": number, "Token": token, "Answers": ans}, headers=h).json()
        bot.edit_message_text(translate_res(res.get('ErrorDescription', '')), chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ فشلت العملية.", chat_id, loading.message_id)

def run_500mb(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري طلب هدية الـ 500 ميجا...")
    try:
        session = requests.Session(); h = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json"}
        login = session.post("https://services.orange.eg/SignIn.svc/SignInUser", json={"appVersion": "8.8.5", "dialNumber": number, "password": password, "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}}, headers=h).json()
        uid = login['SignInUserResult']['UserData']['UserID']
        ctv = session.post("https://services.orange.eg/GetToken.svc/GenerateToken", json={"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}, headers=h).json()['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        res = session.post("https://services.orange.eg/APIs/Promotions/api/CAF/Redeem", headers={"_ctv": ctv, "_htv": htv, "UserId": uid, **h}, json={"PromoCode": "رمضان كريم", "dial": number, "password": password, "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"}).json()
        bot.edit_message_text(translate_res(res.get('ErrorDescription', '')), chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ حدث خطأ.", chat_id, loading.message_id)

# --- [ وظيفة الرسم Nano Banana ] ---
def process_draw(message):
    prompt = message.text; msg = bot.reply_to(message, "🎨 **جاري الرسم...**")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={random.randint(1,1000000)}&width=1024&height=1024&model=extra-realism&nologo=true"
        bot.send_photo(message.chat.id, url, caption=f"✨ **Nano Banana**", reply_markup=user_main_markup())
        bot.delete_message(message.chat.id, msg.message_id)
    except: bot.edit_message_text("السيرفر مضغوط.", message.chat.id, msg.message_id)

# --- [ معالجة الرسائل والأوامر ] ---

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ لوحة الأدمن:", reply_markup=admin_markup())
        return
    if get_bot_status() == 0:
        bot.send_message(message.chat.id, "⚠️ صيانة.")
        return 
    bot.send_message(message.chat.id, f"🌟 أهلاً بك في {BOT_NAME}:", reply_markup=user_main_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid, mid = call.message.chat.id, call.message.message_id
    if call.data == "back_home":
        bot.edit_message_text("القائمة الرئيسية:", cid, mid, reply_markup=user_main_markup())
    elif call.data == "etisalat_main":
        bot.edit_message_text("🟢 خدمات اتصالات:", cid, mid, reply_markup=etisalat_markup())
    elif call.data == "vf_menu":
        bot.edit_message_text("🔴 خدمات فودافون:", cid, mid, reply_markup=vf_menu_markup())
    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج:", cid, mid, reply_markup=orange_markup())
    elif call.data == "extra_menu":
        bot.edit_message_text("🛠️ خدمات إضافية:", cid, mid, reply_markup=extra_markup())
    elif call.data == "use_streaming":
        user_data_steps[cid] = {"step": "email", "type": "streaming"}
        bot.send_message(cid, "📧 ابعت الإيميل (اتصالات):")
    elif call.data == "use_social":
        user_data_steps[cid] = {"step": "email", "type": "social"}
        bot.send_message(cid, "📧 ابعت الإيميل (اتصالات):")
    elif call.data == "spin_wheel_action":
        msg = bot.send_message(cid, "📱 أرسل رقم أورانج للعجلة:")
        bot.register_next_step_handler(msg, get_phone_step, "spin_wheel")
    elif call.data == "vf_flex_50":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون (خصم 50%):")
        bot.register_next_step_handler(msg, get_phone_step, "vf_flex")
    elif call.data == "vf_plus_promo":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون (عرض Plus):")
        bot.register_next_step_handler(msg, get_phone_step, "vf_plus")
    elif call.data == "check_balance":
        msg = bot.send_message(cid, "💰 أرسل رقم أورانج للاستعلام:")
        bot.register_next_step_handler(msg, lambda m: check_orange_balance(cid, m.text.strip()))
    elif call.data == "prayer_show":
        try:
            d = requests.get("http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5").json()['data']['timings']
            res = f"🕌 مواقيت (القاهرة):\n\nالفجر: {d['Fajr']}\nالظهر: {d['Dhuhr']}\nالعصر: {d['Asr']}\nالمغرب: {d['Maghrib']}\nالعشاء: {d['Isha']}"
            bot.edit_message_text(res, cid, mid, reply_markup=extra_markup())
        except: bot.answer_callback_query(call.id, "خطأ في جلب المواقيت.")
    elif call.data == "draw_ai":
        msg = bot.send_message(cid, "🎨 أرسل الوصف بالإنجليزي:")
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
        msg = bot.send_message(cid, "📣 أرسل الإذاعة:")
        bot.register_next_step_handler(msg, do_broadcast)

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    cid = message.chat.id
    if cid in user_data_steps:
        s = user_data_steps[cid]
        if s.get("step") == "email":
            s["email"] = message.text.strip(); s["step"] = "password"
            bot.reply_to(message, "🔑 ابعت الباسورد:")
        elif s.get("step") == "password":
            p = message.text.strip(); m = bot.reply_to(message, "⏳ جاري...")
            res = run_social_script(s["email"], p) if s["type"] == "social" else run_streaming_script(s["email"], p)
            bot.edit_message_text(res, cid, m.message_id, reply_markup=user_main_markup())
            user_data_steps.pop(cid)

def get_phone_step(message, mode):
    p = message.text.strip(); msg = bot.send_message(message.chat.id, "🔐 أرسل كلمة المرور:")
    bot.register_next_step_handler(msg, get_pass_step, p, mode)

def get_pass_step(message, phone, mode):
    pwd = message.text.strip()
    if mode == "vf_flex": run_vf_flex(message.chat.id, phone, pwd)
    elif mode == "vf_plus": redeem_vodafone_plus_discount(phone, pwd, message.chat.id)
    elif mode == "get_500mb": run_500mb(message.chat.id, phone, pwd)
    elif mode == "spin_wheel": spin_wheel(phone, pwd, message.chat.id)
    else: run_fawazeer(message.chat.id, phone, pwd)

def do_broadcast(message):
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    c.execute('SELECT user_id FROM users'); users = c.fetchall(); conn.close()
    for u in users:
        try: bot.send_message(u[0], message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ تم.")

if __name__ == "__main__":
    print(f"{BOT_NAME} is Online with VF Plus Support...")
    bot.infinity_polling()
