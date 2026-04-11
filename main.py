import telebot
import requests
import json
import sqlite3
import hashlib
import urllib.parse
import random
import time
import os
from telebot import types 

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk' 
ADMIN_ID = 7721807760             
DEV_USER = '@AMI_EG'              
BOT_NAME = "Mido AI"
bot = telebot.TeleBot(API_TOKEN) 

# روابط الـ API الخاصة بك
TEMPORARY_EMAIL_API = "https://zecora0.serv00.net"
TIKTOK_API_URL = "https://tik-batbyte.vercel.app/tiktok?username="

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
        types.InlineKeyboardButton("👨‍💻 المطور يا أخويا", url=f"https://t.me/{DEV_USER[1:]}")
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
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📧 بريد مؤقت عشوائي", callback_data="gen_email"),
        types.InlineKeyboardButton("🔍 فحص محفظة", callback_data="check_wallet"),
        types.InlineKeyboardButton("📱 معلومات تيك توك", callback_data="tiktok_info"),
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_show"),
        types.InlineKeyboardButton("🎨 رسم Nano Banana", callback_data="draw_ai"),
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

# --- [ 1️⃣ وظيفة البريد المؤقت ] ---
def create_random_temp_email(chat_id):
    try:
        response = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=random", timeout=10)
        data = response.json()
        email = data.get('email') if data.get('success') else "خطأ في التوليد"
        bot.send_message(chat_id, f"📥 بريدك المؤقت الجديد:\n`{email}`", parse_mode="Markdown")
    except:
        bot.send_message(chat_id, "❌ السيرفر لا يستجيب")

# --- [ 2️⃣ وظيفة فحص المحفظة ] ---
def process_wallet_check(message):
    number = message.text.strip()
    chat_id = message.chat.id
    bot.send_message(chat_id, "⏳ جاري الفحص...")
    url = "https://fep.kashier.io/v3/orders"
    payload = {
        "apiOperation": "INITIATE_R2P",
        "paymentMethod": {"type": "wallet"},
        "customer": {"mobilePhone": number},
        "order": {"reference": "34d82fe7", "amount": "5", "currency": "EGP"},
        "merchantId": "MID-4934-104"
    }
    headers = {'Content-Type': "application/json", 'Kashier-Hash': "24a66f31d9e032af51f629553f156cfa8477e8952cdafa356a8389cd64051056"}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        result = response.json()
        status = result.get("response", {}).get("status")
        if status == "SUCCESS":
            bot.send_message(chat_id, "✅ الرقم مسجل في محفظة بنجاح.")
        else:
            bot.send_message(chat_id, "❌ الرقم غير مسجل.")
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ: {e}")

# --- [ 3️⃣ وظيفة تيك توك ] ---
def process_tiktok_info(message):
    username = message.text.strip()
    chat_id = message.chat.id
    try:
        response = requests.get(f"{TIKTOK_API_URL}{username}")
        data = response.json()
        if 'error' in data:
            bot.send_message(chat_id, "❌ المستخدم غير موجود.")
            return
        info = f"👤 الاسم: {data.get('nickname')}\n👥 المتابعين: {data.get('followers')}\n❤️ القلوب: {data.get('hearts')}"
        pic = data.get('profile_picture')
        bot.send_photo(chat_id, pic, caption=info)
    except:
        bot.send_message(chat_id, "❌ تعذر جلب البيانات.")

# --- [ وظائف فودافون وأورانج والرسم (الأصلية بدون تغيير) ] ---

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
        order_url = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
        order_payload = {"channel": {"name": "MobileApp"}, "orderItem": [{"action": "add", "id": "Flex_2024_633", "itemPrice": [{"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "", "value": "150.0"}}}, {"name": "MigrationFees", "price": {"taxIncludedAmount": {"unit": "LE", "value": "0.0"}}}], "product": {"characteristic": [{"name": "TariffRank", "value": "2"}, {"name": "TariffID", "value": "633"}, {"name": "Quota"}, {"name": "Validity"}, {"name": "MaxAdjustmentNumber", "value": ""}, {"name": "offerRank", "value": "1"}, {"name": "MigrationDesc", "value": "Intervention Offer Migration"}, {"name": "CohortId", "value": "11"}], "productSpecification": [{"id": "Migrations", "name": "Category"}, {"id": "Upon Migration", "name": "MigrationRule"}, {"id": "0", "name": "RatePlanType"}, {"id": "Flex Family", "name": "BundleType"}], "relatedParty": [{"id": number, "name": "MSISDN", "@referredType": "prepaid", "role": "Subscriber"}, {"id": "470", "name": "TariffID", "@referredType": "prepaid", "role": "TariffID"}]}, "@type": "Migration Fees", "eCode": 0}], "@type": "InterventionTariff"}
        order_headers = {'User-Agent': "okhttp/4.11.0", 'Authorization': f"Bearer {tok}", 'clientId': "AnaVodafoneAndroid", 'msisdn': number, 'Content-Type': "application/json; charset=UTF-8"}
        order_res = requests.post(order_url, data=json.dumps(order_payload), headers=order_headers).json()
        reason = order_res.get('reason', 'Unknown Error')
        if reason == "Success With Grace":
            stats["success"] += 1
            bot.edit_message_text(translate_res(reason), chat_id, loading.message_id, reply_markup=user_main_markup())
        else:
            stats["failed"] += 1
            bot.edit_message_text(f"❌ الرد: {reason}", chat_id, loading.message_id)
    except Exception as e: bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", chat_id, loading.message_id)

def check_orange_balance(chat_id, phone):
    loading = bot.send_message(chat_id, "⏳ جاري الاستعلام...")
    url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
    data = {"SelectedUserDial": None, "IsForAnotherRecipient": True, "RecipientDial": phone, "Dial": phone}
    try:
        res = requests.post(url, headers={"lang": "en"}, json=data, timeout=15).json()
        if 'CreditBalance' in res:
            bot.edit_message_text(f"💰 رصيد الرقم {phone} هو: {res['CreditBalance']} جنيه.", chat_id, loading.message_id, reply_markup=orange_markup())
        else: bot.edit_message_text("❌ عذراً، لم نتمكن من جلب الرصيد.", chat_id, loading.message_id)
    except: bot.edit_message_text("❌ خطأ في الاتصال بالسيرفر.", chat_id, loading.message_id)

def process_draw(message):
    prompt = message.text
    msg = bot.reply_to(message, "🎨 **جاري استخدام Nano Banana لرسم خيالك...**")
    try:
        seed = random.randint(1, 1000000)
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&model=extra-realism&nologo=true"
        bot.send_photo(message.chat.id, image_url, caption=f"✨ **تم التوليد بواسطة Nano Banana**", reply_to_message_id=message.message_id)
        bot.delete_message(message.chat.id, msg.message_id)
    except: bot.edit_message_text("السيرفر مضغوط، جرب تاني.", message.chat.id, msg.message_id)

# --- [ معالجة الرسائل والأوامر ] ---

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ أهلاً بك يا أدمن في لوحتك:", reply_markup=admin_markup())
    elif get_bot_status() == 0:
        bot.send_message(message.chat.id, "⚠️ البوت في حالة صيانة حالياً.")
    else:
        bot.send_message(message.chat.id, "اهلا بك في خدمات MIDO_NET المدمجة 🚀\nاختر الخدمة المطلوبة:", reply_markup=user_main_markup())

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
    elif call.data == "gen_email":
        create_random_temp_email(cid)
    elif call.data == "check_wallet":
        msg = bot.send_message(cid, "ارسل رقم الهاتف المراد فحصه:")
        bot.register_next_step_handler(msg, process_wallet_check)
    elif call.data == "tiktok_info":
        msg = bot.send_message(cid, "ارسل يوزر تيك توك بدون @:")
        bot.register_next_step_handler(msg, process_tiktok_info)
    elif call.data == "vf_flex_50":
        msg = bot.send_message(cid, "📱 أرسل رقم فودافون:")
        bot.register_next_step_handler(msg, get_phone_step, "vf_flex")
    elif call.data == "check_balance":
        msg = bot.send_message(cid, "💰 أرسل رقم أورانج:")
        bot.register_next_step_handler(msg, lambda m: check_orange_balance(cid, m.text.strip()))
    elif call.data == "draw_ai":
        msg = bot.send_message(cid, "🎨 أرسل وصف الصورة بالإنجليزي:")
        bot.register_next_step_handler(msg, process_draw)
    elif call.data == "prayer_show":
        try:
            d = requests.get("http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5").json()['data']['timings']
            res = f"🕌 مواقيت الصلاة (القاهرة):\nالفجر: {d['Fajr']}\nالظهر: {d['Dhuhr']}\nالعصر: {d['Asr']}\nالمغرب: {d['Maghrib']}\nالعشاء: {d['Isha']}"
            bot.edit_message_text(res, cid, mid, reply_markup=extra_markup())
        except: bot.answer_callback_query(call.id, "تعذر جلب المواقيت.")

def get_phone_step(message, mode):
    phone = message.text.strip()
    msg = bot.send_message(message.chat.id, "🔐 أرسل كلمة المرور:")
    bot.register_next_step_handler(msg, get_pass_step, phone, mode)

def get_pass_step(message, phone, mode):
    pwd = message.text.strip()
    if mode == "vf_flex": run_vf_flex(message.chat.id, phone, pwd)

if __name__ == "__main__":
    bot.infinity_polling()
