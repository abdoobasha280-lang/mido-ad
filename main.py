import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests
import hashlib
import json
import time
import re
import base64
from base64 import b64encode
import xml.etree.ElementTree as ET

# ========== إعدادات البوت ==========
TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
CHANNEL_USERNAME = "midooojiokjj"
ADMINS = [7721807760]  # المطور الوحيد
BOT_ACTIVE = True
SERVICE_STATUS = {
    'orange': True,
    'etisalat': True,
    'vodafone': True,
    'we': True,
    'tiktok': True,
    'other': True
}
TEMPORARY_EMAIL_API = "https://zecora0.serv00.net"
TIKTOK_API_URL = "https://tik-batbyte.vercel.app/tiktok?username="

bot = telebot.TeleBot(TOKEN)
APPROVED_USERS = []
BANNED_USERS = []

# ========== دوال مساعدة ==========
def is_bot_active():
    return BOT_ACTIVE

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
def get_temp_email_domains():
    try:
        r = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=domains", timeout=10)
        if r.status_code == 200 and r.json().get('success'):
            return r.json().get('domains', [])
    except:
        pass
    return []

def create_random_temp_email():
    try:
        r = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=random", timeout=10)
        if r.status_code == 200 and r.json().get('success'):
            return r.json().get('email')
    except:
        pass
    return None

def create_custom_temp_email(username, domain):
    try:
        r = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=custom&name={username}&domain={domain}", timeout=10)
        if r.status_code == 200 and r.json().get('success'):
            return r.json().get('email')
    except:
        pass
    return None

def get_temp_email_messages(email):
    try:
        r = requests.get(f"{TEMPORARY_EMAIL_API}/fake-mail.php?action=messages&email={email}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def delete_temp_email(email):
    try:
        r = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=delete-email&email={email}", timeout=10)
        return r.json().get('success', False)
    except:
        return False

# ========== خدمة أورانج: معرفة الرصيد ==========
def check_orange_balance(phone):
    try:
        url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
        payload = {"SelectedUserDial": None, "IsForAnotherRecipient": True, "RecipientDial": phone, "Dial": phone}
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json', 'lang': 'en'}
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        if data.get('ErrorCode') == 0:
            return f"✅ الرصيد الحالي: {data.get('CreditBalance', 0)} جنيه"
        return f"❌ خطأ: {data.get('ErrorDescription', 'غير معروف')}"
    except Exception as e:
        return f"❌ خطأ في الاتصال: {str(e)}"

# ========== خدمة أورانج: تفعيل عرض 524 ميجا (كود رمضان كريم) ==========
def redeem_orange_500mg(number, password):
    show_progress(chat_id)  # سيتم تمرير chat_id من الخارج
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
            return "✅ تم تفعيل 524 ميجا بنجاح!"
        elif "User is redeemed before" in err:
            return "⚠️ لقد قمت بتفعيل هذا العرض من قبل"
        return f"❌ {err}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمة أورانج: عجلة الحظ ==========
def spin_orange_wheel(number, password):
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
            return f"🎡 {offer_name}\n⚠️ أنت مشترك بالفعل في هذا العرض"
        return f"🎡 {offer_name}\n✅ تم الاشتراك في العرض بنجاح"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمة أورانج: Business Gifts (هدية 1000 ميجا يومية) ==========
def orange_business_gifts(number, password):
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

# ========== خدمة أورانج: تفعيل 2000 ميجا (باستخدام الرقم التسلسلي) ==========
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
            return "✅ تم تفعيل 2000 ميجا بنجاح!"
        return f"❌ فشل التفعيل: {rc.json().get('ErrorDescription', 'خطأ')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمة أورانج: فوازير رمضان (حل تلقائي) ==========
def solve_orange_fawazeer(number, password):
    try:
        # تسجيل الدخول
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {"appVersion": "9.0.1", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"}, "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password}
        r = requests.post(url, json=payload)
        AccessToken = r.json()['SignInUserResult']['AccessToken']
        # جلب التوكن
        url_gen = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        payload_gen = {"ChannelName": "MobinilAndMe", "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF", "Dial": number, "Language": "ar", "Module": "0", "Password": password}
        headers_gen = {'Token': AccessToken, 'Content-Type': 'application/json'}
        rg = requests.post(url_gen, json=payload_gen, headers=headers_gen)
        Token = rg.json()["Token"]
        # جلب الأسئلة
        url_q = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        rq = requests.post(url_q, json={"Dial": number, "Language": "ar", "Token": Token})
        data = rq.json()
        if data.get('ErrorCode') == 1:
            return "⚠️ لقد دخلت على الفوازير اليوم! جرب غداً."
        questions = data["Questions"]
        answers = []
        for q in questions:
            for a in q["Answers"]:
                if a["IsCorrect"]:
                    answers.append({"QuestionId": a["QuestionId"], "AnswerId": a["Id"]})
                    break
        # إرسال الإجابات
        url_sub = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        rs = requests.post(url_sub, json={"Dial": number, "Language": "ar", "Token": Token, "Answers": answers})
        if rs.json().get('ErrorDescription') == "FawazeerSuccess":
            return "✅ تم حل الفوازير بنجاح! تم إضافة 250 ميجا إلى رصيدك 🎉"
        else:
            return f"❌ {rs.json().get('ErrorDescription', 'خطأ غير معروف')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمة أورانج: استخراج أسئلة وإجابات الفوازير ==========
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
        result = "🧩 أسئلة وإجابات Fawazeer:\n\n"
        for q in data.get("Questions", []):
            correct = next((a for a in q["Answers"] if a["IsCorrect"]), None)
            result += f"❓ {q['Body']}\n✅ الإجابة الصحيحة: {correct['Body'] if correct else 'غير موجود'}\n\n"
        return result if "Questions" in data else "❌ لا توجد أسئلة متاحة حالياً"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمة أورانج: تفعيل WatchIT ==========
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
            return "✅ تم تفعيل اشتراك WatchIT بنجاح!"
        elif rf.json().get("ErrorCode") == 1:
            return "ℹ️ أنت مشترك بالفعل في WatchIT"
        return f"❌ {rf.json().get('ErrorDescription', 'خطأ')}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمات إتصالات (Etisalat) ==========
def redeem_etisalat_500mg_social(number, password, email):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml", "APP-Version": "27.0.0"}
        data = '<loginRequest><deviceId></deviceId><firstLoginAttempt>true</firstLoginAttempt><platform>Android</platform></loginRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", headers=headers, data=data, timeout=30)
        if "true" not in r.text:
            return "❌ بيانات الدخول غير صحيحة"
        msisdn = number[1:] if number.startswith('0') else number
        xml = f'<submitOrderRequest><mabOperation></mabOperation><msisdn>{msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>'
        r2 = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", headers=headers, data=xml, timeout=30)
        if "true" in r2.text:
            return "✅ تم تفعيل 500 ميجا سوشيال بنجاح!"
        return "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_etisalat_500mg_streaming(number, password, email):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml", "APP-Version": "27.0.0"}
        data = '<loginRequest><deviceId></deviceId><firstLoginAttempt>true</firstLoginAttempt><platform>Android</platform></loginRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", headers=headers, data=data, timeout=30)
        if "true" not in r.text:
            return "❌ بيانات الدخول غير صحيحة"
        msisdn = number[1:] if number.startswith('0') else number
        xml = f'<submitOrderRequest><mabOperation></mabOperation><msisdn>{msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_2_STREAMING_UNITS</productName></submitOrderRequest>'
        r2 = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", headers=headers, data=xml, timeout=30)
        if "true" in r2.text:
            return "✅ تم تفعيل 500 ميجا ستريمنج بنجاح!"
        return "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_etisalat_100_units(email, password):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml"}
        data = '<loginRequest><deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt><platform>Android</platform></loginRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", headers=headers, data=data, timeout=30)
        root = ET.fromstring(r.text)
        number = root.find(".//dial").text
        payload = f'<submitOrderRequest><mabOperation></mabOperation><msisdn>{number}</msisdn><operation>ACTIVATE</operation><parameters><parameter><name>Offer_ID</name><value>23214</value></parameter><parameter><name>isRTIM</name><value>Y</value></parameter></parameters><productName>TWIST_TV</productName></submitOrderRequest>'
        r2 = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/submitOrder", headers=headers, data=payload, timeout=30)
        if "<status>true</status>" in r2.text:
            return "✅ تم تفعيل هدية 100 وحدة بنجاح!"
        return "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_etisalat_daily_gift(email, password):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml"}
        data = '<loginRequest><deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt><platform>Android</platform></loginRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", headers=headers, data=data, timeout=30)
        root = ET.fromstring(r.text)
        number = root.find(".//dial").text
        url_g = f"https://mab.etisalat.com.eg:11003/Saytar/rest/dailyTipsWS/dailyTipsExtraGift?req=<dialAndLanguageRequest><subscriberNumber>{number}</subscriberNumber><language>1</language></dialAndLanguageRequest>"
        rg = requests.get(url_g, headers=headers)
        root_g = ET.fromstring(rg.text)
        for gift in root_g.findall(".//dailyGift"):
            if gift.find("redeemed").text == "false":
                gift_id = gift.find(".//param[@name='GIFT_ID']/value").text
                amount = gift.find(".//param[@name='AMOUNT']/value").text
                sub_payload = f'<dailyTipsSubmitRequest><operationId>REDEEM</operationId><params><param><name>GIFT_ID</name><value>{gift_id}</value></param><param><name>AMOUNT</name><value>{amount}</value></param><param><name>GIFT_TYPE</name><value>DailyTip</value></param><param><name>GIFT_CATEGORY</name><value>Main</value></param></params><productId>DAILY_TIPS_GIFT</productId><subscriberNumber>{number}</subscriberNumber></dailyTipsSubmitRequest>'
                rs = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/dailyTipsWS/submitOrder", headers=headers, data=sub_payload, timeout=30)
                if "<status>true</status>" in rs.text:
                    return f"🎉 تم تفعيل الهدية اليومية ({amount} ميجا) بنجاح!"
                return "❌ فشل التفعيل"
        return "⚠️ لا توجد هدايا متاحة للتفعيل اليوم"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def activate_etisalat_shahid_vip(email, password):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml", "APP-Version": "27.0.0"}
        data = '<loginRequest><deviceId></deviceId><firstLoginAttempt>true</firstLoginAttempt><platform>Android</platform></loginRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", headers=headers, data=data, timeout=30)
        root = ET.fromstring(r.text)
        number = root.find("dial").text
        headers["APP-Version"] = "33.1.0"
        headers["Language"] = "ar"
        payload = f'<generalSubmitOrderRequest><category></category><contactDial></contactDial><msisdn>{number}</msisdn><operation>ACTIVATE</operation><passParameters/><productName>SHAHID_HYBRID_VIP</productName></generalSubmitOrderRequest>'
        r2 = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/General/submitOrder", headers=headers, data=payload, timeout=30)
        if "<status>true</status>" in r2.text:
            return "✅ تم تفعيل اشتراك شاهد VIP بنجاح!"
        return "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def delete_etisalat_account(email, password):
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml"}
        payload = f'<deleteUserAccountRequest><email>{email}</email></deleteUserAccountRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/quickAccess/deleteAccount", headers=headers, data=payload, timeout=30)
        if "<status>true</status>" in r.text:
            return "✅ تم حذف حساب ماي اتصالات بنجاح"
        return "❌ فشل حذف الحساب"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمات فودافون ==========
def redeem_vodafone_flex_discount(number, password):
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3", "client_id": "my-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        url2 = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
        payload = {"channel": {"name": "MobileApp"}, "orderItem": [{"action": "add", "id": "Flex_2021_523", "itemPrice": [{"name": "OriginalPrice", "price": {"taxIncludedAmount": {"unit": "LE", "value": "130.0"}}}], "product": {"characteristic": [{"name": "offerRank", "value": "1"}, {"name": "TariffID", "value": "523"}], "relatedParty": [{"id": number, "name": "MSISDN", "role": "Subscriber"}]}, "@type": "Access fees Discount"}], "@type": "InterventionTariff"}
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "msisdn": number}
        r2 = requests.post(url2, json=payload, headers=headers)
        if "Success With Grace" in r2.text:
            return "✅ تم تفعيل خصم 50% على باقة فليكس بنجاح!"
        return "⚠️ قد يكون العرض مفعل مسبقاً أو غير متاح"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_vodafone_gifts(number, password):
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3", "client_id": "my-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        promo = {"promoId": "2633", "channelId": "1", "wlistId": "2553", "contextualPromoId": "13", "triggerId": "189"}
        success = 0
        for _ in range(6):
            rr = requests.post("https://mobile.vodafone.com.eg/mobile-app/promo/unifiedRedeemPromo?lang=ar", json=promo, headers=headers)
            if rr.status_code == 200:
                success += 1
        if success:
            return f"✅ تم تفعيل {success} من هدايا فودافون بنجاح!"
        return "❌ فشل في تفعيل الهدايا"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_vodafone_plus_discount(number, password):
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3", "client_id": "my-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "msisdn": number}
        r2 = requests.get("https://web.vodafone.com.eg/services/dxl/promo/promotion?%40type=Promo&%24.context.type=scratchCoupon", headers=headers)
        if "Promo_TX_ID" in r2.text:
            return "✅ تم تفعيل العرض مسبقاً"
        if "No Data Found" not in r2.text:
            return "✅ تم تفعيل خصم باقة Plus 20,000 بنجاح!"
        return "⚠️ لا يوجد عرض متاح حالياً"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_vodafone_summer_gift(number, password):
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "95fd95fb-7489-4958-8ae6-d31a525cd20a", "client_id": "ana-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "msisdn": number}
        r2 = requests.get("https://web.vodafone.com.eg/services/dxl/promo/promotion?@type=Promo&$.context.type=massSummerPromo25", headers=headers)
        if r2.status_code == 404:
            return "⚠️ لقد حصلت على هدية الصيف من قبل"
        data = r2.json()
        amount = data[1]["characteristics"][0]["value"]
        return f"✅ تم تفعيل هدية الصيف {amount} ميجا بنجاح!"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def distribute_vodafone_flex(owner_number, owner_password, target_number, percentage):
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": owner_number, "password": owner_password, "grant_type": "password", "client_secret": "95fd95fb-7489-4958-8ae6-d31a525cd20a", "client_id": "ana-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "msisdn": owner_number}
        payload = {"name": "FlexFamily", "type": "SendInvitation", "category": [{"value": "523", "listHierarchyId": "PackageID"}], "parts": {"member": [{"id": [{"value": owner_number, "schemeName": "MSISDN"}], "type": "Owner"}, {"id": [{"value": target_number, "schemeName": "MSISDN"}], "type": "Member"}], "characteristicsValue": {"characteristicsValue": [{"characteristicName": "quotaDist1", "value": percentage, "type": "percentage"}]}}}
        r2 = requests.post("https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup", json=payload, headers=headers)
        if '{}' in r2.text:
            return "✅ تم إرسال دعوة توزيع الفليكسات بنجاح"
        return "❌ فشل إرسال الدعوة"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمات WE ==========
def get_we_line_info(number, password):
    try:
        if number.startswith("0"): number = number[1:]
        url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
        payload = {"acctId": number, "password": password, "appLocale": "en-US", "isSelfcare": "Y", "isMobile": "N"}
        r = requests.post(url, json=payload)
        data = r.json()
        return f"📱 رقم الخط: {data['body']['subscriber']['servNumber']}\n👤 الاسم: {data['body']['customer']['custName']}\n📝 نظام الخط: {data['body']['subscriber']['writtenLang']}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def get_we_usage(number, password):
    try:
        if number.startswith("0"): number = number[1:]
        url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
        payload = {"acctId": number, "password": password, "appLocale": "en-US", "isSelfcare": "Y", "isMobile": "N"}
        r = requests.post(url, json=payload)
        data = r.json()
        token = data['body']['token']
        sub_id = data['body']['subscriber']['subscriberId']
        headers = {"csrftoken": token}
        query = {"subscriberId": sub_id, "needQueryPoint": True}
        r2 = requests.post("https://my.te.eg/echannel/service/besapp/base/rest/busiservice/cz/cbs/bb/queryFreeUnit", json=query, headers=headers)
        result = "📊 معلومات الاستهلاك:\n\n"
        for pkg in r2.json().get('body', []):
            result += f"⦿ {pkg.get('offerName')}:\n"
            result += f"   المستخدم: {pkg.get('used')} / {pkg.get('total')}\n"
            result += f"   المتبقي: {pkg.get('remain')}\n"
            result += f"   ينتهي: {pkg.get('expireTime')}\n\n"
        return result
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== خدمات أخرى ==========
def get_tiktok_info(username):
    try:
        r = requests.get(f"{TIKTOK_API_URL}{username}", timeout=10)
        data = r.json()
        if 'error' in data:
            return None, f"❌ {data['error']}"
        caption = f"📌 الاسم: {data.get('nickname')}\n🆔 المعرف: {data.get('user_id')}\n👥 متابعين: {data.get('followers')}\n❤️ إعجابات: {data.get('hearts')}\n🎥 فيديوهات: {data.get('videos')}\n🔗 الرابط: https://tiktok.com/@{username}"
        return data.get('profile_picture'), caption
    except Exception as e:
        return None, f"❌ خطأ: {str(e)}"

def check_wallet_status(number):
    try:
        url = "https://fep.kashier.io/v3/orders"
        payload = {"apiOperation": "INITIATE_R2P", "paymentMethod": {"type": "wallet"}, "customer": {"mobilePhone": number}, "order": {"reference": "34d82fe7-6923-4c1f-abfb-7989d9973ebd", "amount": "5", "currency": "EGP"}}
        headers = {'Kashier-Hash': "24a66f31d9e032af51f629553f156cfa8477e8952cdafa356a8389cd64051056", 'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers)
        msg = r.json().get("response", {}).get("transactionResponseMessage", {}).get("ar", "")
        if "غير مسجل" in msg:
            return "❌ الرقم غير مسجل في أي محفظة إلكترونية"
        if r.json().get("response", {}).get("status") == "SUCCESS":
            return "✅ الرقم مسجل في محفظة إلكترونية ويمكن إرسال طلب الدفع"
        return f"⚠️ {msg}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== لوحة تحكم الأدمن ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "⛔ هذا الأمر للمسؤولين فقط!")
        return
    keyboard = [
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data='user_mgmt')],
        [InlineKeyboardButton("⚙️ إدارة الخدمات", callback_data='service_mgmt')],
        [InlineKeyboardButton("📊 إحصاءات", callback_data='stats')],
        [InlineKeyboardButton("📢 إشعار عام", callback_data='broadcast')]
    ]
    bot.send_message(message.chat.id, "👨‍💻 لوحة تحكم الأدمن", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'user_mgmt')
def user_mgmt(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("📋 قائمة المستخدمين", callback_data='list_users')],
        [InlineKeyboardButton("➕ إضافة مستخدم", callback_data='add_user')],
        [InlineKeyboardButton("➖ إزالة مستخدم", callback_data='remove_user')],
        [InlineKeyboardButton("⛔ حظر مستخدم", callback_data='ban_user')],
        [InlineKeyboardButton("✅ إلغاء حظر", callback_data='unban_user')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')]
    ]
    bot.edit_message_text("إدارة المستخدمين", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'service_mgmt')
def service_mgmt(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton(f"Orange {'✅' if SERVICE_STATUS['orange'] else '❌'}", callback_data='toggle_orange')],
        [InlineKeyboardButton(f"Etisalat {'✅' if SERVICE_STATUS['etisalat'] else '❌'}", callback_data='toggle_etisalat')],
        [InlineKeyboardButton(f"Vodafone {'✅' if SERVICE_STATUS['vodafone'] else '❌'}", callback_data='toggle_vodafone')],
        [InlineKeyboardButton(f"WE {'✅' if SERVICE_STATUS['we'] else '❌'}", callback_data='toggle_we')],
        [InlineKeyboardButton(f"TikTok {'✅' if SERVICE_STATUS['tiktok'] else '❌'}", callback_data='toggle_tiktok')],
        [InlineKeyboardButton(f"خدمات أخرى {'✅' if SERVICE_STATUS['other'] else '❌'}", callback_data='toggle_other')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')]
    ]
    bot.edit_message_text("إدارة الخدمات", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data.startswith('toggle_'))
def toggle_service(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    service = call.data.split('_')[1]
    SERVICE_STATUS[service] = not SERVICE_STATUS[service]
    bot.answer_callback_query(call.id, f"تم {'تفعيل' if SERVICE_STATUS[service] else 'تعطيل'} {service}")
    service_mgmt(call)

@bot.callback_query_handler(func=lambda call: call.data == 'stats')
def stats(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    text = f"📊 إحصائيات البوت:\n👥 الأدمن: {len(ADMINS)}\n✅ المستخدمين الموافق عليهم: {len(APPROVED_USERS)}\n⛔ المحظورين: {len(BANNED_USERS)}\n🟢 حالة البوت: {'نشط' if BOT_ACTIVE else 'متوقف'}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast')
def broadcast_prompt(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, "أرسل رسالتك للنشر:")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(message):
    if message.from_user.id not in ADMINS:
        return
    for uid in APPROVED_USERS + ADMINS:
        try:
            bot.send_message(uid, f"📢 إعلان من الإدارة:\n\n{message.text}")
            time.sleep(0.1)
        except:
            pass
    bot.reply_to(message, "✅ تم إرسال الإشعار لجميع المستخدمين")

@bot.callback_query_handler(func=lambda call: call.data == 'list_users')
def list_users(call):
    if call.from_user.id not in ADMINS:
        return
    txt = "👥 قائمة المستخدمين الموافق عليهم:\n" + "\n".join(str(u) for u in APPROVED_USERS) if APPROVED_USERS else "لا يوجد مستخدمون"
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='user_mgmt')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'add_user')
def add_user_prompt(call):
    if call.from_user.id not in ADMINS:
        return
    msg = bot.send_message(call.message.chat.id, "أرسل معرف المستخدم (ID):")
    bot.register_next_step_handler(msg, add_user_exec)

def add_user_exec(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        uid = int(message.text.strip())
        if uid in APPROVED_USERS:
            bot.reply_to(message, "المستخدم موجود بالفعل")
        elif uid in ADMINS:
            bot.reply_to(message, "هذا أدمن")
        else:
            APPROVED_USERS.append(uid)
            bot.reply_to(message, f"✅ تم إضافة المستخدم {uid}")
    except:
        bot.reply_to(message, "خطأ: المعرف يجب أن يكون رقماً")

@bot.callback_query_handler(func=lambda call: call.data == 'remove_user')
def remove_user_prompt(call):
    if call.from_user.id not in ADMINS:
        return
    msg = bot.send_message(call.message.chat.id, "أرسل معرف المستخدم للإزالة:")
    bot.register_next_step_handler(msg, remove_user_exec)

def remove_user_exec(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        uid = int(message.text.strip())
        if uid in APPROVED_USERS:
            APPROVED_USERS.remove(uid)
            bot.reply_to(message, f"✅ تم إزالة المستخدم {uid}")
        else:
            bot.reply_to(message, "المستخدم غير موجود في القائمة")
    except:
        bot.reply_to(message, "خطأ")

@bot.callback_query_handler(func=lambda call: call.data == 'ban_user')
def ban_user_prompt(call):
    if call.from_user.id not in ADMINS:
        return
    msg = bot.send_message(call.message.chat.id, "أرسل معرف المستخدم للحظر:")
    bot.register_next_step_handler(msg, ban_user_exec)

def ban_user_exec(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        uid = int(message.text.strip())
        if uid in ADMINS:
            bot.reply_to(message, "لا يمكن حظر أدمن")
        elif uid in BANNED_USERS:
            bot.reply_to(message, "المستخدم محظور بالفعل")
        else:
            BANNED_USERS.append(uid)
            if uid in APPROVED_USERS:
                APPROVED_USERS.remove(uid)
            bot.reply_to(message, f"✅ تم حظر المستخدم {uid}")
    except:
        bot.reply_to(message, "خطأ")

@bot.callback_query_handler(func=lambda call: call.data == 'unban_user')
def unban_user_prompt(call):
    if call.from_user.id not in ADMINS:
        return
    msg = bot.send_message(call.message.chat.id, "أرسل معرف المستخدم لإلغاء الحظر:")
    bot.register_next_step_handler(msg, unban_user_exec)

def unban_user_exec(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        uid = int(message.text.strip())
        if uid in BANNED_USERS:
            BANNED_USERS.remove(uid)
            bot.reply_to(message, f"✅ تم إلغاء حظر المستخدم {uid}")
        else:
            bot.reply_to(message, "المستخدم غير محظور")
    except:
        bot.reply_to(message, "خطأ")

@bot.callback_query_handler(func=lambda call: call.data == 'admin_back')
def admin_back(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    admin_panel(call.message)

# ========== رسالة البدء ==========
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    if not is_bot_active():
        bot.reply_to(message, "البوت متوقف حالياً للصيانة، حاول لاحقاً")
        return
    if not is_user_subscribed(user.id):
        keyboard = [[InlineKeyboardButton("📢 اشترك في القناة", url=f'https://t.me/{CHANNEL_USERNAME}')], [InlineKeyboardButton("✅ تأكد من الاشتراك", callback_data='check_sub')]]
        bot.send_message(message.chat.id, f"⚠️ عذراً، يجب الاشتراك في القناة أولاً:\nhttps://t.me/{CHANNEL_USERNAME}", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    keyboard = []
    if SERVICE_STATUS['orange']: keyboard.append([InlineKeyboardButton("🟠 Orange", callback_data='orange')])
    if SERVICE_STATUS['etisalat']: keyboard.append([InlineKeyboardButton("🟢 Etisalat", callback_data='etisalat')])
    if SERVICE_STATUS['vodafone']: keyboard.append([InlineKeyboardButton("🔴 Vodafone", callback_data='vodafone')])
    if SERVICE_STATUS['we']: keyboard.append([InlineKeyboardButton("🔵 WE", callback_data='we')])
    if SERVICE_STATUS['other']: keyboard.append([InlineKeyboardButton("🟣 خدمات أخرى", callback_data='other_services')])
    keyboard.append([InlineKeyboardButton("ℹ️ معلومات البوت", callback_data='bot_info')])
    keyboard.append([InlineKeyboardButton("👨‍💻 المطور @AMI_EG", url='https://t.me/AMI_EG')])
    bot.send_message(message.chat.id, f"🎉 اهلاً بك يا {user.first_name} في بوت MIDO 🎉\nاختر الخدمة التي تريدها:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_sub(call):
    if is_user_subscribed(call.from_user.id):
        bot.edit_message_text("✅ تم التحقق، مرحباً بك!", call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد، يرجى الاشتراك أولاً", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'bot_info')
def bot_info(call):
    text = "🤖 بوت MIDO للخدمات المجانية\n💡 الإصدار: 3.0\n📅 تم التطوير بواسطة @AMI_EG\n📢 قناة البوت: @midooojiokjj\n\n✅ جميع الخدمات تعمل بشكل تلقائي"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='back')]]))

# ========== القوائم الرئيسية للخدمات ==========
@bot.callback_query_handler(func=lambda call: call.data == 'orange')
def orange_menu(call):
    if not SERVICE_STATUS['orange']:
        bot.answer_callback_query(call.id, "خدمة Orange معطلة حالياً", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("💰 معرفة الرصيد", callback_data='orange_balance')],
        [InlineKeyboardButton("🎁 عرض 524 ميجا (رمضان كريم)", callback_data='orange_500mg')],
        [InlineKeyboardButton("🎡 عجلة الحظ", callback_data='orange_wheel')],
        [InlineKeyboardButton("🎁 Business Gifts (1000 ميجا)", callback_data='orange_business')],
        [InlineKeyboardButton("📱 تفعيل 2000 ميجا", callback_data='orange_2000mb')],
        [InlineKeyboardButton("🧩 فوازير رمضان (حل تلقائي)", callback_data='orange_fawazeer')],
        [InlineKeyboardButton("🔍 استخراج أسئلة الفوازير", callback_data='orange_extract')],
        [InlineKeyboardButton("🎬 اشتراك WatchIT", callback_data='orange_watchit')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Orange:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat')
def etisalat_menu(call):
    if not SERVICE_STATUS['etisalat']:
        bot.answer_callback_query(call.id, "خدمة Etisalat معطلة حالياً", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("📱 500 ميجا سوشيال", callback_data='etisalat_500_social')],
        [InlineKeyboardButton("📱 500 ميجا ستريمنج", callback_data='etisalat_500_stream')],
        [InlineKeyboardButton("🎁 هدية 100 وحدة", callback_data='etisalat_100_units')],
        [InlineKeyboardButton("🎁 الهدية اليومية", callback_data='etisalat_daily')],
        [InlineKeyboardButton("🎬 اشتراك شاهد VIP", callback_data='etisalat_shahid')],
        [InlineKeyboardButton("🗑️ حذف حساب ماي اتصالات", callback_data='etisalat_delete')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Etisalat:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone')
def vodafone_menu(call):
    if not SERVICE_STATUS['vodafone']:
        bot.answer_callback_query(call.id, "خدمة Vodafone معطلة حالياً", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("💰 خصم فليكس 260", callback_data='vodafone_flex')],
        [InlineKeyboardButton("🎁 كوبونات فودافون", callback_data='vodafone_gifts')],
        [InlineKeyboardButton("💰 خصم باقة Plus 20,000", callback_data='vodafone_plus')],
        [InlineKeyboardButton("☀️ هدايا الصيف 1000MG", callback_data='vodafone_summer')],
        [InlineKeyboardButton("📊 توزيع الفليكسات", callback_data='vodafone_distribute')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Vodafone:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'we')
def we_menu(call):
    if not SERVICE_STATUS['we']:
        bot.answer_callback_query(call.id, "خدمة WE معطلة حالياً", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("📱 معلومات الخط", callback_data='we_info')],
        [InlineKeyboardButton("📊 الاستهلاك", callback_data='we_usage')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات WE:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'other_services')
def other_menu(call):
    if not SERVICE_STATUS['other']:
        bot.answer_callback_query(call.id, "الخدمات الأخرى معطلة حالياً", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("🔍 TikTok Search", callback_data='tiktok')],
        [InlineKeyboardButton("📧 بريد مؤقت", callback_data='temp_email')],
        [InlineKeyboardButton("💳 معرفة المحفظة", callback_data='wallet')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات أخرى:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== دوال جمع البيانات للخدمات ==========
# أورانج: خدمات تحتاج رقم + كلمة مرور
def ask_orange_number(call, service_type):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم هاتفك (مثال: 01234567890):")
    bot.register_next_step_handler(msg, lambda m: ask_orange_password(m, service_type))

def ask_orange_password(message, service_type):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "⚠️ رقم غير صحيح. يجب أن يبدأ بـ01 ويتكون من 11 رقم.")
        return
    msg = bot.reply_to(message, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: execute_orange_service(m, number, service_type))

def execute_orange_service(message, number, service_type):
    password = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    if service_type == 'balance':
        result = check_orange_balance(number)
    elif service_type == '500mg':
        result = redeem_orange_500mg(number, password)
    elif service_type == 'wheel':
        result = spin_orange_wheel(number, password)
    elif service_type == 'business':
        result = orange_business_gifts(number, password)
    elif service_type == 'fawazeer':
        result = solve_orange_fawazeer(number, password)
    elif service_type == 'extract':
        result = extract_fawazeer_questions(number, password)
    elif service_type == 'watchit':
        result = activate_watchit(number, password)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='orange')]]))

# أورانج 2000 ميجا (تحتاج رقم + باسورد + سيريال)
def ask_orange_2000mb_number(call):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم هاتفك:")
    bot.register_next_step_handler(msg, ask_orange_2000mb_password)

def ask_orange_2000mb_password(message):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: ask_orange_2000mb_serial(m, number))

def ask_orange_2000mb_serial(message, number):
    password = message.text.strip()
    msg = bot.reply_to(message, "🔢 أدخل الرقم التسلسلي للشريحة (SIM Serial):")
    bot.register_next_step_handler(msg, lambda m: execute_orange_2000mb(m, number, password))

def execute_orange_2000mb(message, number, password):
    serial = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    result = activate_orange_2000mb(number, password, serial)
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='orange')]]))

# إتصالات: خدمات تحتاج رقم + باسورد + بريد إلكتروني
def ask_etisalat_number(call, service_type):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم هاتفك (مثال: 01123456789):")
    bot.register_next_step_handler(msg, lambda m: ask_etisalat_password(m, service_type))

def ask_etisalat_password(message, service_type):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: ask_etisalat_email(m, number, service_type))

def ask_etisalat_email(message, number, service_type):
    password = message.text.strip()
    msg = bot.reply_to(message, "📧 أدخل البريد الإلكتروني:")
    bot.register_next_step_handler(msg, lambda m: execute_etisalat_service(m, number, password, service_type))

def execute_etisalat_service(message, number, password, service_type):
    email = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    if service_type == 'social':
        result = redeem_etisalat_500mg_social(number, password, email)
    elif service_type == 'stream':
        result = redeem_etisalat_500mg_streaming(number, password, email)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

# إتصالات: خدمات تحتاج بريد + باسورد فقط (100 وحدة، هدية يومية، شاهد، حذف)
def ask_etisalat_email_only(call, service_type):
    msg = bot.send_message(call.message.chat.id, "📧 أدخل البريد الإلكتروني:")
    bot.register_next_step_handler(msg, lambda m: ask_etisalat_password_only(m, service_type))

def ask_etisalat_password_only(message, service_type):
    email = message.text.strip()
    msg = bot.reply_to(message, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: execute_etisalat_email_service(m, email, service_type))

def execute_etisalat_email_service(message, email, service_type):
    password = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    if service_type == '100units':
        result = redeem_etisalat_100_units(email, password)
    elif service_type == 'daily':
        result = redeem_etisalat_daily_gift(email, password)
    elif service_type == 'shahid':
        result = activate_etisalat_shahid_vip(email, password)
    elif service_type == 'delete':
        result = delete_etisalat_account(email, password)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

# فودافون: خدمات تحتاج رقم + باسورد
def ask_vodafone_number(call, service_type):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم هاتفك:")
    bot.register_next_step_handler(msg, lambda m: ask_vodafone_password(m, service_type))

def ask_vodafone_password(message, service_type):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: execute_vodafone_service(m, number, service_type))

def execute_vodafone_service(message, number, service_type):
    password = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    if service_type == 'flex':
        result = redeem_vodafone_flex_discount(number, password)
    elif service_type == 'gifts':
        result = redeem_vodafone_gifts(number, password)
    elif service_type == 'plus':
        result = redeem_vodafone_plus_discount(number, password)
    elif service_type == 'summer':
        result = redeem_vodafone_summer_gift(number, password)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='vodafone')]]))

# فودافون: توزيع الفليكسات (رقم المالك + باسورد + رقم مستهدف + نسبة)
def ask_vodafone_distribute_owner(call):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم المالك:")
    bot.register_next_step_handler(msg, ask_vodafone_distribute_password)

def ask_vodafone_distribute_password(message):
    owner = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', owner):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "🔑 أدخل كلمة مرور المالك:")
    bot.register_next_step_handler(msg, lambda m: ask_vodafone_distribute_target(m, owner))

def ask_vodafone_distribute_target(message, owner):
    owner_pass = message.text.strip()
    msg = bot.reply_to(message, "📱 أدخل الرقم المستهدف:")
    bot.register_next_step_handler(msg, lambda m: ask_vodafone_distribute_percent(m, owner, owner_pass))

def ask_vodafone_distribute_percent(message, owner, owner_pass):
    target = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', target):
        bot.reply_to(message, "الرقم المستهدف غير صحيح")
        return
    msg = bot.reply_to(message, "🔢 أدخل نسبة التوزيع (مثال: 50):")
    bot.register_next_step_handler(msg, lambda m: execute_vodafone_distribute(m, owner, owner_pass, target))

def execute_vodafone_distribute(message, owner, owner_pass, target):
    try:
        percent = int(message.text.strip())
    except:
        bot.reply_to(message, "النسبة يجب أن تكون رقماً")
        return
    chat_id = message.chat.id
    show_progress(chat_id)
    result = distribute_vodafone_flex(owner, owner_pass, target, percent)
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='vodafone')]]))

# WE: خدمات تحتاج رقم + باسورد
def ask_we_number(call, service_type):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم هاتفك:")
    bot.register_next_step_handler(msg, lambda m: ask_we_password(m, service_type))

def ask_we_password(message, service_type):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "🔑 أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: execute_we_service(m, number, service_type))

def execute_we_service(message, number, service_type):
    password = message.text.strip()
    chat_id = message.chat.id
    show_progress(chat_id)
    if service_type == 'info':
        result = get_we_line_info(number, password)
    else:
        result = get_we_usage(number, password)
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='we')]]))

# تيك توك
def ask_tiktok_username(call):
    msg = bot.send_message(call.message.chat.id, "🔍 أدخل اسم المستخدم (بدون @):")
    bot.register_next_step_handler(msg, execute_tiktok)

def execute_tiktok(message):
    username = message.text.strip()
    chat_id = message.chat.id
    pic, caption = get_tiktok_info(username)
    if pic:
        bot.send_photo(chat_id, pic, caption=caption, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]]))
    else:
        bot.send_message(chat_id, caption, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]]))

# معرفة المحفظة
def ask_wallet_number(call):
    msg = bot.send_message(call.message.chat.id, "📱 أدخل رقم الهاتف (11 رقم):")
    bot.register_next_step_handler(msg, execute_wallet)

def execute_wallet(message):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    chat_id = message.chat.id
    show_progress(chat_id)
    result = check_wallet_status(number)
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]]))

# ========== ربط الأزرار بالدوال ==========
# أزرار أورانج
@bot.callback_query_handler(func=lambda call: call.data == 'orange_balance')
def cb_orange_balance(call): ask_orange_number(call, 'balance')
@bot.callback_query_handler(func=lambda call: call.data == 'orange_500mg')
def cb_orange_500mg(call): ask_orange_number(call, '500mg')
@bot.callback_query_handler(func=lambda call: call.data == 'orange_wheel')
def cb_orange_wheel(call): ask_orange_number(call, 'wheel')
@bot.callback_query_handler(func=lambda call: call.data == 'orange_business')
def cb_orange_business(call): ask_orange_number(call, 'business')
@bot.callback_query_handler(func=lambda call: call.data == 'orange_2000mb')
def cb_orange_2000mb(call): ask_orange_2000mb_number(call)
@bot.callback_query_handler(func=lambda call: call.data == 'orange_fawazeer')
def cb_orange_fawazeer(call): ask_orange_number(call, 'fawazeer')
@bot.callback_query_handler(func=lambda call: call.data == 'orange_extract')
def cb_orange_extract(call): ask_orange_number(call, 'extract')
@bot.callback_query_handler(func=lambda call: call.data == 'orange_watchit')
def cb_orange_watchit(call): ask_orange_number(call, 'watchit')

# أزرار إتصالات
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_500_social')
def cb_etisalat_social(call): ask_etisalat_number(call, 'social')
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_500_stream')
def cb_etisalat_stream(call): ask_etisalat_number(call, 'stream')
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_100_units')
def cb_etisalat_100(call): ask_etisalat_email_only(call, '100units')
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_daily')
def cb_etisalat_daily(call): ask_etisalat_email_only(call, 'daily')
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_shahid')
def cb_etisalat_shahid(call): ask_etisalat_email_only(call, 'shahid')
@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_delete')
def cb_etisalat_delete(call): ask_etisalat_email_only(call, 'delete')

# أزرار فودافون
@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_flex')
def cb_vodafone_flex(call): ask_vodafone_number(call, 'flex')
@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_gifts')
def cb_vodafone_gifts(call): ask_vodafone_number(call, 'gifts')
@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_plus')
def cb_vodafone_plus(call): ask_vodafone_number(call, 'plus')
@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_summer')
def cb_vodafone_summer(call): ask_vodafone_number(call, 'summer')
@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_distribute')
def cb_vodafone_distribute(call): ask_vodafone_distribute_owner(call)

# أزرار WE
@bot.callback_query_handler(func=lambda call: call.data == 'we_info')
def cb_we_info(call): ask_we_number(call, 'info')
@bot.callback_query_handler(func=lambda call: call.data == 'we_usage')
def cb_we_usage(call): ask_we_number(call, 'usage')

# أزرار خدمات أخرى
@bot.callback_query_handler(func=lambda call: call.data == 'tiktok')
def cb_tiktok(call): ask_tiktok_username(call)
@bot.callback_query_handler(func=lambda call: call.data == 'temp_email')
def cb_temp_email(call): temp_email_menu(call)
@bot.callback_query_handler(func=lambda call: call.data == 'wallet')
def cb_wallet(call): ask_wallet_number(call)

# قائمة البريد المؤقت
def temp_email_menu(call):
    keyboard = [
        [InlineKeyboardButton("🔄 بريد عشوائي", callback_data='temp_random')],
        [InlineKeyboardButton("✏️ بريد مخصص", callback_data='temp_custom')],
        [InlineKeyboardButton("📨 عرض الرسائل", callback_data='temp_messages')],
        [InlineKeyboardButton("🗑️ حذف بريد", callback_data='temp_delete')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]
    ]
    bot.edit_message_text("📧 البريد المؤقت:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'temp_random')
def temp_random(call):
    email = create_random_temp_email()
    if email:
        bot.edit_message_text(f"✅ بريدك المؤقت:\n`{email}`", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')]]))
    else:
        bot.edit_message_text("❌ فشل إنشاء البريد", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'temp_custom')
def temp_custom(call):
    msg = bot.send_message(call.message.chat.id, "✏️ أدخل اسم المستخدم (بدون @ والنطاق):")
    bot.register_next_step_handler(msg, get_temp_domain)

def get_temp_domain(message):
    username = message.text.strip()
    domains = get_temp_email_domains()
    if not domains:
        bot.reply_to(message, "لا توجد نطاقات متاحة")
        return
    keyboard = []
    for d in domains[:5]:
        keyboard.append([InlineKeyboardButton(d, callback_data=f'temp_create_{username}@{d}')])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')])
    bot.send_message(message.chat.id, "اختر النطاق:", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data.startswith('temp_create_'))
def temp_create(call):
    email = call.data.replace('temp_create_', '')
    username, domain = email.split('@')
    created = create_custom_temp_email(username, domain)
    if created:
        bot.edit_message_text(f"✅ بريدك المؤقت:\n`{created}`", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')]]))
    else:
        bot.edit_message_text("❌ فشل إنشاء البريد", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'temp_messages')
def temp_messages(call):
    msg = bot.send_message(call.message.chat.id, "📧 أدخل البريد الإلكتروني:")
    bot.register_next_step_handler(msg, show_temp_messages)

def show_temp_messages(message):
    email = message.text.strip()
    msgs = get_temp_email_messages(email)
    if msgs:
        txt = f"📨 رسائل {email}:\n\n"
        for m in msgs[:5]:
            txt += f"📩 من: {m.get('from')}\n📌 موضوع: {m.get('subject')}\n📅 التاريخ: {m.get('date')}\n\n"
        bot.send_message(message.chat.id, txt)
    else:
        bot.send_message(message.chat.id, "لا توجد رسائل لهذا البريد")
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='temp_email')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'temp_delete')
def temp_delete(call):
    msg = bot.send_message(call.message.chat.id, "🗑️ أدخل البريد الإلكتروني للحذف:")
    bot.register_next_step_handler(msg, delete_temp_mail)

def delete_temp_mail(message):
    email = message.text.strip()
    if delete_temp_email(email):
        bot.send_message(message.chat.id, "✅ تم حذف البريد")
    else:
        bot.send_message(message.chat.id, "❌ فشل الحذف أو البريد غير موجود")
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='temp_email')]]))

# زر الرجوع الرئيسي
@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_to_main(call):
    start(call.message)

# ========== تشغيل البوت ==========
if __name__ == '__main__':
    print("🤖 بوت MIDO يعمل بكامل طاقته...")
    print(f"✅ تم تفعيل جميع الخدمات")
    bot.infinity_polling()
