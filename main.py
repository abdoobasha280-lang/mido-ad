import sqlite3
import logging
import hashlib
import json
import asyncio
import httpx
import base64
import os
import uuid
import yt_dlp
import xml.etree.ElementTree as ET
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters, ContextTypes
)

# -------------------- ⚙️ الإعدادات الأساسية --------------------
TOKEN = "8612878441:AAHwz7-akagxmpsLWm7cyYvN6yMoRu1fsvc" 

ADMIN_IDS = [7721807760]  
DEVELOPER_USERNAME = "@AMI_EG"

REQUIRED_CHANNELS = [
    {"name": "midooojiokjj", "url": "https://t.me/midooojiokjj", "username": "@midooojiokjj"},
]

# حالات المحادثة
PHONE, PASSWORD, EMAIL, DOWNLOAD_LINK, SEARCH_NUM, BAN_ID, BROADCAST_TEXT = range(7)
DB_FILE = "bot_data.db"
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

if not os.path.exists('downloads'):
    os.makedirs('downloads')

# -------------------- 🗄️ إدارة قاعدة البيانات --------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
                    joined_date TEXT, is_banned INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, phone TEXT,
                    service_type TEXT, amount INTEGER, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_state (key TEXT PRIMARY KEY, value TEXT)''')
    
    c.execute("INSERT OR IGNORE INTO bot_state (key, value) VALUES ('enabled', 'True')")
    c.execute("INSERT OR IGNORE INTO bot_state (key, value) VALUES ('total_downloads', '0')")
    c.execute("INSERT OR IGNORE INTO bot_state (key, value) VALUES ('total_messages', '0')")
    
    conn.commit()
    conn.close()

def is_bot_enabled():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_state WHERE key='enabled'")
    res = c.fetchone()
    conn.close()
    return res[0].lower() == 'true' if res else True

def is_user_banned(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res[0] == 1 if res else False

def register_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date) VALUES (?, ?, ?, ?)", 
              (user_id, username, first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def register_group(group_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO groups (group_id, joined_date) VALUES (?, ?)", (group_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_activation(user_id, phone, service_type, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO activations (user_id, phone, service_type, amount, date) VALUES (?, ?, ?, ?, ?)",
              (user_id, phone, service_type, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def increment_stat(stat_key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE bot_state SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT) WHERE key=?", (stat_key,))
    conn.commit()
    conn.close()

def get_stat(stat_key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM bot_state WHERE key=?", (stat_key,))
    res = c.fetchone()
    conn.close()
    return int(res[0]) if res else 0

# -------------------- 🔌 دوال الـ APIs (أورانج واتصالات) --------------------

async def api_fawazeer_250(number, password):
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            url = "https://services.orange.eg/SignIn.svc/SignInUser"
            payload = {"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
            resp = await client.post(url, json=payload)
            access_token = resp.json()['SignInUserResult']['AccessToken']
            
            url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
            headers = {'Token': access_token, 'AppVersion': "9.0.1", 'OsVersion': "13", 'IsAndroid': "true"}
            payload_gen = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}
            resp_gen = await client.post(url_gen, json=payload_gen, headers=headers)
            token = resp_gen.json()["Token"]

            url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
            resp_q = await client.post(url_q, json={"Dial": number, "Language": "ar", "Token": token})
            data = resp_q.json()
            if data.get('ErrorCode') == 1: return False, "⚠️ حصلت عليها اليوم، جرب غداً"
            
            questions = data.get("Questions")
            answers = [{"QuestionId": q["Answers"][0]["QuestionId"], "AnswerId": next(a["Id"] for a in q["Answers"] if a["IsCorrect"])} for q in questions]
            
            url_sub = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
            resp_sub = await client.post(url_sub, json={"Dial": number, "Language": "ar", "Token": token, "Answers": answers})
            if resp_sub.json().get('ErrorDescription') == "FawazeerSuccess":
                return True, "✅ تم تفعيل 250 ميجا فوازير بنجاح"
            return False, f"❌ {resp_sub.json().get('ErrorDescription')}"
        except: return False, "❌ خطأ في البيانات أو الشبكة"

async def api_orange_500(number, password):
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            url = "https://services.orange.eg/SignIn.svc/SignInUser"
            payload = {"appVersion": "9.0.0", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
            resp = await client.post(url, json=payload)
            user_id = resp.json()['SignInUserResult']['UserData']["UserID"]

            url_t = "https://services.orange.eg/GetToken.svc/GenerateToken"
            resp_t = await client.post(url_t, json={"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}})
            ctv = resp_t.json()['GenerateTokenResult']['Token']
            htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

            url_r = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
            headers = {"_ctv": ctv, "_htv": htv, "UserId": str(user_id)}
            payload_r = {"Language": "ar", "OSVersion": "Android7.0", "PromoCode": "رمضان كريم", "dial": number, "password": password, "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"}
            resp_r = await client.post(url_r, headers=headers, json=payload_r)
            err = resp_r.json().get('ErrorDescription')
            if err == "Success": return True, "✅ تم تفعيل 524 ميجا بنجاح 🎉"
            return False, f"❌ {err}"
        except: return False, "❌ حدث خطأ، حاول لاحقاً"

async def api_wheel(number, password):
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            url_t = "https://services.orange.eg/GetToken.svc/GenerateToken"
            r_t = await client.post(url_t, json={"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}})
            ctv = r_t.json()["GenerateTokenResult"]["Token"]
            htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

            url_s = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin"
            headers = {"_ctv": ctv, "_htv": htv, "IsAndroid": "true", "AppVersion": "7.2.0"}
            payload_s = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "en", "Password": password, "ServiceClassId": "1033"}
            r_s = await client.post(url_s, json=payload_s, headers=headers)
            res = r_s.json()
            if "ErrorDescription" in res: return False, "⚠️ استهلكت محاولات العجلة اليوم"
            
            offer_id, cat_id, offer_name = res["OfferDetails"]["OfferId"], res["SecondryButtonDetails"]["CategoryId"], res["OfferDetails"]["OfferName"]
            await asyncio.sleep(2)
            
            url_f = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
            payload_f = {"CategoryId": cat_id, "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "en", "OfferId": offer_id, "Password": password, "ServiceClassId": "1033"}
            r_f = await client.post(url_f, json=payload_f, headers=headers)
            return True, f"🎡 العجلة: {offer_name}\n✅ تم الاشتراك بنجاح"
        except: return False, "❌ فشلت محاولة العجلة"

async def api_orange_codes(number, password, msg_to_edit=None):
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if msg_to_edit: await msg_to_edit.edit_text("⏳ **جاري تسجيل الدخول في أورانج...**")
            url = "https://services.orange.eg/SignIn.svc/SignInUser"
            payload = {"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
            headers = {'User-Agent': "okhttp/4.10.0", 'Connection': "Keep-Alive", 'Content-Type': "application/json; charset=UTF-8"}
            response = await client.post(url, json=payload, headers=headers)
            try: access_token = response.json()['SignInUserResult']['AccessToken']
            except: return False, "❌ خطأ في الرقم أو كلمة المرور."

            if msg_to_edit: await msg_to_edit.edit_text("⚡ **جاري فحص الأكواد...**")
            url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
            payload_gen = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}
            headers_gen = {'User-Agent': "okhttp/4.10.0", 'Token': access_token, 'Content-Type': "application/json; charset=UTF-8", 'AppVersion': "9.0.1", 'OsVersion': "13", 'IsAndroid': "true"}
            response_gen = await client.post(url_gen, json=payload_gen, headers=headers_gen)
            token = response_gen.json()["Token"]

            url_share = "https://services.orange.eg/APIs/Promotions/api/SummerOffer/SharingInquiry"
            response_share = await client.post(url_share, json={"Dial": number, "Language": "ar", "Token": token})
            data_res = response_share.json()
            
            if data_res.get('ErrorDescription') == "SummerOfferSuccess":
                codes_list = data_res.get('SharableCodes', [])
                if codes_list:
                    f = codes_list[0]
                    return True, f"🎁 **أكواد أورانج المتاحة:**\n\n🔑 الكود: `{f.get('Code')}`\n💎 الهدية: `{f.get('GiftValue')}`\n⏳ المتبقي: `{f.get('RemainingSharingTime')}`"
            return False, "⚠️ ليس لديك أكواد حالياً على هذا الخط."
        except: return False, "❌ حدث خطأ غير متوقع."

async def api_etisalat_2hours(number, email, password, msg_to_edit=None):
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            num = number[1:] if number.startswith("011") else number
            auth = base64.b64encode(f"{email}:{password}".encode("ascii")).decode("ascii")
            if msg_to_edit: await msg_to_edit.edit_text("⏳ **جاري التفعيل   ...**")
            
            urllog = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
            headerslog = {"applicationVersion": "2", "applicationName": "MAB", "Accept": "text/xml", "Authorization": f"Basic {auth}", "Content-Type": "text/xml; charset=UTF-8", "User-Agent": "okhttp/5.0.0-alpha.11"}
            datalog = "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><loginRequest><platform>Android</platform></loginRequest>"
            log = await client.post(urllog, headers=headerslog, data=datalog)
            
            if "true" not in log.text: return False, "❌ بيانات الحساب خاطئة."
            if msg_to_edit: await msg_to_edit.edit_text("⚡ **جاري فحص العروض...**")
            
            st = log.headers.get("Set-Cookie", "")
            ck = st.split(";")[0] if ";" in st else st
            br = log.headers.get("auth", "")
            
            url = f"https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/offersV3?req=<dialAndLanguageRequest><subscriberNumber>{num}</subscriberNumber><language>1</language></dialAndLanguageRequest>"
            headers = {'applicationVersion': "2", 'Content-Type': "text/xml", 'applicationName': "MAB", 'Accept': "text/xml", 'auth': f"Bearer {br}", 'Cookie': ck, 'User-Agent': "okhttp/5.0.0-alpha.11"}
            response = await client.get(url, headers=headers)
            
            root = ET.fromstring(response.text)
            offer_id = None
            for parameter in root.findall('.//fulfilmentParameter'):
                if parameter.find('name').text == 'Offer_ID':
                    offer_id = parameter.find('value').text
                    break
            if not offer_id: return False, "⚠️ حصلت على العرض اليوم بالفعل."
            
            if msg_to_edit: await msg_to_edit.edit_text("🚀 **جاري تفعيل ساعتين نت...**")
            urlsub = "https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/submitOrder"
            datasub = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><msisdn>{num}</msisdn><operation>ACTIVATE</operation><parameters><parameter><name>GIFT_FULLFILMENT_PARAMETERS</name><value>Offer_ID:{offer_id};ACTIVATE:True;isRTIM:Y</value></parameter></parameters><productName>FAN_ZONE_HOURLY_BUNDLE</productName></submitOrderRequest>"
            subs = await client.post(urlsub, headers=headerslog, data=datasub)
            if "true" in subs.text: return True, "✅ تم إضافة ساعتين نت اتصالات بنجاح."
            return False, "❌ فشل تفعيل العرض."
        except: return False, "❌ حدث خطأ غير متوقع."

# -------------------- 🕌 دالة مواقيت الصلاة --------------------
async def get_prayer_times():
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get("http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5")
            times = res.json()['data']['timings']
            msg = (
                f"🕌 **مواقيت الصلاة في مصر بتوقيت القاهرة:**\n"
                f"______________________________\n\n"
                f"🌅 الفجر: `{times['Fajr']}`\n"
                f"☀️ الشروق: `{times['Sunrise']}`\n"
                f"☀️ الظهر: `{times['Dhuhr']}`\n"
                f"🌇 العصر: `{times['Asr']}`\n"
                f"🌆 المغرب: `{times['Maghrib']}`\n"
                f"🌃 العشاء: `{times['Isha']}`\n"
                f"______________________________\n"
                f"✨ صلاتك حياتك.. حافظ عليها ✨"
            )
            return msg
        except: return "❌ عذراً، فشل الاتصال بخادم مواقيت الصلاة حالياً."

# -------------------- 👑 لوحة التحكم الكلية (القديمة + الجديدة) --------------------

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return

    msg = "🛠️ لوحة التحكم:"
    
    # دمج الأزرار القديمة (الإحصائيات تنبيه، الإذاعة، قناتنا) مع الإضافات الفاخرة الجديدة
    keyboard = [
        [InlineKeyboardButton("الإحصائيات 📊", callback_data="adm_stats_alert")],
        [InlineKeyboardButton("إذاعة 📢", callback_data="adm_broadcast_menu"),
         InlineKeyboardButton("قناتنا 👨‍💻", url="https://t.me/midooojiokjj")],
        [InlineKeyboardButton("🔍 بحث عن رقم خط", callback_data="adm_search"),
         InlineKeyboardButton("📋 قائمة آخر التفعيلات", callback_data="adm_list")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="adm_ban"),
         InlineKeyboardButton("🔄 تبديل حالة البوت", callback_data="bot_toggle")]
    ]
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id not in ADMIN_IDS: return

    if query.data == "adm_stats_alert":
        # الإحصائيات القديمة الفورية (الأعضاء والجروبات) مضافاً إليها إحصائيات النظام الفاخرة الجديدة
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        u_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM groups")
        g_count = c.fetchone()[0]
        conn.close()

        bot_status = "🟢 شغال" if is_bot_enabled() else "🔴 صيانة"
        downloads = get_stat("total_downloads")
        messages = get_stat("total_messages")

        alert_text = (
            f"👤 الأعضاء: {u_count}\n"
            f"👥 الجروبات: {g_count}\n"
            f"🤖 حالة البوت: {bot_status}\n"
            f"📥 الفيديوهات المحملة: {downloads}\n"
            f"📩 رسائل البوت: {messages}"
        )
        await query.answer(alert_text, show_alert=True)
        
    elif query.data == "adm_broadcast_menu":
        await query.answer()
        markup = [
            [InlineKeyboardButton("إذاعة للجميع 🌎", callback_data="adm_bc_all")],
            [InlineKeyboardButton("تراجع 🔙", callback_data="back_to_admin")]
        ]
        await query.edit_message_text("اختر نوع الإذاعة:", reply_markup=InlineKeyboardMarkup(markup))
        
    elif query.data == "adm_bc_all":
        await query.answer()
        await query.edit_message_text("أرسل نص الإذاعة الآن:")
        return BROADCAST_TEXT

    elif query.data == "bot_toggle":
        await query.answer()
        new_state = "False" if is_bot_enabled() else "True"
        conn = sqlite3.connect(DB_FILE)
        conn.execute("UPDATE bot_state SET value = ? WHERE key = 'enabled'", (new_state,))
        conn.commit()
        conn.close()
        await admin_panel(update, context)
        
    elif query.data == "adm_list":
        await query.answer()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id, phone, service_type, date FROM activations ORDER BY id DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            txt = "📋 لا توجد تفعيلات مسجلة حتى الآن."
        else:
            txt = "📋 **آخر 10 تفعيلات في النظام:**\n______________________________\n\n"
            for r in rows:
                txt += f"👤 ID: `{r[0]}`\n📱 الخط: `{r[1]}`\n🛠 الخدمة: `{r[2]}`\n📅 الوقت: `{r[3]}`\n🔹🔹🔹\n"
        
        keys = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")]]
        await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(keys), parse_mode="Markdown")
        
    elif query.data == "adm_search":
        await query.answer()
        await query.edit_message_text("🔍 **أرسل الآن رقم الهاتف المراد البحث عن تفعيلاته:**")
        return SEARCH_NUM
        
    elif query.data == "adm_ban":
        await query.answer()
        await query.edit_message_text("🚫 **أرسل الـ Telegram ID للمستخدم المراد حظره/إلغاء حظره:**")
        return BAN_ID

# -------------------- 📝 وظائف معالجة أوامر الإدارة --------------------

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    broadcast_msg = update.message.text
    increment_stat("total_messages")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [r[0] for r in c.fetchall()]
    c.execute("SELECT group_id FROM groups")
    groups = [r[0] for r in c.fetchall()]
    conn.close()
    
    all_chats = list(set(users + groups))
    sent_count = 0
    
    status_msg = await update.message.reply_text("⏳ جاري بدء الإذاعة...")
    
    for chat in all_chats:
        try:
            await context.bot.send_message(chat_id=chat, text=broadcast_msg)
            sent_count += 1
        except:
            continue
            
    await status_msg.edit_text(f"✅ تمت الإذاعة بنجاح لـ {sent_count} شات.")
    return ConversationHandler.END

async def process_search_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    increment_stat("total_messages")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, service_type, amount, date FROM activations WHERE phone=?", (phone,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        txt = f"❌ لم يتم العثور على أي عمليات تفعيل للرقم: `{phone}`"
    else:
        txt = f"📊 **نتائج البحث للرقم ({phone}):**\n______________________________\n\n"
        for r in rows:
            txt += f"👤 قام به آيدي: `{r[0]}`\n🛠 الخدمة: `{r[1]}`\n📦 القيمة: `{r[2]} MB`\n📅 التاريخ: `{r[3]}`\n🔹🔹🔹\n"
            
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لوحة التحكم", callback_data="back_to_admin")]]), parse_mode="Markdown")
    return ConversationHandler.END

async def process_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = update.message.text.strip()
    increment_stat("total_messages")
    if not target_id.isdigit():
        await update.message.reply_text("❌ يرجى إدخال ID صحيح (أرقام فقط).")
        return ConversationHandler.END
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (target_id,))
    res = c.fetchone()
    
    if res is None:
        await update.message.reply_text("❌ هذا المستخدم لم يسجل في البوت من قبل.")
        conn.close()
        return ConversationHandler.END
        
    new_ban = 0 if res[0] == 1 else 1
    c.execute("UPDATE users SET is_banned=? WHERE user_id=?", (new_ban, target_id))
    conn.commit()
    conn.close()
    
    status_txt = "🚫 تم حظره بنجاح" if new_ban == 1 else "🟢 تم إلغاء حظره بنجاح"
    await update.message.reply_text(f"✅ العضو `{target_id}` {status_txt}.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 لوحة التحكم", callback_data="back_to_admin")]]), parse_mode="Markdown")
    return ConversationHandler.END

# -------------------- 📱 واجهات البوت الرئيسية --------------------
async def check_sub(user_id, bot):
    for ch in REQUIRED_CHANNELS:
        try:
            m = await bot.get_chat_member(ch["username"], user_id)
            if m.status in ["left", "kicked"]: return False
        except: return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    increment_stat("total_messages")
    
    if chat.type in ["group", "supergroup"]:
        register_group(chat.id)
        return

    register_user(user.id, user.username, user.first_name)
    
    if is_user_banned(user.id):
        await update.message.reply_text("❌ عذراً، لقد تم حظرك من استخدام هذا البوت من قبل الإدارة.")
        return

    if not is_bot_enabled() and user.id not in ADMIN_IDS:
        await update.message.reply_text("⚠️ البوت حالياً في وضع الصيانة.")
        return

    if not await check_sub(user.id, context.bot):
        keys = [[InlineKeyboardButton(f"📢 {ch['name']}", url=ch["url"])] for ch in REQUIRED_CHANNELS]
        keys.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="back_to_start")])
        await update.message.reply_text("❗ **يجب الاشتراك في القنوات أولاً:**", reply_markup=InlineKeyboardMarkup(keys))
        return

    # الأزرار الشفافة والمودرن للواجهة الأساسية
    keyboard = [
        [InlineKeyboardButton("🍊 ORANGE SERVICES", callback_data="menu_orange")],
        [InlineKeyboardButton("🟢 ETISALAT SERVICES", callback_data="menu_etisalat")],
        [InlineKeyboardButton("🔴 VODAFONE SERVICES", callback_data="menu_vodafone")],
        [InlineKeyboardButton("⚙️ CONFIGS SERVICES", callback_data="menu_configs")],
        [InlineKeyboardButton("✨ EXTRA SERVICES", callback_data="menu_extra")]
    ]
    
    msg_text = f"🛡️ **أهلاً بك يا {user.first_name}**\n\ بوت الخدمات التلقائي المطوّر (Midoبوت).\n______________________________\nاختر الخدمة التي تريدها من الأزرار بالأسفل:"
    if update.message:
        await update.message.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(msg_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# -------------------- 📋 معالجة القوائم الفرعية --------------------

async def menu_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_orange":
        keyboard = [
            [InlineKeyboardButton("🎁 250 ميجا", callback_data="svc_250")],
            [InlineKeyboardButton("🚀 500 ميجا", callback_data="svc_500")],
            [InlineKeyboardButton("🎡 عجلة الحظ", callback_data="svc_wheel")],
            [InlineKeyboardButton("📋 معرفة أكواد أورانج", callback_data="svc_ora_codes")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]
        ]
        await query.edit_message_text("🍊 **اختر خدمة أورانج:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "menu_etisalat":
        keyboard = [
            [InlineKeyboardButton("⏱️ ساعتين اتصالات", callback_data="svc_eti_2h")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]
        ]
        await query.edit_message_text("🟢 **اختر خدمة اتصالات:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "menu_vodafone":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]]
        await query.edit_message_text("🔴 **خدمات فودافون**\n\n⚠️ عذراً، هذا القسم تحت التطوير حالياً وسيتوفر قريباً!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "menu_configs":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]]
        await query.edit_message_text("⚙️ **قسم الكونفنجات**\n\n🛠️ عذراً، هذا القسم قيد الصيانة والتحديث الآن.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "menu_extra":
        keyboard = [
            [InlineKeyboardButton("📥 تحميل فيديوهات", callback_data="extra_download")],
            [InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="extra_prayer")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_start")]
        ]
        await query.edit_message_text("✨ **الخدمات الإضافية المتاحة:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "extra_prayer":
        msg = await get_prayer_times()
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="menu_extra")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# -------------------- 📥 سكريبت تحميل الفيديوهات (Async) --------------------

async def start_download_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📥 **أرسل الآن رابط الفيديو لتحميله فوراً ياحب :**")
    return DOWNLOAD_LINK

def download_video_sync(url, output_path):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def process_video_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    increment_stat("total_messages")
    
    if not url.startswith("http"):
        await update.message.reply_text("❌ الرابط غير صحيح، يرجى إرسال رابط حقيقي.")
        return ConversationHandler.END

    status_msg = await update.message.reply_text("⏳ **جاري تحميل مقطع الفيديو...**")
    unique_name = f"downloads/{uuid.uuid4()}.mp4"
    
    try:
        filename = await asyncio.to_thread(download_video_sync, url, unique_name)
        await status_msg.edit_text("🚀 **جاري إرسال الفديو ليك   ...**")
        
        with open(filename, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=f"✅ تم التحميل بنجاح بواسطة bot mido.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ حذف 🗑️", callback_data="delete_msg")]])
            )
        await status_msg.delete()
        increment_stat("total_downloads")
        
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        await status_msg.edit_text("⚠️ فشل تحميل الفيديو. الحجم كبير جداً أو الرابط غير مدعوم.")
        if os.path.exists(unique_name): os.remove(unique_name)
        
    return ConversationHandler.END

# -------------------- 🔄 خط سير تفعيل شبكات الإتصال --------------------

async def start_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['service'] = query.data
    
    if "eti_" in query.data:
        await query.edit_message_text("📱 **أرسل رقم اتصالات  :**")
    else:
        await query.edit_message_text("📱 **أرسل رقم أورانج  :**")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()
    service = context.user_data.get('service', '')
    increment_stat("total_messages")
    
    if "eti_" in service:
        await update.message.reply_text("📧 **أرسل البريد الإلكتروني (Gmail) المرتبط بالحساب:**")
        return EMAIL
    else:
        await update.message.reply_text("🔑 **أرسل كلمة مرور الحساب (Password):**")
        return PASSWORD

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text.strip()
    increment_stat("total_messages")
    await update.message.reply_text("🔑 **أرسل كلمة المرور (Password):**")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    phone = context.user_data['phone']
    service = context.user_data['service']
    increment_stat("total_messages")
    
    msg = await update.message.reply_text("⏳ **جاري معالجة طلبك...**")
    success, amount, s_type, res = False, 0, "", ""

    if "eti_2h" in service:
        email = context.user_data['email']
        success, res = await api_etisalat_2hours(phone, email, password, msg_to_edit=msg)
        if success: amount, s_type = 0, "Etisalat_2H"
    elif "svc_ora_codes" in service:
        success, res = await api_orange_codes(phone, password, msg_to_edit=msg)
        if success: amount, s_type = 0, "Orange_Codes"
    elif "250" in service:
        await msg.edit_text("⏳ **جاري تفعيل الـ 250 ميجا...**")
        success, res = await api_fawazeer_250(phone, password)
        if success: amount, s_type = 250, "250MB"
    elif "500" in service:
        await msg.edit_text("⏳ **جاري تفعيل الـ 500 ميجا...**")
        success, res = await api_orange_500(phone, password)
        if success: amount, s_type = 500, "500MB"
    else:
        await msg.edit_text("⏳ **جاري تدوير العجلة...**")
        success, res = await api_wheel(phone, password)
        if success: amount, s_type = 100, "Wheel"

    if success: 
        log_activation(update.effective_user.id, phone, s_type, amount)
    
    await msg.edit_text(f"{res}\n______________________________\nبواسطة المطور: {DEVELOPER_USERNAME}")
    return ConversationHandler.END

# -------------------- 🚀 تشغيل المحركات والربط الكلي --------------------
def main():
    init_db() 
    app = Application.builder().token(TOKEN).build()
    
    # الـ Conversation Handler المدمج للأدمن بدون أي حظر للوظائف القديمة
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callbacks, pattern="^adm_")],
        states={
            SEARCH_NUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_search_num)],
            BAN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_ban_user)],
            BROADCAST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_broadcast)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )

    extra_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_download_flow, pattern="extra_download")],
        states={
            DOWNLOAD_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_video_download)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )

    net_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_flow, pattern="^svc_")],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="back_to_admin"))
    app.add_handler(CallbackQueryHandler(start, pattern="back_to_start"))
    app.add_handler(CallbackQueryHandler(menu_manager, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(menu_manager, pattern="^extra_"))
    
    app.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.message.delete(), pattern="delete_msg"))
    app.add_handler(CallbackQueryHandler(admin_callbacks, pattern="bot_toggle"))

    app.add_handler(admin_conv)
    app.add_handler(extra_conv)
    app.add_handler(net_conv)
    
    print("Mido AI is running perfectly with ALL features combined... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
