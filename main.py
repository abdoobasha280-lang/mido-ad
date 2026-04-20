import telebot
import requests
import json
import sqlite3
import time
import hashlib
import base64
import xml.etree.ElementTree as ET
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
import io
import random

# ================== الإعدادات الأساسية ==================
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U'
CHANNEL_ID = '@midooojiokjj'          # معرف القناة (بدون https://t.me/)
ADMIN_ID = 7721807760                 # آيدي الأدمن الرئيسي
DEV_USER = '@AMI_EG'                  # يوزر المطور

bot = telebot.TeleBot(API_TOKEN)

# حالة البوت (شغال/متوقف)
bot_active = True

# قوائم الأدمن والمحظورين (تخزين في قاعدة البيانات أفضل، لكن سنستخدم ملفات JSON للبساطة)
ADMINS_FILE = 'admins.json'
BLOCKED_USERS_FILE = 'blocked_users.json'

def load_json(filename, default):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

admins = load_json(ADMINS_FILE, [])
blocked_users = load_json(BLOCKED_USERS_FILE, [])

# ================== قاعدة البيانات ==================
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

def set_bot_status(status):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE settings SET status = ?', (status,))
    conn.commit()
    conn.close()

init_db()
bot_active = (get_bot_status() == 1)

# ================== دوال التحقق من الصلاحيات ==================
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID) or str(user_id) in admins

def is_developer(user_id):
    return str(user_id) == str(ADMIN_ID)

def is_blocked(user_id):
    return str(user_id) in blocked_users

def check_sub(user_id):
    """التحقق من اشتراك المستخدم في القناة (تخطي للأدمن)"""
    if is_admin(user_id):
        return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ================== لوحة تحكم الأدمن ==================
def admin_markup():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    
    markup = InlineKeyboardMarkup(row_width=1)
    status_text = "🟢 شغال" if get_bot_status() == 1 else "🔴 متوقف"
    markup.add(
        InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="admin_stats"),
        InlineKeyboardButton(f"حالة البوت: {status_text}", callback_data="admin_toggle"),
        InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast"),
        InlineKeyboardButton("⛔ حظر مستخدم", callback_data="admin_block"),
        InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unblock"),
        InlineKeyboardButton("➕ إضافة أدمن", callback_data="admin_add"),
        InlineKeyboardButton("➖ حذف أدمن", callback_data="admin_remove")
    )
    return markup

# دوال معالجة أوامر الأدمن (سيتم ربطها بالكول باك)
def handle_admin_stats(call):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    conn.close()
    bot.edit_message_text(f"📊 إحصائيات:\n👥 عدد المستخدمين: {total_users}\n👮 عدد الأدمنة: {len(admins)}\n⛔ عدد المحظورين: {len(blocked_users)}",
                          call.message.chat.id, call.message.message_id, reply_markup=admin_markup())

def handle_admin_toggle(call):
    global bot_active
    new_status = 0 if get_bot_status() == 1 else 1
    set_bot_status(new_status)
    bot_active = (new_status == 1)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_markup())
    bot.answer_callback_query(call.id, f"تم { 'تشغيل' if new_status==1 else 'إيقاف'} البوت")

def handle_admin_broadcast(call):
    msg = bot.send_message(call.message.chat.id, "أرسل الرسالة التي تريد إذاعتها:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    success = 0
    for user in users:
        try:
            bot.send_message(user[0], f"📢 إعلان:\n{message.text}")
            success += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم الإرسال لـ {success} مستخدم", reply_markup=admin_markup())

def handle_admin_block(call):
    msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لحظره:")
    bot.register_next_step_handler(msg, process_block)

def process_block(message):
    uid = message.text.strip()
    if uid not in blocked_users:
        blocked_users.append(uid)
        save_json(BLOCKED_USERS_FILE, blocked_users)
        bot.reply_to(message, f"⛔ تم حظر المستخدم {uid}")
    else:
        bot.reply_to(message, "المستخدم محظور بالفعل")
    bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_markup())

def handle_admin_unblock(call):
    msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لإلغاء حظره:")
    bot.register_next_step_handler(msg, process_unblock)

def process_unblock(message):
    uid = message.text.strip()
    if uid in blocked_users:
        blocked_users.remove(uid)
        save_json(BLOCKED_USERS_FILE, blocked_users)
        bot.reply_to(message, f"✅ تم إلغاء حظر {uid}")
    else:
        bot.reply_to(message, "المستخدم ليس في قائمة المحظورين")
    bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_markup())

def handle_admin_add(call):
    if not is_developer(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مصرح: المطور فقط", show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لإضافته كأدمن:")
    bot.register_next_step_handler(msg, process_add_admin)

def process_add_admin(message):
    uid = message.text.strip()
    if uid not in admins:
        admins.append(uid)
        save_json(ADMINS_FILE, admins)
        bot.reply_to(message, f"✅ تمت إضافة {uid} كأدمن")
    else:
        bot.reply_to(message, "هذا المستخدم أدمن بالفعل")
    bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_markup())

def handle_admin_remove(call):
    if not is_developer(call.from_user.id):
        bot.answer_callback_query(call.id, "غير مصرح: المطور فقط", show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لحذفه من الأدمنة:")
    bot.register_next_step_handler(msg, process_remove_admin)

def process_remove_admin(message):
    uid = message.text.strip()
    if uid in admins:
        admins.remove(uid)
        save_json(ADMINS_FILE, admins)
        bot.reply_to(message, f"✅ تم حذف {uid} من الأدمنة")
    else:
        bot.reply_to(message, "هذا المستخدم ليس أدمن")
    bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_markup())

# ================== دوال الخدمات ==================
# ----- القائمة الرئيسية -----
def main_menu_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🍊 أورانج", callback_data="orange_menu"),
        InlineKeyboardButton("📱 إتصالات", callback_data="etisalat_menu"),
        InlineKeyboardButton("⚙ خدمات مجانية", callback_data="free_menu"),
        InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

# ----- قائمة أورانج -----
def orange_menu_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎁 250 ميجا (فوازير)", callback_data="orange_250"),
        InlineKeyboardButton("🎁 500 ميجا (كود رمضان)", callback_data="orange_500"),
        InlineKeyboardButton("💰 معرفة الرصيد", callback_data="orange_balance"),
        InlineKeyboardButton("🎡 عجلة الحظ", callback_data="orange_wheel"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# ----- قائمة إتصالات -----
def etisalat_menu_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎁 500 ميجا سوشيل", callback_data="etisalat_500"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# ----- قائمة خدمات مجانية -----
def free_menu_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times"),
        InlineKeyboardButton("🖼 إنشاء صورة نصية", callback_data="generate_image"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# ------------------- أورانج 250 ميجا (فوازير) -------------------
def orange_250_process(chat_id, number, password):
    loading_msg = bot.send_message(chat_id, "⏳ جاري فحص الحساب وحل الفوازير...")
    session = requests.Session()
    headers = {
        'User-Agent': "okhttp/4.10.0",
        'Content-Type': "application/json; charset=UTF-8"
    }
    try:
        # تسجيل الدخول
        auth_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        auth_payload = {
            "appVersion": "9.0.1",
            "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password
        }
        res = session.post(auth_url, json=auth_payload, headers=headers).json()
        acc_token = res['SignInUserResult']['AccessToken']
        time.sleep(1.5)

        # توليد توكن العملية
        gen_url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        gen_payload = {
            "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number, "Language": "ar", "Module": "0", "Password": password
        }
        headers['Token'] = acc_token
        token = session.post(gen_url, json=gen_payload, headers=headers).json()["Token"]

        # سحب الأسئلة
        q_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        q_data = session.post(q_url, json={"Dial": number, "Language": "ar", "Token": token}, headers=headers).json()
        if q_data.get('ErrorCode') == 1:
            bot.edit_message_text("❌ لقد شاركت اليوم بالفعل، جرب مرة أخرى غداً.", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
            return
        answers = []
        for q in q_data["Questions"]:
            for a in q["Answers"]:
                if a["IsCorrect"]:
                    answers.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break
        # إرسال الحل
        submit_url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        submit_res = session.post(submit_url, json={"Dial": number, "Language": "ar", "Token": token, "Answers": answers}, headers=headers).json()
        if submit_res.get('ErrorDescription') == "FawazeerSuccess":
            bot.edit_message_text("✅ مبروك! تم حل فوازير اليوم بنجاح واستلام الـ 250 ميجا.", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
        else:
            bot.edit_message_text(f"⚠️ رد النظام: {submit_res.get('ErrorDescription')}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
    except Exception as e:
        bot.edit_message_text(f"❌ فشل العملية: {str(e)}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())

# ------------------- أورانج 500 ميجا (كود رمضان) -------------------
def orange_500_process(chat_id, number, password):
    loading_msg = bot.send_message(chat_id, "⏳ جاري معالجة طلب 500 ميجا...")
    try:
        # تسجيل الدخول
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "8.8.5",
            "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password,
        }
        headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
        response_data = response.json()
        if 'SignInUserResult' not in response_data:
            bot.edit_message_text("❌ رقم الهاتف أو كلمة المرور غير صحيحة.", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
            return
        user_id = response_data['SignInUserResult']['UserData']['UserID']

        # جلب التوكن
        url1 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        headers1 = {"Content-Type": "application/json; charset=UTF-8", "User-Agent": "okhttp/3.14.9"}
        data1 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        token_response = requests.post(url1, headers=headers1, data=data1, timeout=10)
        token_data = token_response.json()
        ctv = token_data['GenerateTokenResult']['Token']
        h = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest()
        htv = h.upper()

        # استرداد العرض
        url4 = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
        headers4 = {
            "_ctv": ctv, "_htv": htv, "isEasyLogin": "false", "UserId": user_id,
            "Content-Type": "application/json; charset=UTF-8", "User-Agent": "okhttpwhitepro/3.12.1"
        }
        json4 = {
            "Language": "ar", "OSVersion": "Android7.0", "PromoCode": "رمضان كريم",
            "dial": number, "password": password,
            "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"
        }
        response4 = requests.post(url4, headers=headers4, json=json4, timeout=10)
        result_data = response4.json()
        error_desc = result_data.get('ErrorDescription', '')
        if error_desc == "Success":
            bot.edit_message_text("✅ ألف مبروك! تم استلام 500 ميجا.", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
        elif error_desc == "User is redeemed before":
            bot.edit_message_text("⚠️ لقد استلمت هذه الهدية من قبل.", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
        else:
            bot.edit_message_text(f"❌ خطأ: {error_desc}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())

# ------------------- معرفة رصيد أورانج -------------------
def orange_balance_process(chat_id, number, password):
    loading_msg = bot.send_message(chat_id, "⏳ جاري جلب الرصيد...")
    try:
        url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
        data = {"SelectedUserDial": None, "IsForAnotherRecipient": True, "RecipientDial": number, "Dial": number}
        headers = {"lang": "en"}
        response = requests.post(url, headers=headers, json=data, timeout=10)
        balance = response.json()['CreditBalance']
        bot.edit_message_text(f"💰 رصيدك الحالي: {balance} جنيه", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
    except Exception as e:
        bot.edit_message_text(f"❌ فشل جلب الرصيد: {str(e)}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())

# ------------------- عجلة الحظ أورانج -------------------
def orange_wheel_process(chat_id, number, password):
    loading_msg = bot.send_message(chat_id, "🎡 جاري تشغيل عجلة الحظ...")
    try:
        # شريط تقدم وهمي
        progress = ["*[░░░░░░░░░░] 0%*", "*[▓▓░░░░░░░░] 25%*", "*[▓▓▓▓░░░░░░] 50%*", "*[▓▓▓▓▓▓░░░░] 75%*", "*[▓▓▓▓▓▓▓▓▓▓] 100%*"]
        for i, p in enumerate(progress):
            time.sleep(0.8)
            bot.edit_message_text(p, chat_id, loading_msg.message_id, parse_mode='Markdown')
        
        # استدعاء API عجلة الحظ (نفس الكود المقدم)
        url2 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        headers2 = {"Content-Type": "application/json; charset=UTF-8", "User-Agent": "okhttp/3.14.9"}
        data2 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        response = requests.post(url2, headers=headers2, data=data2, timeout=10)
        response_data = response.json()
        ctv1 = response_data["GenerateTokenResult"]
        ctv = ctv1["Token"]
        hash_input = ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk"
        hashed_value = hashlib.sha256(hash_input.encode()).hexdigest()
        htv = hashed_value.upper()

        url_spin = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin"
        payload_spin = json.dumps({
            "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number, "Language": "en", "Password": password, "ServiceClassId": "1033"
        })
        headers_spin = {
            'User-Agent': "okhttp/3.14.9", '_ctv': ctv, '_htv': htv,
            'Content-Type': "application/json; charset=UTF-8"
        }
        response_spin = requests.post(url_spin, data=payload_spin, headers=headers_spin, timeout=10)
        spin_data = response_spin.json()
        if "ErrorDescription" in spin_data:
            error = spin_data['ErrorDescription']
            bot.edit_message_text(f"⚠️ {error}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
            return
        
        offer = spin_data["OfferDetails"]["OfferId"]
        category_id = spin_data["SecondryButtonDetails"]["CategoryId"]
        offer_name = spin_data["OfferDetails"]["OfferName"]

        # تأكيد العرض
        time.sleep(2)
        # إعادة جلب توكن جديد
        response2 = requests.post(url2, headers=headers2, data=data2, timeout=10)
        ctv = response2.json()["GenerateTokenResult"]["Token"]
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        url_fulfill = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
        payload_fulfill = json.dumps({
            "CategoryId": category_id, "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number, "Language": "en", "OfferId": offer, "Password": password, "ServiceClassId": "1033"
        })
        headers_fulfill = {
            'User-Agent': "okhttp/3.14.9", '_ctv': ctv, '_htv': htv,
            'Content-Type': "application/json; charset=UTF-8"
        }
        response_fulfill = requests.post(url_fulfill, data=payload_fulfill, headers=headers_fulfill, timeout=10)
        fulfill_data = response_fulfill.json()
        if "Already opted in" in str(fulfill_data):
            result = f"🎡 {offer_name}\n⚠️ أنت مشترك بالفعل في هذا العرض"
        else:
            result = f"🎡 {offer_name}\n✅ تم الاشتراك في العرض بنجاح"
        bot.edit_message_text(result, chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ في عجلة الحظ: {str(e)}", chat_id, loading_msg.message_id, reply_markup=orange_menu_markup())

# ------------------- إتصالات 500 ميجا سوشيل -------------------
def etisalat_500_process(chat_id, email, password):
    loading_msg = bot.send_message(chat_id, "⏳ جاري معالجة طلب 500 ميجا سوشيل...")
    try:
        tok = f"{email}:{password}"
        token = base64.b64encode(tok.encode()).decode()
        login_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan"
        login_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<loginRequest><deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt><modelType></modelType>
<osVersion></osVersion><platform>Android</platform><udid></udid></loginRequest>"""
        headers = {
            'Host': "mab.etisalat.com.eg:11003", 'User-Agent': "okhttp/5.0.0-alpha.11",
            'Content-Type': "text/xml; charset=UTF-8", 'Authorization': f"Basic {token}",
            'Language': "ar", 'APP-Version': "33.1.0", 'OS-Type': "Android"
        }
        r = requests.post(login_url, data=login_xml, headers=headers, timeout=10)
        root = ET.fromstring(r.text)
        number = root.find("dial").text

        redeem_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/rtim/rtimSubmitOrder"
        redeem_xml = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<rtimSubmitOrder><extraProductId>22932</extraProductId><offerId>22932</offerId>
<operationId>REDEEM</operationId><productId>RTIM_OFFERS=Offer_ID:22932;isRTIM:Y</productId>
<rtimFlag>true</rtimFlag><subscriberNumber>{number}</subscriberNumber></rtimSubmitOrder>"""
        response_redeem = requests.post(redeem_url, data=redeem_xml, headers=headers, timeout=10)
        if "success" in response_redeem.text.lower():
            bot.edit_message_text("✅ تم استلام 500 ميجا سوشيل بنجاح!", chat_id, loading_msg.message_id, reply_markup=etisalat_menu_markup())
        else:
            bot.edit_message_text("❌ فشل الاسترداد، قد تكون استلمت الهدية مسبقاً.", chat_id, loading_msg.message_id, reply_markup=etisalat_menu_markup())
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, loading_msg.message_id, reply_markup=etisalat_menu_markup())

# ------------------- مواقيت الصلاة -------------------
def prayer_times_process(chat_id, city="Cairo"):
    loading_msg = bot.send_message(chat_id, "⏳ جلب مواقيت الصلاة...")
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5"
        response = requests.get(url, timeout=10)
        data = response.json()
        timings = data['data']['timings']
        result = f"🕌 مواقيت الصلاة في {city}:\n"
        for name, time in timings.items():
            result += f"{name}: {time}\n"
        bot.edit_message_text(result, chat_id, loading_msg.message_id, reply_markup=free_menu_markup())
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ: {str(e)}", chat_id, loading_msg.message_id, reply_markup=free_menu_markup())

# ------------------- إنشاء صورة نصية -------------------
def generate_image_process(chat_id, text):
    loading_msg = bot.send_message(chat_id, "🖼 جاري إنشاء الصورة...")
    try:
        img = Image.new('RGB', (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        # رسم حدود بسيطة
        draw.rectangle([10, 10, 790, 390], outline=(0,0,0), width=3)
        # كتابة النص في المنتصف
        bbox = draw.textbbox((0,0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (800 - text_width) // 2
        y = (400 - text_height) // 2
        draw.text((x, y), text, fill=(0,0,0), font=font)
        # حفظ الصورة في الذاكرة
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        bot.send_photo(chat_id, img_bytes, caption="✅ تم إنشاء الصورة بنجاح", reply_markup=free_menu_markup())
        bot.delete_message(chat_id, loading_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, loading_msg.message_id, reply_markup=free_menu_markup())

# ================== معالج الأزرار والرسائل ==================
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if is_blocked(message.from_user.id):
        bot.reply_to(message, "⛔ أنت محظور من استخدام البوت.")
        return
    if not bot_active and not is_admin(message.from_user.id):
        bot.reply_to(message, "⚠️ البوت في صيانة، حاول لاحقاً.")
        return
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"مرحباً {message.from_user.first_name}!\nاختر خدمة:", reply_markup=main_menu_markup())
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        markup.add(InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
        bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القناة أولاً:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if is_blocked(call.from_user.id):
        bot.answer_callback_query(call.id, "أنت محظور", show_alert=True)
        return
    if not bot_active and not is_admin(call.from_user.id) and call.data not in ["check_sub", "back_main"]:
        bot.answer_callback_query(call.id, "البوت متوقف حالياً", show_alert=True)
        return

    # التحقق من الاشتراك
    if call.data == "check_sub":
        if check_sub(call.from_user.id):
            bot.edit_message_text("✅ تم التحقق! اختر خدمة:", call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)
        return

    # أزرار الأدمن
    if call.data.startswith("admin_"):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "غير مصرح", show_alert=True)
            return
        if call.data == "admin_stats":
            handle_admin_stats(call)
        elif call.data == "admin_toggle":
            handle_admin_toggle(call)
        elif call.data == "admin_broadcast":
            handle_admin_broadcast(call)
        elif call.data == "admin_block":
            handle_admin_block(call)
        elif call.data == "admin_unblock":
            handle_admin_unblock(call)
        elif call.data == "admin_add":
            handle_admin_add(call)
        elif call.data == "admin_remove":
            handle_admin_remove(call)
        return

    # قوائم الخدمات
    if call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())
    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج:", call.message.chat.id, call.message.message_id, reply_markup=orange_menu_markup())
    elif call.data == "etisalat_menu":
        bot.edit_message_text("📱 خدمات إتصالات:", call.message.chat.id, call.message.message_id, reply_markup=etisalat_menu_markup())
    elif call.data == "free_menu":
        bot.edit_message_text("⚙ خدمات مجانية:", call.message.chat.id, call.message.message_id, reply_markup=free_menu_markup())
    
    # خدمات أورانج
    elif call.data == "orange_250":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_250"))
    elif call.data == "orange_500":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_500"))
    elif call.data == "orange_balance":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج:")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_balance"))
    elif call.data == "orange_wheel":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج لعجلة الحظ:")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_wheel"))
    
    # خدمة إتصالات
    elif call.data == "etisalat_500":
        msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني (إيميل حساب إتصالات):")
        bot.register_next_step_handler(msg, get_etisalat_password)
    
    # خدمات مجانية
    elif call.data == "prayer_times":
        msg = bot.send_message(call.message.chat.id, "أدخل اسم المدينة (مثال: Cairo):")
        bot.register_next_step_handler(msg, lambda m: prayer_times_process(m.chat.id, m.text))
    elif call.data == "generate_image":
        msg = bot.send_message(call.message.chat.id, "أدخل النص الذي تريد تحويله إلى صورة:")
        bot.register_next_step_handler(msg, lambda m: generate_image_process(m.chat.id, m.text))

def get_number_password(message, service):
    number = message.text.strip()
    if not (number.isdigit() and len(number) == 11 and number.startswith('01')):
        bot.reply_to(message, "رقم غير صالح، أدخل 11 رقمًا يبدأ بـ 01")
        return
    msg = bot.send_message(message.chat.id, "أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: process_orange_service(m, number, service))

def process_orange_service(message, number, service):
    password = message.text.strip()
    if service == "orange_250":
        orange_250_process(message.chat.id, number, password)
    elif service == "orange_500":
        orange_500_process(message.chat.id, number, password)
    elif service == "orange_balance":
        orange_balance_process(message.chat.id, number, password)
    elif service == "orange_wheel":
        orange_wheel_process(message.chat.id, number, password)

def get_etisalat_password(message):
    email = message.text.strip()
    msg = bot.send_message(message.chat.id, "أدخل كلمة المرور لحساب إتصالات:")
    bot.register_next_step_handler(msg, lambda m: etisalat_500_process(m.chat.id, email, m.text))

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text and not message.text.startswith('/'):
        start(message)

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.infinity_polling()
