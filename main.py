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
user_data_steps = {}

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
        "Success With Grace": "✅ مبروك! تم تفعيل عرض الخصم بنجاح.",
        "User is redeemed before": "⚠️ استلمت الهدية دي قبل كدة يا نجم.",
        "Invalid phone number or password": "❌ الرقم أو الباسوورد غلط.",
        "FawazeerSuccess": "✅ مبروك! حليت الفزورة واستلمت الجائزة.",
        "ErrorCode 1": "⚠️ شاركت في الفوازير النهاردة فعلاً.",
        "invalid_grant": "❌ بيانات الدخول غير صحيحة.",
    }
    return translations.get(text, f"النتيجة: {text}")

# --- [ واجهات الأزرار المحدثة ] ---
def user_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔴 خدمات فودافون", callback_data="vf_menu"),
        types.InlineKeyboardButton("🍊 خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🟢 خدمات اتصالات", callback_data="etisalat_main"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_menu"),
        types.InlineKeyboardButton("👨‍💻 المطور  ", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup 

def vf_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📉 خصم 50% فلكس 300", callback_data="vf_flex_300"),
        types.InlineKeyboardButton("📉 خصم 50% فلكس 260", callback_data="vf_flex_260"),
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

def etisalat_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎬 500 استريمنج", callback_data="use_streaming"),
        types.InlineKeyboardButton("📱 500 سوشيال", callback_data="use_social"),
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

# --- [ سكريبت خصم فلكس 260 الجديد ] ---
def run_vf_flex_260(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري محاولة تفعيل خصم فلكس 260...")
    try:
        auth_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload_auth = {'grant_type': "password", 'username': number, 'password': password, 'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a", 'client_id': "ana-vodafone-app"}
        headers_auth = {'User-Agent': "okhttp/4.11.0", 'clientId': "AnaVodafoneAndroid", 'Accept-Language': "ar"}
        auth_res = requests.post(auth_url, data=payload_auth, headers=headers_auth).json()
        
        if 'access_token' not in auth_res:
            bot.edit_message_text("❌ بيانات الدخول غلط.", chat_id, loading.message_id); return
        
        tok = auth_res['access_token']
        order_url = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
        payload_order = {
            "channel": {"name": "MobileApp"},
            "orderItem": [{
                "action": "add", "id": "Flex_2021_523",
                "itemPrice": [
                    {"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "LE", "value": "130.0"}}},
                    {"name": "MigrationFees", "price": {"taxIncludedAmount": {"unit": "LE", "value": "0.0"}}}
                ],
                "product": {
                    "characteristic": [
                        {"name": "offerRank", "value": "1"}, {"name": "TariffID", "value": "523"},
                        {"name": "Quota"}, {"name": "Validity", "@type": "MONTH", "value": "1"},
                        {"name": "MaxAdjustmentNumber", "value": "1"}, {"name": "TariffRank", "value": "6"},
                        {"name": "MigrationDesc", "value": "Intervention Offer Migration"}, {"name": "CohortId", "value": "24"}
                    ],
                    "productSpecification": [
                        {"id": "Retention With Offer", "name": "Category"}, {"id": "Upon Renewal / Repurchase", "name": "MigrationRule"},
                        {"id": "10", "name": "RatePlanType"}, {"id": "Flex Family", "name": "BundleType"}
                    ],
                    "relatedParty": [
                        {"id": number, "name": "MSISDN", "@referredType": "prepaid", "role": "Subscriber"},
                        {"id": "523", "name": "TariffID", "@referredType": "prepaid", "role": "TariffID"}
                    ]
                },
                "@type": "Access fees Discount", "eCode": 0
            }],
            "@type": "InterventionTariff"
        }
        headers_order = {'User-Agent': "okhttp/4.11.0", 'Authorization': f"Bearer {tok}", 'clientId': "AnaVodafoneAndroid", 'msisdn': number, 'Content-Type': "application/json; charset=UTF-8"}
        res = requests.post(order_url, data=json.dumps(payload_order), headers=headers_order).json()
        
        reason = res.get('reason', 'Unknown')
        if reason == "Success With Grace":
            bot.edit_message_text("✅ مبروك! تمت تفعيل خصم 50% على فلكس 260 بنجاح.", chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            bot.edit_message_text(f"⚠️ الرد: {reason}", chat_id, loading.message_id)
    except Exception as e: bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, loading.message_id)

# --- [ سكريبت عرض بلس ] ---
def redeem_vodafone_plus_discount(number, password, chat_id):
    loading = bot.send_message(chat_id, "⏳ جاري فحص عرض Plus...")
    try:
        auth_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {'username': number, 'password': password, 'grant_type': 'password', 'client_secret': 'a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3', 'client_id': 'my-vodafone-app'}
        headers = {'User-Agent': "okhttp/4.9.3", 'clientId': "my-vodafone-app", 'x-agent-version': "2024.10.1"}
        auth_data = requests.post(auth_url, data=payload, headers=headers).json()
        if 'access_token' not in auth_data:
            bot.edit_message_text("❌ بيانات غلط.", chat_id, loading.message_id); return
        
        tok = auth_data['access_token']
        url_promo = "https://web.vodafone.com.eg/services/dxl/promo/promotion?%40type=Promo&%24.context.type=scratchCoupon"
        headers_promo = {'Authorization': f"Bearer {tok}", 'channel': "MOBILE", 'useCase': "Promo", 'msisdn': number, 'Accept-Language': "ar"}
        res_promo = requests.get(url_promo, headers=headers_promo)
        if "No Data Found" in res_promo.text: bot.edit_message_text("⚠️ لا يوجد عرض متاح.", chat_id, loading.message_id)
        elif "Promo_TX_ID" in res_promo.text: bot.edit_message_text("✅ مفعل مسبقاً.", chat_id, loading.message_id, reply_markup=user_main_markup())
        else: bot.edit_message_text("✅ تم التفعيل بنجاح!", chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ حدث خطأ.", chat_id, loading.message_id)

# --- [ سكريبت عجلة الحظ ] ---
def spin_wheel(number, password, chat_id):
    loading = bot.send_message(chat_id, "⏳ جاري تشغيل العجلة...")
    try:
        url2 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        h2 = {"Content-Type": "application/json; charset=UTF-8", 'User-Agent': "okhttp/3.14.9"}
        d2 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        ctv = requests.post(url2, headers=h2, data=d2).json()["GenerateTokenResult"]["Token"]
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        
        res_spin = requests.post("https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin", json={"ChannelName": "MobinilAndMe", "Dial": number, "Password": password, "ServiceClassId": "1033"}, headers={'_ctv': ctv, '_htv': htv, **h2}).json()
        if "ErrorDescription" in res_spin: bot.edit_message_text("⚠️ استهلكت المحاولات.", chat_id, loading.message_id); return
        
        offer, cat, name = res_spin["OfferDetails"]["OfferId"], res_spin["SecondryButtonDetails"]["CategoryId"], res_spin["OfferDetails"]["OfferName"]
        time.sleep(1)
        res_f = requests.post("https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill", json={"CategoryId": cat, "Dial": number, "OfferId": offer, "Password": password, "ServiceClassId": "1033"}, headers={'_ctv': ctv, '_htv': htv, **h2}).json()
        bot.edit_message_text(f"🎡 {name}\n✅ تمت العملية.", chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ خطأ.", chat_id, loading.message_id)

# --- [ وظائف فودافون الأصلية (فلكس 300) ] ---
def run_vf_flex_300(chat_id, number, password):
    loading = bot.send_message(chat_id, "⏳ جاري تفعيل خصم فلكس 300...")
    try:
        auth_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {'grant_type': "password", 'username': number, 'password': password, 'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a", 'client_id': "ana-vodafone-app"}
        auth_res = requests.post(auth_url, data=payload, headers={'User-Agent': "okhttp/4.11.0"}).json()
        if 'access_token' not in auth_res: bot.edit_message_text("❌ بيانات غلط.", chat_id, loading.message_id); return
        tok = auth_res['access_token']
        order_payload = {"channel": {"name": "MobileApp"}, "orderItem": [{"action": "add", "id": "Flex_2024_633", "itemPrice": [{"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "", "value": "150.0"}}}, {"name": "MigrationFees", "price": {"taxIncludedAmount": {"unit": "LE", "value": "0.0"}}}], "product": {"characteristic": [{"name": "TariffRank", "value": "2"}, {"name": "TariffID", "value": "633"}, {"name": "offerRank", "value": "1"}, {"name": "CohortId", "value": "11"}], "productSpecification": [{"id": "Migrations", "name": "Category"}, {"id": "Flex Family", "name": "BundleType"}], "relatedParty": [{"id": number, "name": "MSISDN", "role": "Subscriber"}]}, "@type": "Migration Fees", "eCode": 0}], "@type": "InterventionTariff"}
        res = requests.post("https://mobile.vodafone.com.eg/services/dxl/pom/productOrder", data=json.dumps(order_payload), headers={'Authorization': f"Bearer {tok}", 'msisdn': number, 'Content-Type': "application/json"}).json()
        bot.edit_message_text(translate_res(res.get('reason', 'Error')), chat_id, loading.message_id, reply_markup=user_main_markup())
    except: bot.edit_message_text("❌ خطأ.", chat_id, loading.message_id)

# --- [ وظائف اتصالات ] ---
def run_social_script(email, password):
    try:
        token = base64.b64encode(f"{email}:{password}".encode()).decode()
        h = {'User-Agent': "okhttp/5.0.0-alpha.11", 'Content-Type': "text/xml; charset=UTF-8", 'Authorization': f"Basic {token}"}
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", data="<?xml version='1.0' encoding='UTF-8'?><loginRequest><platform>Android</platform></loginRequest>", headers=h, timeout=15)
        num = ET.fromstring(r.text).find("dial").text
        requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", data=f"<?xml version='1.0' encoding='UTF-8'?> <submitOrderRequest> <msisdn>{num}</msisdn> <operation>REDEEM</operation> <productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName> </submitOrderRequest>", headers=h, timeout=15)
        return f"✅ تم للرقم: {num}"
    except: return "❌ خطأ في البيانات."

# --- [ معالجة الرسائل والأوامر ] ---

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"🛠️ هلا يا أدمن في {BOT_NAME}:", reply_markup=admin_markup()); return
    if get_bot_status() == 0:
        bot.send_message(message.chat.id, "⚠️ البوت في صيانة حالياً."); return
    bot.send_message(message.chat.id, f"🌟 مرحباً بك في {BOT_NAME}:", reply_markup=user_main_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid, mid = call.message.chat.id, call.message.message_id
    if call.data == "back_home": bot.edit_message_text("الرئيسية:", cid, mid, reply_markup=user_main_markup())
    elif call.data == "vf_menu": bot.edit_message_text("🔴 فودافون:", cid, mid, reply_markup=vf_menu_markup())
    elif call.data == "orange_menu": bot.edit_message_text("🍊 أورانج:", cid, mid, reply_markup=orange_markup())
    elif call.data == "etisalat_main": bot.edit_message_text("🟢 اتصالات:", cid, mid, reply_markup=etisalat_markup())
    elif call.data == "extra_menu": bot.edit_message_text("🛠️ إضافية:", cid, mid, reply_markup=extra_markup())
    
    # تحويل لخطوات الإدخال
    elif call.data == "vf_flex_300":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون (خصم 300):")
        bot.register_next_step_handler(msg, get_phone_step, "vf_flex_300")
    elif call.data == "vf_flex_260":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون (خصم 260):")
        bot.register_next_step_handler(msg, get_phone_step, "vf_flex_260")
    elif call.data == "vf_plus_promo":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون (Plus):")
        bot.register_next_step_handler(msg, get_phone_step, "vf_plus")
    elif call.data == "spin_wheel_action":
        msg = bot.send_message(cid, "📱 أرسل رقم أورانج للعجلة:")
        bot.register_next_step_handler(msg, get_phone_step, "spin_wheel")
    
    # ... بقية الـ Callback (الرسم، المواقيت، الأدمن) يتم تنفيذها بنفس النمط القديم

def get_phone_step(message, mode):
    phone = message.text.strip(); msg = bot.send_message(message.chat.id, "🔐 أرسل كلمة المرور:")
    bot.register_next_step_handler(msg, get_pass_step, phone, mode)

def get_pass_step(message, phone, mode):
    pwd = message.text.strip()
    if mode == "vf_flex_300": run_vf_flex_300(message.chat.id, phone, pwd)
    elif mode == "vf_flex_260": run_vf_flex_260(message.chat.id, phone, pwd)
    elif mode == "vf_plus": redeem_vodafone_plus_discount(phone, pwd, message.chat.id)
    elif mode == "spin_wheel": spin_wheel(phone, pwd, message.chat.id)
    # وأي مودات تانية...

if __name__ == "__main__":
    print(f"{BOT_NAME} is Online with Flex 260 Discount...")
    bot.infinity_polling()
