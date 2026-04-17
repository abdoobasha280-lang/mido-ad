import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import hashlib
import time
import re
import base64
import json
import xml.etree.ElementTree as ET

# ========== إعدادات البوت ==========
TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
CHANNEL_USERNAME = "midooojiokjj"
ADMIN_ID = 7721807760
BOT_ACTIVE = True

APPROVED_USERS = []
BANNED_USERS = []

bot = telebot.TeleBot(TOKEN)

# ========== دوال مساعدة ==========
def is_user_subscribed(user_id):
    try:
        return bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id).status in ['member', 'administrator', 'creator']
    except:
        return False

def show_progress(chat_id):
    progress = ["*[░░░░░░░░░░] 0%*", "*[▓▓░░░░░░░░] 25%*", "*[▓▓▓▓░░░░░░] 50%*", "*[▓▓▓▓▓▓░░░░] 75%*", "*[▓▓▓▓▓▓▓▓▓▓] 100%*"]
    msg = bot.send_message(chat_id, progress[0], parse_mode='Markdown')
    for i in range(1, len(progress)):
        time.sleep(1)
        bot.edit_message_text(progress[i], chat_id, msg.message_id, parse_mode='Markdown')
    return True

# ========== دوال البريد المؤقت ==========
def create_random_temp_email():
    try:
        r = requests.get("https://zecora0.serv00.net/fake.php?mail=random", timeout=10)
        if r.status_code == 200 and r.json().get('success'):
            return r.json().get('email')
    except:
        pass
    return None

def get_temp_email_messages(email):
    try:
        r = requests.get(f"https://zecora0.serv00.net/fake-mail.php?action=messages&email={email}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

# ========== دوال خدمات Orange (كاملة) ==========
def check_orange_balance(phone):
    try:
        url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
        payload = {"SelectedUserDial": None, "IsForAnotherRecipient": True, "RecipientDial": phone, "Dial": phone}
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if data.get('ErrorCode') == 0:
            return f"✅ الرصيد: {data.get('CreditBalance', 0)} جنيه"
        return f"❌ خطأ: {data.get('ErrorDescription', 'غير معروف')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_500mg(number, password):
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "9.0.0", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        fox = r.json()['SignInUserResult']['UserData']["UserID"]
        url1 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        data1 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        r1 = requests.post(url1, data=data1, headers={'Content-Type': 'application/json'})
        ctv = r1.json()['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        url4 = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
        headers4 = {"_ctv": ctv, "_htv": htv, "isEasyLogin": "false", "UserId": fox, "Content-Type": "application/json"}
        json4 = {"Language": "ar", "OSVersion": "Android7.0", "PromoCode": "رمضان كريم", "dial": number, "password": password, "Channelname": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"}
        r4 = requests.post(url4, headers=headers4, json=json4)
        err = r4.json()['ErrorDescription']
        if err == "Success":
            return "✅ تم تفعيل 524MG بنجاح!"
        elif "User is redeemed before" in err:
            return "⚠️ تم التفعيل مسبقاً"
        return f"❌ {err}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def spin_wheel(number, password):
    try:
        url2 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        data2 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        r2 = requests.post(url2, data=data2, headers={'Content-Type': 'application/json'})
        ctv = r2.json()['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin"
        payload = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "en", "Password": password, "ServiceClassId": "1033"}
        headers = {'_ctv': ctv, '_htv': htv, 'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers)
        if "ErrorDescription" in r.json():
            return "⚠️ لقد استهلكت المحاولات الثلاث اليومية"
        offer = r.json()["OfferDetails"]["OfferId"]
        CategoryId = r.json()["SecondryButtonDetails"]["CategoryId"]
        offer_name = r.json()["OfferDetails"]["OfferName"]
        time.sleep(2)
        url_f = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
        payload_f = {"CategoryId": CategoryId, "ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "en", "OfferId": offer, "Password": password, "ServiceClassId": "1033"}
        rf = requests.post(url_f, json=payload_f, headers=headers)
        if "Already opted in" in str(rf.json()):
            return f"🎡 {offer_name}\n⚠️ مشترك بالفعل"
        return f"🎡 {offer_name}\n✅ تم الاشتراك"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_orange_business_gifts(number, password):
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        token = r.json()['SignInUserResult']['AccessToken']
        url_g = "https://services.orange.eg/APIs/Gaming/api/Gamification/GetDailyGifts"
        payload_g = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Password": password}
        headers_g = {'Token': token, 'Content-Type': 'application/json'}
        rg = requests.post(url_g, json=payload_g, headers=headers_g)
        gift = rg.json()["Result"]["Gifts"][0]
        Id, Day, LongDescription = gift["Id"], gift["Day"], gift["LongDescription"]
        url_r = "https://services.orange.eg/APIs/Gaming/api/Gamification/RedeemDailyGift"
        payload_r = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Day": Day, "Dial": number, "GiftId": Id, "Language": "ar", "Password": number}
        rr = requests.post(url_r, json=payload_r, headers=headers_g)
        msg = rr.json().get('ErrorDescription', '')
        if "لقد حصلت علي 1000 ميجابايتس" in msg:
            return f"🎁 {LongDescription}\n✅ {msg}"
        return f"❌ {msg}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def activate_orange_2000mb(number, password, serial):
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "9.3.0", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        token = r.json()['SignInUserResult']['AccessToken']
        url_c = "https://services.orange.eg/APIs/Profile/api/UserSubDials/CheckSIMSerial"
        payload_c = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Home4gDial": number, "Home4gSimSerial": serial, "Language": "ar", "VoiceDial": number}
        headers_c = {'Token': token, 'Content-Type': 'application/json'}
        rc = requests.post(url_c, json=payload_c, headers=headers_c)
        if rc.json().get('ErrorDescription') == "Success":
            return "✅ تم تفعيل 2000MB بنجاح!"
        return f"❌ فشل: {rc.json().get('ErrorDescription', 'خطأ')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_orange_fawazeer(number, password):
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload)
        AccessToken = r.json()['SignInUserResult']['AccessToken']
        url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        payload_gen = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}
        headers_gen = {'Token': AccessToken, 'Content-Type': 'application/json'}
        rg = requests.post(url_gen, json=payload_gen, headers=headers_gen)
        Token = rg.json()["Token"]
        url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        rq = requests.post(url_q, json={"Dial": number, "Language": "ar", "Token": Token})
        data = rq.json()
        if data.get('ErrorCode') == 1:
            return "⚠️ لقد دخلت اليوم، جرب غداً"
        answers = [{"QuestionId": a["QuestionId"], "AnswerId": a["Id"]} for q in data["Questions"] for a in q["Answers"] if a["IsCorrect"]]
        url_sub = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        rs = requests.post(url_sub, json={"Dial": number, "Language": "ar", "Token": Token, "Answers": answers})
        if rs.json().get('ErrorDescription') == "FawazeerSuccess":
            return "✅ تم تفعيل Fawazeer بنجاح! (250 ميجا)"
        return f"❌ {rs.json().get('ErrorDescription', 'خطأ')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def extract_fawazeer_questions(number, password):
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "9.3.0", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload)
        AccessToken = r.json()['SignInUserResult']['AccessToken']
        url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        payload_gen = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}
        headers_gen = {'Token': AccessToken, 'Content-Type': 'application/json'}
        rg = requests.post(url_gen, json=payload_gen, headers=headers_gen)
        Token = rg.json()["Token"]
        url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        rq = requests.post(url_q, json={"Dial": number, "Language": "ar", "Token": Token})
        data = rq.json()
        result = "🧩 أسئلة Fawazeer:\n\n"
        for q in data.get("Questions", []):
            correct = next((a for a in q["Answers"] if a["IsCorrect"]), None)
            result += f"❓ {q['Body']}\n✅ الإجابة: {correct['Body'] if correct else 'غير موجود'}\n\n"
        return result if "Questions" in data else "❌ لا توجد أسئلة"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def activate_watchit(number, password):
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload)
        AccessToken = r.json()['SignInUserResult']['AccessToken']
        url_t = "https://services.orange.eg/GetToken.svc/GenerateToken"
        r_t = requests.post(url_t, json={"channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "password": password})
        ctv = r_t.json()['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()
        url_f = "https://services.orange.eg/APIs/Entertainment/api/EagleRevamp/Fulfillment"
        payload_f = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Password": password, "ServiceID": "5"}
        headers_f = {"_ctv": ctv, "_htv": htv, "Content-Type": "application/json"}
        rf = requests.post(url_f, json=payload_f, headers=headers_f)
        if rf.json().get("ErrorCode") == 0:
            return "✅ تم الاشتراك في WatchIT بنجاح"
        elif rf.json().get("ErrorCode") == 1:
            return "ℹ️ أنت مشترك بالفعل"
        return f"❌ {rf.json().get('ErrorDescription', 'خطأ')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== دوال الخدمات الأخرى (Etisalat, Vodafone, WE) ==========
def etisalat_500mg(number, password, email):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml"}
        data = '<loginRequest><deviceId></deviceId><firstLoginAttempt>true</firstLoginAttempt><platform>Android</platform></loginRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", headers=headers, data=data, timeout=30)
        if "true" not in r.text:
            return "❌ بيانات الدخول غير صحيحة"
        msisdn = number[1:] if number.startswith('0') else number
        xml = f'<submitOrderRequest><mabOperation></mabOperation><msisdn>{msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>'
        r2 = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", headers=headers, data=xml, timeout=30)
        return "✅ تم التفعيل" if "true" in r2.text else "❌ فشل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def vodafone_flex(number, password):
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3", "client_id": "my-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        url2 = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
        payload = {"channel": {"name": "MobileApp"}, "orderItem": [{"action": "add", "id": "Flex_2021_523", "itemPrice": [{"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "LE", "value": "130.0"}}}], "product": {"characteristic": [{"name": "offerRank", "value": "1"}, {"name": "TariffID", "value": "523"}], "relatedParty": [{"id": number, "name": "MSISDN", "role": "Subscriber"}]}, "@type": "Access fees Discount"}], "@type": "InterventionTariff"}
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "msisdn": number}
        r2 = requests.post(url2, json=payload, headers=headers)
        return "✅ تم تفعيل خصم فليكس" if "Success With Grace" in r2.text else "⚠️ مفعل مسبقاً"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def we_line_info(number, password):
    try:
        if number.startswith("0"): number = number[1:]
        url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
        payload = {"acctId": number, "password": password, "appLocale": "en-US", "isSelfcare": "Y", "isMobile": "N"}
        r = requests.post(url, json=payload)
        data = r.json()
        return f"📱 رقم الخط: {data['body']['subscriber']['servNumber']}\nالاسم: {data['body']['customer']['custName']}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def get_tiktok_info(username):
    try:
        r = requests.get(f"https://tik-batbyte.vercel.app/tiktok?username={username}", timeout=10)
        data = r.json()
        if 'error' in data:
            return f"❌ {data['error']}"
        return f"📌 {data.get('nickname')}\n🆔 {data.get('user_id')}\n👥 متابعين: {data.get('followers')}\n❤️ {data.get('hearts')}\n🎥 {data.get('videos')}\n🔗 https://tiktok.com/@{username}"
    except Exception as e:
        return f"❌ {str(e)}"

# ========== دوال الخدمات الجديدة ==========
def generate_image(prompt):
    """إنشاء صورة باستخدام API مجاني (Pollinations)"""
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&nologo=true"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content  # return image bytes
        return None
    except:
        return None

def get_prayer_times(city="Cairo", country="Egypt"):
    """جلب مواقيت الصلاة من API الأذان"""
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('code') == 200:
            timings = data['data']['timings']
            date = data['data']['date']['readable']
            result = f"📅 {date}\n📍 {city}, {country}\n\n"
            result += f"الفجر: {timings['Fajr']}\n"
            result += f"الشروق: {timings['Sunrise']}\n"
            result += f"الظهر: {timings['Dhuhr']}\n"
            result += f"العصر: {timings['Asr']}\n"
            result += f"المغرب: {timings['Maghrib']}\n"
            result += f"العشاء: {timings['Isha']}\n"
            return result
        return "❌ تعذر الحصول على المواقيت"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== لوحة تحكم الأدمن ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ هذا الأمر للمسؤول فقط!")
        return
    keyboard = [
        [InlineKeyboardButton("📊 عدد المستخدمين", callback_data='stats')],
        [InlineKeyboardButton(f"{'⏸️ إيقاف البوت' if BOT_ACTIVE else '▶️ تشغيل البوت'}", callback_data='toggle_bot')],
        [InlineKeyboardButton("📢 إذاعة عامة", callback_data='broadcast')]
    ]
    bot.send_message(message.chat.id, "👨‍💻 لوحة التحكم", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'stats')
def stats(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    bot.answer_callback_query(call.id, f"👥 المستخدمون: {len(APPROVED_USERS)}\n🚫 المحظورون: {len(BANNED_USERS)}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'toggle_bot')
def toggle_bot(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    global BOT_ACTIVE
    BOT_ACTIVE = not BOT_ACTIVE
    bot.answer_callback_query(call.id, f"تم {'إيقاف' if not BOT_ACTIVE else 'تشغيل'} البوت")

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast')
def broadcast_prompt(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, "أرسل رسالتك:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    for uid in APPROVED_USERS:
        try:
            bot.send_message(uid, f"📢 إعلان:\n{message.text}")
        except:
            pass
    bot.reply_to(message, "✅ تم الإرسال")

# ========== رسالة البدء ==========
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    if not BOT_ACTIVE:
        bot.reply_to(message, "البوت متوقف للصيانة")
        return
    if not is_user_subscribed(user.id):
        keyboard = [[InlineKeyboardButton("📢 اشترك هنا", url=f'https://t.me/{CHANNEL_USERNAME}')], [InlineKeyboardButton("✅ تأكد", callback_data='check_sub')]]
        bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القناة أولاً:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    if user.id not in APPROVED_USERS and user.id != ADMIN_ID:
        APPROVED_USERS.append(user.id)
    keyboard = [
        [InlineKeyboardButton("🟠 Orange", callback_data='orange')],
        [InlineKeyboardButton("🟢 Etisalat", callback_data='etisalat')],
        [InlineKeyboardButton("🔴 Vodafone", callback_data='vodafone')],
        [InlineKeyboardButton("🔵 WE", callback_data='we')],
        [InlineKeyboardButton("🟣 خدمات أخرى", callback_data='other')],
        [InlineKeyboardButton("ℹ️ معلومات البوت", callback_data='info')]
    ]
    bot.send_message(message.chat.id, f"اهلا بيك يا {user.first_name} في بوت MIDO\nاختر الخدمه التي تريدها ومتنسناش ب اسكرين", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_sub(call):
    if is_user_subscribed(call.from_user.id):
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "لم تشترك بعد", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'info')
def bot_info(call):
    bot.edit_message_text("🤖 بوت MIDO\n💡 للخدمات المجانية\n📢 @midooojiokjj", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='back')]]))

# ========== قوائم الخدمات ==========
@bot.callback_query_handler(func=lambda call: call.data == 'orange')
def orange_menu(call):
    keyboard = [
        [InlineKeyboardButton("عرض 524MG", callback_data='orange_524')],
        [InlineKeyboardButton("عجلة الحظ", callback_data='orange_wheel')],
        [InlineKeyboardButton("هدايا الأعمال", callback_data='orange_business')],
        [InlineKeyboardButton("2000MB", callback_data='orange_2000')],
        [InlineKeyboardButton("فوازير Orange", callback_data='orange_fawazeer')],
        [InlineKeyboardButton("استخراج أسئلة الفوازير", callback_data='orange_extract')],
        [InlineKeyboardButton("اشتراك WatchIT", callback_data='orange_watchit')],
        [InlineKeyboardButton("معرفة الرصيد", callback_data='orange_balance')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Orange:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat')
def etisalat_menu(call):
    keyboard = [
        [InlineKeyboardButton("500 ميجا سوشيال", callback_data='etisalat_500')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Etisalat:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone')
def vodafone_menu(call):
    keyboard = [
        [InlineKeyboardButton("خصم فليكس", callback_data='vodafone_flex')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Vodafone:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'we')
def we_menu(call):
    keyboard = [
        [InlineKeyboardButton("معلومات الخط", callback_data='we_info')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات WE:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'other')
def other_menu(call):
    keyboard = [
        [InlineKeyboardButton("🔍 TikTok", callback_data='tiktok')],
        [InlineKeyboardButton("📧 بريد مؤقت", callback_data='temp_email')],
        [InlineKeyboardButton("🎨 إنشاء صورة", callback_data='generate_image')],
        [InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data='prayer_times')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات أخرى:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== دوال تنفيذ الخدمات ==========
def get_orange_number(message, service):
    num = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', num):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: exec_orange(m, num, service))

def exec_orange(message, number, service):
    pwd = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    if service == '524':
        result = redeem_500mg(number, pwd)
    elif service == 'wheel':
        result = spin_wheel(number, pwd)
    elif service == 'business':
        result = redeem_orange_business_gifts(number, pwd)
    elif service == '2000':
        msg = bot.reply_to(message, "أدخل الرقم التسلسلي للشريحة:")
        bot.register_next_step_handler(msg, lambda m: exec_orange_2000(m, number, pwd))
        return
    elif service == 'fawazeer':
        result = redeem_orange_fawazeer(number, pwd)
    elif service == 'extract':
        result = extract_fawazeer_questions(number, pwd)
    elif service == 'watchit':
        result = activate_watchit(number, pwd)
    elif service == 'balance':
        result = check_orange_balance(number)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='orange')]]))

def exec_orange_2000(message, number, password):
    serial = message.text.strip()
    show_progress(message.chat.id)
    result = activate_orange_2000mb(number, password, serial)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='orange')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_524')
def orange_524(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, '524'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_wheel')
def orange_wheel(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, 'wheel'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_business')
def orange_business(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, 'business'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_2000')
def orange_2000(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, '2000'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_fawazeer')
def orange_fawazeer(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, 'fawazeer'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_extract')
def orange_extract(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, 'extract'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_watchit')
def orange_watchit(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, 'watchit'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_balance')
def orange_balance(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_number(m, 'balance'))

# Etisalat
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_500')
def etisalat_500(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Etisalat وكلمة المرور والبريد (مثال: 01123456789 pass email@example.com):")
    bot.register_next_step_handler(msg, exec_etisalat)

def exec_etisalat(message):
    parts = message.text.strip().split()
    if len(parts) < 3:
        bot.reply_to(message, "بيانات غير كافية")
        return
    number, password, email = parts[0], parts[1], parts[2]
    show_progress(message.chat.id)
    result = etisalat_500mg(number, password, email)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

# Vodafone
@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_flex')
def vodafone_flex(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Vodafone وكلمة المرور:")
    bot.register_next_step_handler(msg, exec_vodafone)

def exec_vodafone(message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "بيانات غير كافية")
        return
    number, password = parts[0], parts[1]
    show_progress(message.chat.id)
    result = vodafone_flex(number, password)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='vodafone')]]))

# WE
@bot.callback_query_handler(func=lambda call: call.data == 'we_info')
def we_info(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم WE وكلمة المرور:")
    bot.register_next_step_handler(msg, exec_we)

def exec_we(message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "بيانات غير كافية")
        return
    number, password = parts[0], parts[1]
    show_progress(message.chat.id)
    result = we_line_info(number, password)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='we')]]))

# TikTok
@bot.callback_query_handler(func=lambda call: call.data == 'tiktok')
def tiktok(call):
    msg = bot.send_message(call.message.chat.id, "أدخل اسم المستخدم (بدون @):")
    bot.register_next_step_handler(msg, exec_tiktok)

def exec_tiktok(message):
    username = message.text.strip()
    result = get_tiktok_info(username)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='other')]]))

# البريد المؤقت
@bot.callback_query_handler(func=lambda call: call.data == 'temp_email')
def temp_menu(call):
    keyboard = [
        [InlineKeyboardButton("إنشاء بريد عشوائي", callback_data='temp_create')],
        [InlineKeyboardButton("عرض الرسائل", callback_data='temp_show')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='other')]
    ]
    bot.edit_message_text("البريد المؤقت:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'temp_create')
def temp_create(call):
    email = create_random_temp_email()
    if email:
        bot.edit_message_text(f"✅ بريدك: `{email}`", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')]]))
    else:
        bot.edit_message_text("❌ فشل", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'temp_show')
def temp_show_prompt(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني:")
    bot.register_next_step_handler(msg, temp_show_messages)

def temp_show_messages(message):
    email = message.text.strip()
    msgs = get_temp_email_messages(email)
    if msgs:
        txt = f"رسائل {email}:\n"
        for m in msgs[:3]:
            txt += f"من: {m.get('from')}\nموضوع: {m.get('subject')}\n\n"
        bot.send_message(message.chat.id, txt)
    else:
        bot.send_message(message.chat.id, "لا توجد رسائل")
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='temp_email')]]))

# إنشاء الصورة
@bot.callback_query_handler(func=lambda call: call.data == 'generate_image')
def generate_image_prompt(call):
    msg = bot.send_message(call.message.chat.id, "أرسل وصف الصورة التي تريد إنشاءها:")
    bot.register_next_step_handler(msg, process_image_generation)

def process_image_generation(message):
    prompt = message.text.strip()
    if len(prompt) < 3:
        bot.reply_to(message, "الوصف قصير جداً")
        return
    status_msg = bot.reply_to(message, "⏳ جاري إنشاء الصورة...")
    img_data = generate_image(prompt)
    if img_data:
        bot.send_photo(message.chat.id, img_data, caption=f"🎨 {prompt}")
        bot.delete_message(message.chat.id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ فشل إنشاء الصورة، حاول مرة أخرى", message.chat.id, status_msg.message_id)
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='other')]]))

# مواقيت الصلاة
@bot.callback_query_handler(func=lambda call: call.data == 'prayer_times')
def prayer_times_prompt(call):
    msg = bot.send_message(call.message.chat.id, "أدخل اسم المدينة (مثال: Cairo, Alexandria):")
    bot.register_next_step_handler(msg, process_prayer_times)

def process_prayer_times(message):
    city = message.text.strip()
    status_msg = bot.reply_to(message, "⏳ جاري جلب المواقيت...")
    result = get_prayer_times(city)
    bot.edit_message_text(result, message.chat.id, status_msg.message_id)
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='other')]]))

# زر الرجوع العام
@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back(call):
    start(call.message)

# ========== تشغيل البوت ==========
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
