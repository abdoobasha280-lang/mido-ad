import telebot
import requests
import json
import sqlite3
import time
import hashlib
import base64
import xml.etree.ElementTree as ET
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================== الإعدادات الأساسية ==================
API_TOKEN = '7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U'
CHANNEL_ID = '@midooojiokjj'          # معرف القناة (مع @)
ADMIN_ID = 7721807760                 # ايدي المطور الرئيسي
DEV_USER = '@AMI_EG'                  # يوزر المطور للتواصل

bot = telebot.TeleBot(API_TOKEN)

# حالة البوت (شغال/متوقف) - تخزن في قاعدة البيانات
bot_active = True

# ================== إعداد قاعدة البيانات والملفات ==================
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

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def load_json(filename, default):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

admins = load_json('admins.json', [])
blocked_users = load_json('blocked_users.json', [])

init_db()
bot_active = (get_bot_status() == 1)

# ================== دوال التحقق ==================
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID) or str(user_id) in admins

def is_blocked(user_id):
    return str(user_id) in blocked_users

def check_sub(user_id):
    """التحقق من الاشتراك في القناة (تخطي للأدمن)"""
    if is_admin(user_id):
        return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ================== لوحة تحكم الأدمن ==================
def admin_panel_markup():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    user_count = c.fetchone()[0]
    conn.close()
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"👥 المستخدمين: {user_count}", callback_data="admin_stats"),
        InlineKeyboardButton("🟢 تشغيل/إيقاف البوت", callback_data="admin_toggle"),
        InlineKeyboardButton("📢 إذاعة جماعية", callback_data="admin_broadcast"),
        InlineKeyboardButton("⛔ حظر مستخدم", callback_data="admin_block"),
        InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unblock"),
        InlineKeyboardButton("➕ إضافة أدمن", callback_data="admin_add"),
        InlineKeyboardButton("➖ حذف أدمن", callback_data="admin_remove")
    )
    return markup

def send_admin_panel(chat_id, message_id=None):
    text = "🛠 لوحة تحكم البوت"
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=admin_panel_markup())
            return
        except:
            pass
    bot.send_message(chat_id, text, reply_markup=admin_panel_markup())

# ================== القوائم الرئيسية ==================
def main_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🍊 أورانج", callback_data="orange_menu"),
        InlineKeyboardButton("📱 إتصالات", callback_data="etisalat_menu"),
        InlineKeyboardButton("⚙ خدمات مجانية", callback_data="free_menu"),
        InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return markup

def orange_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎁 250 ميجا (فوازير)", callback_data="orange_250"),
        InlineKeyboardButton("🎁 500 ميجا (كود رمضان)", callback_data="orange_500"),
        InlineKeyboardButton("💰 معرفة الرصيد", callback_data="orange_balance"),
        InlineKeyboardButton("🎡 عجلة الحظ", callback_data="orange_wheel"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def etisalat_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎁 500 ميجا سوشيل", callback_data="etisalat_500"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

def free_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times"),
        Inlinerayer_times"),
        InlineKeyboardButton("🖼KeyboardButton("🖼 إنشاء إنشاء صورة نصية", callback_data="generate_image صورة نصية", callback_data="generate_image"),
       "),
        Inline InlineKeyboardButton("KeyboardButton("🔙 رجوع", callback🔙 رجوع_data="back_main")
   ", callback_data="back_main")
    )
    )
    return markup

# ================= return markup

# ================== دوال الخدمات= دوال الخدمات ================= ==================

# --- أورانج=

# --- أورانج 250 ميجا ( 250 ميجا (فوازير) ---فوازير) ---
def orange_250(chat_id,
def orange_250(chat_id, number, password):
    msg = bot.send_message(chat number, password):
    msg = bot.send_message(chat_id, "⏳_id, "⏳ جاري حل الفو جاري حلازير...")
    session = requests.S الفوازير...")
    session = requests.Sessionession()
    headers =()
    headers = {'User-Agent': " {'User-Agent': "okhttp/4.10.0", 'okhttp/4.10.0Content-Type': "application", 'Content-Type': "application/json; charset=UTF/json; charset=UTF-8"}
    try-8"}
    try:
        # تسجيل الدخ:
        # تسجيل الدخول
        auth = sessionول
        auth = session.post("https://services..post("https://services.orange.eg/Sorange.eg/SignIn.svc/SignInUser", json={
           ignIn.svc/SignInUser", json={
            "appVersion": "9 "appVersion": "9.0.1", "channel":.0.1", "channel": {"ChannelName": "Mobinil {"ChannelName": "MobinilAndMe", "Password":AndMe", "Password": "ig3yh*mk "ig3yh*mk5l42@5l42@oj7oj7QAR8yFQAR8yF"},
            "dialNumber": number, ""},
            "dialNumber": number, "isAndroid": True, "lang":isAndroid": True, "lang": "ar", "password": password "ar", "password": password
        }, timeout=15
        }, timeout=15).json()
        acc_token).json()
        acc_token = auth['Sign = auth['SignInUserResult']['AccessToken']
        timeInUserResult']['AccessToken']
        time.sleep(1)

        # توليد توكن
       .sleep(1)

        # توليد توكن headers['Token'] = acc_token
        headers['Token'] = acc_token
        gen = session.post("https://
        gen = session.post("https://services.orange.services.orange.eg/eg/APIs/Profile/api/BasicAuthentication/GenerateAPIs/Profile/api/BasicAuthentication/Generate", json={
            "ChannelName": "M", json={
            "ChannelName": "MobinilAndMe", "obinilAndMe", "ChannelPassword": "ig3yh*mkChannelPassword": "ig3yh*mk55l42@ojl42@oj7QAR8yF7QAR8yF",
            "Dial",
            "Dial": number, "Language": "ar", "Module":": number, "Language": "ar", "Module": "0", "Password": password "0", "Password": password
        }, timeout=15).json
        }, timeout=15).json()
       ()
        token = gen["Token"]

        token = gen["Token"]

        # # جلب الأسئ جلب الأسئلة
        q = session.post("لة
        q = sessionhttps://services.orange.eg/APIs/Ram.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffadan2024/api/RamadanOffers/Fawazeer/Questionsers/Fawazeer/Questions",
                         json={"Dial",
                         json={"Dial": number, "Language": "ar": number, "Language":", "Token": token}, "ar", "Token": token}, timeout= timeout=15).json15).json()
        if q.get()
        if q.get('ErrorCode')('ErrorCode') ==  == 1:
            bot.edit_message1:
            bot.edit_message_text("_text("❌ لقد❌ لقد شاركت اليوم بالف شاركت اليوم بالفعل، جرب غداًعل، جرب غداً.", chat.", chat_id, msg.message_id, reply_markup_id, msg.message_id, reply_m=orange_menu())
            return
       arkup=orange_menu())
            return
 answers = []
        for ques        answers = []
        for ques in q in q["Questions"]["Questions"]:
            for ans in ques["Answers"]:
               :
            for ans in ques["Answers"]:
                if ans["IsCorrect"]:
                    if ans["IsCorrect"]:
                    answers.append({"Question answers.append({"QuestionId": ans["QuestionId"], "AnswerId": ans["Id"]})
                    break
       Id": ans["QuestionId"], "AnswerId": ans["Id"]})
                    break
        # إ # إرسال الحل
        sub = session.postرسال الحل
        sub = session.post("https://services.orange.eg/AP("https://services.orange.eg/APIs/Ramadan2024/api/RIs/Ramadan2024/api/RamadanOffers/FawazeeramadanOffers/Fawazeer/Submit",
                           json={"Dial": number, "Language": "ar/Submit",
                           json={"Dial": number, "Language": "ar", "Token": token", "Token": token, "Answers": answers}, timeout=15)., "Answers": answers}, timeout=15).json()
        if sub.get('ErrorDescription')json()
        if sub.get('ErrorDescription') == "FawazeerSuccess == "FawazeerSuccess":
            bot.edit_message_text("✅ تم":
            bot.edit_message_text("✅ تم حل الفوازير بنجاح! استلمت حل الفوازير بنجاح! استلمت 250 250 ميجا.", chat_id ميجا.", chat_id, msg.message_id, reply_markup=orange_menu, msg.message_id, reply_markup=orange_menu())
        else:
            bot.edit_message())
        else:
            bot.edit_message_text(f"⚠️ {sub.get('Error_text(f"⚠️ {sub.get('ErrorDescription')}", chat_id, msg.messageDescription')}", chat_id, msg.message_id, reply_markup_id, reply_markup=orange_menu())
    except Exception as e=orange_menu())
    except Exception as e:
        bot.edit_message_text(f":
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat❌ خطأ: {str(e)}", chat_id,_id, msg.message_id, reply_markup=orange_menu())

# --- أورانج 500 msg.message_id, reply_markup=orange_menu())

# --- أورانج ميجا (كود رمضان 500 ميجا (كود رمضان) ---
def) ---
def orange_500(chat_id, number, password):
    msg = bot.send_message(chat_id, " orange_500(chat_id, number, password):
    msg = bot.send_message(chat_id, "⏳ جاري استرداد 500 ميجا...")
    try:
        # تسجيل الدخول
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR⏳ جاري استرداد 500 ميجا...")
    try:
        # تسجيل الدخول
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
                   "dialNumber": number, "isAndroid":8yF"},
                   "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        headers = {' True, "lang": "ar", "password": password}
        headers = {'User-Agent': "okhttp/4.User-Agent': "okhttp/4.10.0", 'Content-Type': "application10.0", 'Content-Type': "application/json/json"}
        resp = requests"}
        resp = requests.post(url, json=payload, timeout=15).json.post(url, json=payload, timeout=15).json()
        if 'SignInUserResult()
        if 'SignInUserResult' not in resp:
            bot.edit' not in resp:
            bot.edit_message_text("❌ رقم أو ك_message_text("❌ رقم أو كلمة مرور خلمة مرور خاطئة", chat_id, msg.message_id, reply_markup=orange_menuاطئة", chat_id, msg.message_id, reply_markup=orange_menu())
            return
        user_id = resp['SignIn())
            return
        user_id = resp['SignInUserResult']['UserData']['UserID']

       UserResult']['UserData']['UserID']

        # جلب التوكن
        t # جلب التوكن
        turl = "https://services.orange.eg/url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        tGetToken.svc/GenerateToken"
        tdata = '{"channel":{"ChannelName":"Mobinildata = '{"channel":{"ChannelName":"MAndMe","Password":"ig3yh*mkobinilAndMe","Password":"ig3yh*mk5l42@oj75l42@oj7QAR8yQAR8yF"}}'
        trespF"}}'
        tresp = requests.post(turl = requests.post(turl, headers={'Content-Type': ", headers={'Content-Type': "application/json"}, data=tdata, timeoutapplication/json"}, data=tdata, timeout=15).json()
        ctv = tresp['GenerateTokenResult']['Token=15).json()
        ctv = tresp['GenerateTokenResult']['Token']
        htv = hashlib.sha256((']
        htv = hashlib.sha256((ctvctv + ",{.c][o^ue + ",{.c][o^uecnlkijh*.iomv:QzCFcnlkijh*.iomv:QzCFRcd;drof/zx}Rcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigw;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        # الاسترداد
        rurlest().upper()

        # الاسترداد
        rurl = "https://services.orange. = "https://services.orange.eg/APIs/Promotions/apieg/APIs/Promotions/api/CAF/Redeem"
        rheaders/CAF/Redeem"
        rheaders = {"_ctv": ctv, "_htv": h = {"_ctv": ctv, "_htv": htv, "isEasyLogin": "false", "UserId": usertv, "isEasyLogin": "false", "UserId": user_id,_id, "Content-Type": "application "Content-Type": "application/json"}
        rjson = {"Language": "ar",/json"}
        rjson = {"Language": "ar", "OSVersion": "Android7.0", "Prom "OSVersion": "Android7.0", "PromoCode": "رمضان كريم", "dial":oCode": "رمضان كريم", "dial": number number,
                 "password": password, "Channelname":,
                 "password": password, "Channelname": "MobinilAndMe", " "MobinilAndMe", "ChannelPassword": "ig3yh*mChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"}
       k5l42@oj7QAR8yF"}
        rresp = requests.post(rurl, headers=rheaders, json=rjson, timeout=15). rresp = requests.post(rurl, headers=rheaders, json=rjson, timeout=15).json()
        errjson()
        err = rresp.get('ErrorDescription', = rresp.get('ErrorDescription', ' '')
        if err == "Success":
           ')
        if err == "Success":
            bot.edit_message_text("✅ تم است bot.edit_message_text("✅ تم استلام 500 ميجا بنجاح!", chat_id, msg.message_idلام 500 ميجا بنجاح!", chat_id, msg.message_id, reply, reply_markup=orange_menu())
        elif err == "User is_markup=orange_menu())
        elif err == "User is redeemed before":
            bot.edit_message_text("⚠ redeemed before":
            bot.edit_message_text️ لقد استلمت هذه الهدية("⚠️ لقد استلمت هذه الهدية مسبقاً.", chat_id, msg مسبقاً.", chat_id, msg.message_id, reply_markup=orange_menu())
        else:
            bot.message_id, reply_markup=orange_menu())
        else:
            bot.edit_message_text.edit_message_text(f"❌ {err}", chat_id, msg.message_id, reply(f"❌ {err}", chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f"_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f"❌❌ خطأ: {str(e)}", chat_id, msg خطأ: {str(e)}", chat_id, msg.message_id, reply_markup=orange_menu())

# --- معرف.message_id, reply_markup=orange_menu())

# --- معرفة الرة الرصيد أورانج ---
def orange_صيد أورانج ---
def orange_balance(chat_id, number, password):
   balance(chat_id, number, password):
    msg = bot.send_message(chat_id, "⏳ جاري ج msg = bot.send_message(chat_id, "⏳ جاري جلب الرصيد...")
    try:
        url = "https://www.orange.egلب الرصيد...")
    try:
        url =/apis/gsm/gsmonlinepayment/api/payment/rechargecheck "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
        data =eligibilityForOthers"
        data = {"SelectedUserDial": None, "IsForAnotherRec {"SelectedUserDial": None, "IsForAnotherRecipient": True, "RecipientDial": number, "Dial": numberipient": True, "RecipientDial": number, "Dial": number}
        resp = requests.post(url, json=data, headers={"}
        resp = requests.post(url, json=data, headers={"lang": "enlang": "en"}, timeout=15).json()
        balance ="}, timeout=15).json()
        balance = resp.get('CreditBalance', 'غير متاح')
        bot.edit resp.get('CreditBalance', 'غير متاح')
       _message_text(f"💰 رصيدك: bot.edit_message_text(f"💰 رصيدك: {balance {balance} جن} جنيه", chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ فشل: {str(e)}", chat_id, msg.message_id, reply_markup=orange_menu())

# --- عجلة الحظ أورانج ---
def orange_wheel(chat_id, number, password):
    msg = bot.send_message(chat_id, "🎡يه", chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ فشل: {str(e)}", chat_id, msg.message_id, reply_markup=orange_menu())

# --- عجلة الحظ أورانج ---
def orange_wheel(chat_id, number, password):
    msg = bot.send_message(chat_id, "🎡 جاري تشغيل العجلة...\n[░░░░ جاري تشغيل العجلة...\n[░░░░░░░░░░] 0%")
    try:
       ░░░░░░] 0%")
    try:
        # محاكاة شريط تقدم
 # محاكاة شريط تقدم
        for i,        for i, p in enumerate(["░░░░░░░░░░", "▓▓░░░░░░░░ p in enumerate(["░░░░░░░░░░", "▓▓░░░░░░░░", "▓▓▓▓░░░░░░",", "▓▓▓▓░░░░░░", "▓▓▓▓▓▓░░░░", "▓▓▓▓▓▓░░░░", "▓▓▓▓▓▓▓▓▓ "▓▓▓▓▓▓▓▓▓▓"]):
            time.sleep(0.8)
            bot.edit_message_text(f"🎡 جاري التشغيل▓"]):
            time.sleep(0.8)
            bot.edit_message_text(f"🎡 جاري التشغيل...\n[{p}] {(i+1)*20}...\n[{p}] {(i+1)*20}%", chat_id, msg.message_id)

        # جلب التو%", chat_id, msg.message_id)

        # جلب التوكن
        turl = "https://services.orange.egكن
        turl = "https://services.orange.eg/GetToken.svc/GenerateToken"
        tdata = '{"channel":{"ChannelName":"MobinilAndMe","/GetToken.svc/GenerateToken"
        tdata = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yFPassword":"ig3yh*mk5l42@oj7QAR8yF"}}'
        tresp = requests.post(t"}}'
        tresp = requests.post(turl, headers={'Content-Type': "application/json"}, data=tdata, timeout=15).json()
        ctvurl, headers={'Content-Type': "application/json"}, data=tdata, timeout=15).json()
        = tresp['GenerateTokenResult']['Token']
        htv = hashl ctv = tresp['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85h*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexT^#ASwa?=(lk").encode()).hexdigest().upper()

        # سبينdigest().upper()

        # سبين
        spin_url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFort
        spin_url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortuneune/Spin"
        spin/Spin"
        spin_payload = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk_payload = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
                        "5l42@oj7QAR8yF",
                        "Dial": number, "Language": "en", "Password": passwordDial": number, "Language": "en", "Password": password, "ServiceClassId": "1033"}
        spin_headers, "ServiceClassId": "1033"}
        spin_headers = {"_ctv": ctv, "_htv": h = {"_ctv": ctv, "_htv": htv,tv, "Content-Type": "application/json"}
        spin_resp = requests.post(sp "Content-Type": "application/json"}
        spin_resp = requests.post(spin_url, json=spin_payloadin_url, json=spin_payload, headers=spin_headers, timeout=15).json()
        if "ErrorDescription" in spin_res, headers=spin_headers, timeout=15).json()
        if "ErrorDescription" inp:
            bot.edit_message_text(f"⚠️ {spin_res spin_resp:
            bot.edit_message_text(f"⚠️ {spin_resp['ErrorDescription']}", chat_id, msgp['ErrorDescription']}", chat_id, msg.message_id.message_id, reply_markup=orange_menu())
            return
        offer, reply_markup=orange_menu())
            return
        offer = spin_resp["OfferDetails"]["OfferId"]
        cat = spin_resp["SecondryButtonDetails = spin_resp["OfferDetails"]["OfferId"]
        cat = spin_resp["SecondryButtonDetails"]["CategoryId"]
        offer_name = spin_resp[""]["CategoryId"]
        offer_name = spin_resp["OfferDetails"]["OfferName"]

        #OfferDetails"]["OfferName"]

        # جلب توكن جديد للتأك جلب توكن جديد للتأكيد
        tresp2 = requestsيد
        tresp2 = requests.post(turl, headers={'Content-Type': "application/json"}, data=tdata, timeout=15).json.post(turl, headers={'Content-Type': "application/json"}, data=tdata, timeout=15).json()
        ctv2 = tresp2['()
        ctv2 = tresp2['GenerateTokenResult']['Token']
        htv2 = hasGenerateTokenResult']['Token']
        htv2 = hashlib.sha256((ctv2 +hlib.sha256((ctv2 + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper=(lk").encode()).hexdigest().upper()

        fulfill_url = "https://services.()

        fulfill_url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
        fulfill_payload = {"CategoryId": catorange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
        fulfill_payload = {"CategoryId": cat, "ChannelName": "MobinilAndMe", "ChannelPassword": "ig, "ChannelName": "MobinilAndMe", "ChannelPassword":3yh*mk5l42@oj7 "ig3yh*mk5l42@oj7QAR8yF",
                           "Dial":QAR8yF",
                           "Dial": number, "Language": "en", "OfferId": offer, "Password": password, " number, "Language": "en", "OfferId": offer, "Password": password, "ServiceClassId": "1033"}
        fulfill_headers = {"_ctServiceClassId": "1033"}
        fulfill_headers = {"_ctv": ctv2, "_htv": htv2,v": ctv2, "_htv": htv "Content-Type": "application/json"}
        fulfill_resp = requests2, "Content-Type": "application/json"}
        fulfill_resp = requests.post(fulfill_url, json=fulfill_payload, headers=fulfill_headers, timeout=15)..post(fulfill_url, json=fulfill_payload, headers=fulfill_headers, timeout=15).json()
        ifjson()
        if "Already opted in" in str(fulfill "Already opted in" in str(fulfill_resp):
            result = f"🎡 {offer_name}\n⚠️ أن_resp):
            result = f"🎡 {offer_name}\n⚠️ أنت مشترك بالفعل"
        else:
            result = f"🎡 {offer_name}\n✅ تم الاشترت مشترك بالفعل"
        else:
            result = f"🎡 {offer_name}\n✅ تم الاشتراك بنجاح"
        bot.edit_message_text(result, chat_id, msg.message_idاك بنجاح"
        bot.edit_message_text(result, chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
       , reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ في العجلة: {str(e)}", bot.edit_message_text(f"❌ خطأ في العجلة: {str(e)}", chat_id, msg.message_id, reply_markup=orange_menu())

# chat_id, msg.message_id, reply_markup=orange_menu())

# --- إتصالات 500 ميجا سوشيل --- إتصالات 500 ميجا سوشيل ---
def etisalat_500(chat_id, email, ---
def etisalat_500(chat_id, email, password):
    msg = bot.send_message(chat_id, "⏳ جاري استرداد 500 ميجا سوشيل...")
    password):
    msg = bot.send_message(chat_id, "⏳ جاري استرداد 500 ميجا سوشيل...")
    try:
        token = base64.b64encode(f"{ try:
        token = base64.b64encode(f"{email}:{password}".encodeemail}:{password}".encode()).decode()
        headers = {
            'Authorization': f'Basic {token()).decode()
        headers = {
            'Authorization': f'Basic {token}', 'Content-Type': 'text/xml; charset=UTF-8',
            'User-Agent': 'okhttp/}', 'Content-Type': 'text/xml; charset=UTF-8',
            'User-Agent': 'okhttp5.0.0-alpha.11', 'Language': 'ar'
        }
        login/5.0.0-alpha.11', 'Language': 'ar'
        }
        login_xml_xml = '''<?xml version='1.0' encoding='UTF- = '''<?xml version='1.0' encoding='UTF-8'?><loginRequest><deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt><model8'?><loginRequest><deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt><modelType></Type></modelType><osVersion></osVersion><platform>Android</platform><udid></modelType><osVersion></osVersion><platform>Android</platform><udid></udid></loginRequest>'''
        login_resp = requests.postudid></loginRequest>'''
        login_resp = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", data("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", data=login_xml, headers=headers, timeout=login_xml, headers=headers, timeout=15)
        root = ET=15)
        root = ET.fromstring(login_resp.text)
        number = root.find("dial").text

        redeem.fromstring(login_resp.text)
        number = root.find("dial").text

        redeem_xml = f'''<?xml version='1.0' encoding='UTF-8'?><rtimSubmitOrder><extraProductId>22932</extraProduct_xml = f'''<?xml version='1.0' encoding='UTF-8'?><rtimSubmitOrder><extraProductId>22932</extraId><offerId>22932</offerProductId><offerId>22932</offerId><operationId>REDEEM</operationId><operationId>REDEEM</operationId><productId>RTIM_OFFERS=OfferId><productId>RTIM_OFFERS=Offer_ID:22932;isRTIM:Y</productId><rtimFlag>true</rtim_ID:22932;isRTIM:Y</productId><rtimFlag>true</rtimFlag><subscriberNumber>{number}</subscriberNumber></rtimSubmitOrder>'''
        redeemFlag><subscriberNumber>{number}</subscriberNumber></rtimSubmitOrder>'''
        redeem_resp = requests.post("https://mab.etisalat_resp = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/rtim/rtimSubmitOrder", data=redeem_xml, headers=headers, timeout.com.eg:11003/Saytar/rest/rtim/rtimSubmitOrder", data=redeem_xml, headers=headers, timeout=15)
        if "success" in redeem_resp.text.lower():
            bot.edit_message_text("✅ تم=15)
        if "success" in redeem_resp.text.lower():
            bot.edit_message_text("✅ تم استلام  استلام 500 ميجا سوشيل!",500 ميجا سوشيل!", chat_id, msg.message_id, reply_markup=etisalat_menu())
        else:
            bot.edit_message_text("❌ فش chat_id, msg.message_id, reply_markup=etisalat_menu())
        else:
            bot.edit_message_text("❌ فشل الاسترداد (ربما استلمتها مسبقاً)", chat_id, msg.messageل الاسترداد (ربما استلمتها مسبقاً)", chat_id,_id, reply_markup=etisalat_menu())
    except Exception msg.message_id, reply_markup=etisalat_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id, as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id, reply_markup=etisalat_menu())

# --- مواقيت الصلاة (API مجاني) ---
def prayer_times reply_markup=etisalat_menu())

# --- مواقيت الصلاة (API مجاني) ---
def(chat_id, city="Cairo prayer_times(chat_id, city="Cairo"):
    msg = bot.send_message(chat_id, "⏳ جلب مواقيت الصلاة...")
    try:
        resp = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5", timeout=10).json()
        timings = resp['data']['timings']
        text = f"🕌 مو"):
    msg = bot.send_message(chat_id, "⏳ جلب مواقيت الصلاة...")
    try:
        resp = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5", timeout=10).json()
        timings = resp['data']['timings']
        text = f"🕌 مواقيت الصلاة في {city}:\n"
       اقيت الصلاة في {city}:\n"
        for name, t in timings.items():
            for name, t in timings.items():
            text += f"{name}: {t}\n"
        bot.edit text += f"{name}: {t}\n"
        bot.edit_message_text(text, chat_id, msg.message_id, reply_markup=free_menu())
    except Exception as e:
        bot.edit_message_text(text, chat_id, msg.message_id, reply_markup=free_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id_message_text(f"❌ خطأ: {str(e)}", chat_id, msg.message_id, reply_markup=free_menu())

# --- إنشاء ص, reply_markup=free_menu())

# --- إنشاء صورة نصية (بدون Pillow - باستخدام API خارجي مجاني)ورة نصية (بدون Pillow - باستخدام API خارجي مجاني) ---
def generate_image(chat_id, text):
    msg = bot.send_message(chat_id, " ---
def generate_image(chat_id, text):
    msg = bot.send_message(chat_id, "🖼 جاري إنشاء الصورة...")
    try:
        # استخدام API مجاني لتحويل النص إلى صورة
        url =🖼 جاري إنشاء الصورة...")
    try:
        # استخدام API مجاني لتحويل النص إلى صورة
        url = f"https://quickchart.io/chart?cht=tx&chl={requests.utils.quote(text f"https://quickchart.io/chart?cht=tx&chl={requests.utils.quote(text)}&chs=600x200"
        bot.send_photo()}&chs=600x200"
        bot.send_photo(chat_id, url, caption="✅ تم إنشاء الصورة", replychat_id, url, caption="✅ تم إنشاء الصورة", reply_markup=free_menu())
        bot.delete_message(chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text_markup=free_menu())
        bot.delete_message(chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}",(f"❌ خطأ: {str(e)}", chat_id, msg.message_id, reply_markup=free_menu())

# chat_id, msg.message_id, reply_markup=free_menu())

# ================== معالجة الأزرار والرسائل ==================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_user(message.from ================== معالجة الأزرار والرسائل ==================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_user(message.from_user.id_user.id)
    if is_blocked(message.from_user.id)
    if is_blocked(message.from_user.id):
        bot.reply_to(message, "⛔ أنت محظ):
        bot.reply_to(message, "⛔ أنت محظور.")
        return
    if not bot_active and not is_admin(message.from_user.id):
        bot.reply_to(message, "⚠️ البور.")
        return
    if not bot_active and not is_admin(message.from_user.id):
        bot.reply_to(message, "⚠وت في صيانة حالياً.")
        return️ البوت في صيانة حالياً.")
        return
    if check_sub(message.from_user.id):
        bot.send_message
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"مرحباً {message.from_user.first_name}!\nاختر خدمة:", reply_markup=main_menu())
    else:
       (message.chat.id, f"مرحباً {message.from_user.first_name}!\nاختر خدمة:", reply_markup=main_menu())
    else:
        markup = InlineKeyboardMarkup()
        markup.add( markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.meInlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_ID[1:]}"))
        markup.add(InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
        bot.send_message(message.chat.id, "/{CHANNEL_ID[1:]}"))
        markup.add(InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
        bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القناة أولاً:", reply_markup=markup)

@bot.callback⚠️ يجب الاشتراك في القناة أولاً:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if is_blocked(call.from_user_query_handler(func=lambda call: True)
def callback(call):
    if is_blocked(call.from_user.id):
        bot.answer_callback_query(call.id, "محظور",.id):
        bot.answer_callback_query(call.id, "محظور", show_alert=True)
        return
    if not bot_active and not is_admin(call.from show_alert=True)
        return
    if not bot_active and not is_admin(call.from_user.id) and call.data not in ["check_sub", "back_main"]:
        bot._user.id) and call.data not in ["check_sub", "back_main"]:
        bot.answer_callback_query(call.id, "البوت متوقف", show_alert=True)
        return

    # زر التحقق منanswer_callback_query(call.id, "البوت متوقف", show_alert=True)
        return

    # زر التحقق من الاشتراك
    if call.data == "check_sub":
        if check_sub(call.from الاشتراك
    if call.data == "check_sub":
        if check_sub_user.id):
            bot.edit_message_text("✅ تم التحقق! اختر خدمة:", call.message.chat.id, call.message.message_id, reply_markup=main_menu(call.from_user.id):
            bot.edit_message_text("✅ تم التحقق! اختر خدمة:", call.message.chat.id, call.message.message_id, reply_markup=main())
        else:
            bot.answer_callback_query(call.id, "لم تشترك بعد!", show__menu())
        else:
            bot.answer_callback_query(call.id, "لم تشترك بعد!", show_alert=Truealert=True)
        return

    # لوحة الأدمن
    if call.data.startswith("admin_"):
        if not)
        return

    # لوحة الأدمن
    if call.data.startswith("admin_"):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "غير مصرح", show_alert=True)
            return
        # إحصائيات, "غير مصرح", show_alert=True)
            return
        # إحصائ
        if call.data == "admin_stats":
            conn = sqlite3.connectيات
        if call.data == "admin_stats":
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users')
            count = c.fetchone()[0]
            conn.close()
            bot.edit_message_text(f"📊 إحصائيات:\n👥 مستخدمين: {count}\n👮 أدمنة: {len(admins)}\n⛔ محظورين: {len(blocked_users)}",
                                  call.message.chat.id, call.message('users.db')
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users')
            count = c.fetchone()[0]
            conn.close()
            bot.edit_message_text(f"📊 إحصائيات:\n👥 مستخدمين: {count}\n👮 أدمنة: {len(admins)}\n⛔ محظورين: {len(blocked_users)}",
                                  call.message.chat.id, call.message.message_id, reply_markup=admin_panel_m.message_id, reply_markup=admin_panel_markup())
        # تشغيل/arkup())
        # تشغيل/إيقاف
        elif call.data == "admin_toggle":
            global botإيقاف
        elif call.data == "admin_toggle":
           _active
            new = 0 if get_bot_status() == 1 else global bot_active
            new = 0 if get_bot_status() == 1 else 1
            set_bot_status(new)
            bot_active = (new == 1)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup= 1
            set_bot_status(new)
            bot_active = (new == 1)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_panel_markup())
            bot.answer_callback_query(call.id, f"تم {'تشغيل'admin_panel_markup())
            bot.answer_callback_query(call.id, f"تم {'تشغيل' if new==1 else 'إيقاف'} البوت")
        # إذاعة
        elif call.data == "admin_broadcast":
            if new==1 else 'إيقاف'} البوت")
        # إذاعة
        elif call.data == "admin_broadcast":
            msg = bot.send_message(call.message.chat.id, "أرسل نص الإذاعة msg = bot.send_message(call.message.chat.id, "أرسل نص الإذاعة:")
            bot.register_next_step_handler(msg, broadcast_process)
        # حظر
        elif call.data == "admin_block":
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لح:")
            bot.register_next_step_handler(msg, broadcast_process)
        # حظر
        elif call.data == "admin_block":
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستظره:")
            bot.register_next_stepخدم لحظره:")
            bot.register_next_step_handler(msg, block_user)
        # إلغاء حظر
        elif call.data == "_handler(msg, block_user)
        # إلغاء حظر
        elif call.data == "admin_unblock":
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لإلغاء حظره:")
            bot.register_next_step_handler(msg, unblock_user)
       admin_unblock":
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لإلغاء حظره:")
            bot.register_next_step_handler(msg, unblock_user)
        # إضافة أدمن (للمطور فقط)
        elif call # إضافة أدمن (للمطور فقط)
        elif call.data == "admin_add":
            if str(call.from_user.id) !=.data == "admin_add":
            if str(call.from_user.id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, "المطور فقط", show_alert=True)
                return
            msg = bot.send_message(call str(ADMIN_ID):
                bot.answer_callback_query(call.id, "المطور فقط", show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لإض.message.chat.id, "أرسل ID المستخدم لإضافته كأدمن:")
            bot.register_next_step_handler(msg, add_adminافته كأدمن:")
            bot.register_next_step_handler(msg, add_admin)
        # حذف أدمن
        elif call.data == "admin_remove":
            if str(call.from_user.id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, "المطور فقط)
        # حذف أدمن
        elif call.data == "admin_remove":
            if str(call.from_user.id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, "المطور فقط", show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لح", show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, "أرسل ID المستخدم لحذفه من الأدمنة:")
            bot.register_next_step_handler(msg, remove_admin)
        return

    # التنقل بين القوائم
    ifذفه من الأدمنة:")
            bot.register_next_step_handler(msg, remove_admin)
        return

    # التنقل بين القوائم
    if call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية:", call.message.chat call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية:", call.message.chat.id,.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "orange_menu call.message.message_id, reply_markup=main_menu())
    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج:", call.message.chat.id, call.message.message_id, reply_markup=":
        bot.edit_message_text("🍊 خدمات أورانج:", call.message.chat.id, call.message.message_id, reply_markup=orange_menu())
    elif call.data == "etisalat_menu":
        bot.edit_message_text("📱 خدمات إتصالاتorange_menu())
    elif call.data == "etisalat_menu":
        bot.edit_message_text("📱 خدمات إ:", call.message.chat.id, call.message.message_id, reply_markup=etisalat_menu())
    elif call.data == "free_menu":
        bot.edit_message_text("⚙ خدمات مجانية:", call.message.chat.id, call.message.message_id, reply_markup=freeتصالات:", call.message.chat.id, call.message.message_id, reply_markup=etisalat_menu())
    elif call.data == "free_menu":
        bot.edit_message_text("⚙ خدمات مجانية:", call.message.chat.id, call.message.message_id, reply_markup=free_menu())

    # أزرار أ_menu())

    # أزرار أورانج
    elif call.data == "orange_250":
        msg = bot.send_message(callورانج
    elif call.data == "orange_250":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg.message.chat.id, "أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, ", lambda m: get_number_password(m, "orange_250"))
    elif call.data == "orange_500":
        msg = bot.send_message(callorange_250"))
    elif call.data == "orange_500":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_500"))
    elif call.data == "orange_balance":
        msg = bot.send_message.message.chat.id, "أدخل رقم أورانج (11 رقم):")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_500"))
    elif call.data == "orange_balance":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج:")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_balance"))
    elif call.data == "orange_wheel":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج لعجلة الحظ:")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_wheel"))

    # إتصالات
    elif call.data == "etis(call.message.chat.id, "أدخل رقم أورانج:")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_balance"))
    elif call.data == "orange_wheel":
        msg = bot.send_message(call.message.chat.id, "أدخل رقم أورانج لعجلة الحظ:")
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, "orange_wheel"))

    # إتصالات
    elif call.data == "etisalat_500":
        msg = bot.send_messagealat_500":
        msg = bot.send_message(call.message.chat.id, "أد(call.message.chat.id, "أدخل البريد الإلكتروني (إيميل حساب إتصالات):")
        bot.register_next_step_handler(msg, get_etisalat_password)

    # خدمات مجانية
    elif call.data == "prayerخل البريد الإلكتروني (إيميل حساب إتصالات):")
        bot.register_next_step_handler(msg, get_etisalat_password)

    # خدمات مجانية
    elif call.data == "prayer_times":
        msg =_times":
        msg = bot.send_message(call.message.chat.id, "أدخل اسم المدينة (مثال: Cairo): bot.send_message(call.message.chat.id, "أدخل اسم المدينة (مثال: Cairo):")
        bot.register_next_step_handler(msg, lambda m: prayer_times(m.chat.id, m.text))
    elif call.data == "generate_image":
        msg = bot.send_message(call.message.chat.id, "أدخل النص الذي ت")
        bot.register_next_step_handler(msg, lambda m: prayer_times(m.chat.id, m.text))
    elif call.data == "generate_image":
        msg = bot.send_message(call.message.chat.id, "أدخل النص الذي تريدريد تحويله إلى صورة:")
        bot.register_next_step_handler(msg, lambda m: generate_image(m.chat.id, m.text))

# تحويله إلى صورة:")
        bot.register_next_step_handler(msg, lambda m: generate_image(m.chat.id, m.text))

# دو دوال مساعدة للخطوات
def get_number_password(message, service):
    num = message.text.strip()
    if not (num.isdigit() and len(num) == ال مساعدة للخطوات
def get_number_password(message, service):
    num = message.text.strip()
    if not (num.isdigit() and len(num) == 11 and num.startswith('01')):
        bot.reply_to(message, "رقم غير صالح! أد11 and num.startswith('01')):
        bot.reply_to(message, "رقم غير صالح! أدخل 11 رقمًا يبدأ بـ 01")
        return
    msg = bot.send_message(message.chat.id, "أدخل 11 رقمًا يبدأ بـ 01")
        return
    msg = bot.send_message(message.chat.id, "أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda mخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: process_orange(m, num, service))

def process_orange(message, number, service: process_orange(m, num, service))

def process_orange(message, number, service):
    pwd = message.text.strip()
    if service == "orange_250":
        orange_250(message.chat.id, number, pwd)
    elif service == "):
    pwd = message.text.strip()
    if service == "orange_250":
        orange_250(message.chat.id, number, pwd)
    elif service == "orange_500":
        orange_500(message.chat.id, number, pwd)
    elif service == "orange_balance":
        orange_balance(message.chat.id, number, pwd)
    elif service == "orange_wheel":
        orange_wheel(message.chat.id, numberorange_500":
        orange_500(message.chat.id, number, pwd)
    elif service == "orange_balance":
        orange_, pwd)

def get_etisalatbalance(message.chat.id, number, pwd)
    elif service == "orange_wheel":
        orange_wheel(message.chat.id, number, pwd)

def get_etisalat_password(message):
    email = message.text.strip()
    msg = bot.send_message(message.chat.id, "أدخل كلمة مرور حساب إتصالات:")
    bot.register_next_step_handler(msg, lambda m: etisalat_500(m.chat.id, email, m.text_password(message):
    email = message.text.strip()
    msg = bot.send_message(message.chat.id, "أدخل كلمة مرور حساب إتصالات:")
    bot.register_next_step_handler(msg, lambda m: etisalat_500(m.chat.id, email, m))

# دوال الأدمن
def broadcast_process(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute.text))

# دوال الأدمن
def broadcast_process(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    success = 0
    for uid in users:
        try:
            bot.send_message('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    success = 0
    for uid in users:
        try:
            bot.send_message(uid[0], f"📢 إعلان:\n{message.text}")
            success += 1(uid[0], f"📢 إعلان:\n{message.text}")
            success += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم الإرس
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم الإرسال لـ {success}ال لـ {success} مستخدم", reply_markup=admin_panel_markup())

def block_user(message):
    uid = message.text.strip()
    if مستخدم", reply_markup=admin_panel_markup())

def block_user(message):
    uid = message.text.strip()
    if uid not in blocked_users:
        blocked_users.append(uid)
        save_json('blocked_users.json', blocked_users)
        bot.reply_to(message, f"⛔ تم uid not in blocked_users:
        blocked_users.append(uid)
        save_json('blocked_users.json', blocked_users)
        bot.reply_to(message, f"⛔ تم حظر {uid}")
    else:
        bot.reply_to(message, "محظور بالفعل")
    send_admin_panel(message.chat.id)

def unblock_user(message):
    uid = message.text.strip()
    if uid in blocked_users:
        blocked_users.remove(uid)
        save_json(' حظر {uid}")
    else:
        bot.reply_to(message, "محظور بالفعل")
    send_admin_panel(message.chat.idblocked_users.json', blocked_users)
        bot.reply_to(message)

def unblock_user(message):
    uid = message.text.strip()
    if uid in blocked_users:
        blocked_users.remove(uid)
        save_json('blocked_users.json', blocked_users)
        bot.reply_to(message, f"✅ تم إلغاء حظر {uid}")
    else:
        bot.reply_to(message, ", f"✅ تم إلغاء حظر {uid}")
    else:
        bot.reply_to(message, "ليس في قائمة المحظورين")
    send_admin_panel(message.chat.id)

def add_admin(message):
    uid = message.text.stripليس في قائمة المحظورين")
    send_admin_panel(message.chat.id)

def add_admin(message):
    uid = message.text.strip()
    if uid not in admins:
        admins.append(uid)
        save_json('admins.json', admins)
        bot.reply_to(message, f"✅ تمت إضافة {uid}()
    if uid not in admins:
        admins.append(uid)
        save_json('admins.json', admins)
        bot.reply_to(message, f"✅ تمت إضافة {uid كأدمن")
    else:
        bot.reply_to(message, "هذا المستخدم أدمن بالفعل")
    send_admin_panel(message.chat.id)

def remove_admin(message):
    uid} كأدمن")
    else:
        bot.reply_to(message, "هذا المستخدم أدمن بالفعل")
    send_admin_panel(message.chat.id)

def remove_admin(message):
    uid = message.text.strip()
    if uid in admins:
        admins.remove(uid)
        save_json('admins.json', admins)
        bot.reply_to(message, f"✅ تم حذف {uid} من الأدمنة")
    else:
        = message.text.strip()
    if uid in admins:
        admins.remove(uid)
        save_json('admins.json', admins)
        bot.reply_to(message, f"✅ تم حذف {uid} من الأدمنة")
    else:
        bot.reply_to(message, "ليس أدمن")
    bot.reply_to(message, "ليس أدمن")
    send_admin_panel(message.chat.id)

@bot.message_handler(func=lambda m: True)
def fallback(m):
    if m.text and not m.text.start send_admin_panel(message.chat.id)

@bot.message_handler(func=lambda m: True)
def fallback(m):
    if m.text and not m.text.startswith('/'):
        start_cmd(m)

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    print("✅ البوت يعswith('/'):
        start_cmd(m)

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    print("✅ البوت يعمل بنجاح...")
    print(f"📢 القناةمل بنجاح...")
    print(f"📢 القناة: {CHANNEL_ID}")
    print(f"👑 المطور: {ADMIN_ID}")
    bot.infinity_polling(timeout=60)
