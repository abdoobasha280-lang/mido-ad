import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
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

# ========== دوال خدمات Orange ==========
def check_orange_balance(phone, chat_id):
    show_progress(chat_id)
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

def redeem_500mg(number, password, chat_id):
    show_progress(chat_id)
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

def spin_wheel(number, password, chat_id):
    show_progress(chat_id)
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

def redeem_orange_business_gifts(number, password, chat_id):
    show_progress(chat_id)
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

def activate_orange_2000mb(number, password, serial, chat_id):
    show_progress(chat_id)
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

def redeem_orange_fawazeer(number, password, chat_id):
    show_progress(chat_id)
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

def extract_fawazeer_questions(number, password, chat_id):
    show_progress(chat_id)
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

def activate_watchit(number, password, chat_id):
    show_progress(chat_id)
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

# ========== دوال خدمات Etisalat ==========
def redeem_etisalat_500mg(number, password, email, chat_id):
    show_progress(chat_id)
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

def redeem_etisalat_streaming(number, password, email, chat_id):
    show_progress(chat_id)
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

def redeem_etisalat_100_units(email, password, chat_id):
    show_progress(chat_id)
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
            return "✅ تم تفعيل 100 وحدة بنجاح!"
        return "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_etisalat_daily_gift(email, password, chat_id):
    show_progress(chat_id)
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
                    return f"🎉 تم تفعيل {amount} ميجا بنجاح!"
                return "❌ فشل التفعيل"
        return "⚠️ لا توجد هدايا متاحة اليوم"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def activate_shahid_vip(email, password, chat_id):
    show_progress(chat_id)
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
            return "✅ تم تفعيل شاهد VIP بنجاح!"
        return "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def delete_etisalat_account(email, password, chat_id):
    show_progress(chat_id)
    try:
        auth = base64.b64encode(f"{email}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}", "Content-Type": "text/xml"}
        payload = f'<deleteUserAccountRequest><email>{email}</email></deleteUserAccountRequest>'
        r = requests.post("https://mab.etisalat.com.eg:11003/Saytar/rest/quickAccess/deleteAccount", headers=headers, data=payload, timeout=30)
        if "<status>true</status>" in r.text:
            return "✅ تم حذف الحساب بنجاح"
        return "❌ فشل حذف الحساب"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== دوال خدمات Vodafone ==========
def redeem_vodafone_flex_discount(number, password, chat_id):
    show_progress(chat_id)
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
            return "✅ تم تفعيل خصم فليكس بنجاح!"
        return "⚠️ قد يكون مفعل مسبقاً"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_vodafone_gifts(number, password, chat_id):
    show_progress(chat_id)
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
        return f"✅ تم تفعيل {success} هدية بنجاح!" if success else "❌ فشل التفعيل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_vodafone_plus_discount(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3", "client_id": "my-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "msisdn": number}
        r2 = requests.get("https://web.vodafone.com.eg/services/dxl/promo/promotion?%40type=Promo&%24.context.type=scratchCoupon", headers=headers)
        if "Promo_TX_ID" in r2.text:
            return "✅ تم التفعيل مسبقاً"
        return "✅ تم تفعيل العرض بنجاح!" if "No Data Found" not in r2.text else "⚠️ لا يوجد عرض"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def redeem_vodafone_summer_gift(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": number, "password": password, "grant_type": "password", "client_secret": "95fd95fb-7489-4958-8ae6-d31a525cd20a", "client_id": "ana-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "msisdn": number}
        r2 = requests.get("https://web.vodafone.com.eg/services/dxl/promo/promotion?@type=Promo&$.context.type=massSummerPromo25", headers=headers)
        if r2.status_code == 404:
            return "⚠️ تم الحصول على الهدية من قبل"
        data = r2.json()
        amount = data[1]["characteristics"][0]["value"]
        return f"✅ تم تفعيل هدية الصيف {amount} بنجاح!"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def distribute_vodafone_flexes(owner, owner_pass, target, percent, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        data = {"username": owner, "password": owner_pass, "grant_type": "password", "client_secret": "95fd95fb-7489-4958-8ae6-d31a525cd20a", "client_id": "ana-vodafone-app"}
        r = requests.post(url, data=data)
        token = r.json()['access_token']
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "msisdn": owner}
        payload = {"name": "FlexFamily", "type": "SendInvitation", "category": [{"value": "523", "listHierarchyId": "PackageID"}], "parts": {"member": [{"id": [{"value": owner, "schemeName": "MSISDN"}], "type": "Owner"}, {"id": [{"value": target, "schemeName": "MSISDN"}], "type": "Member"}], "characteristicsValue": {"characteristicsValue": [{"characteristicName": "quotaDist1", "value": percent, "type": "percentage"}]}}}
        r2 = requests.post("https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup", json=payload, headers=headers)
        return "✅ تم إرسال طلب التوزيع" if '{}' in r2.text else "❌ فشل"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== دوال خدمات WE ==========
def get_we_line_info(number, password, chat_id):
    show_progress(chat_id)
    try:
        if number.startswith("0"): number = number[1:]
        url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
        payload = {"acctId": number, "password": password, "appLocale": "en-US", "isSelfcare": "Y", "isMobile": "N"}
        r = requests.post(url, json=payload)
        data = r.json()
        return f"📱 رقم الخط: {data['body']['subscriber']['servNumber']}\nالاسم: {data['body']['customer']['custName']}"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def get_we_usage_info(number, password, chat_id):
    show_progress(chat_id)
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
        result = "📊 الاستهلاك:\n"
        for pkg in r2.json().get('body', []):
            result += f"⦿ {pkg.get('offerName')}: مستخدم {pkg.get('used')} / {pkg.get('total')}\n"
        return result
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# ========== دوال خدمات أخرى ==========
def get_tiktok_info(username, chat_id):
    try:
        r = requests.get(f"{TIKTOK_API_URL}{username}", timeout=10)
        data = r.json()
        if 'error' in data:
            return f"❌ {data['error']}"
        caption = f"📌 {data.get('nickname')}\n🆔 {data.get('user_id')}\n👥 متابعين: {data.get('followers')}\n❤️ {data.get('hearts')}\n🎥 {data.get('videos')}\n🔗 https://tiktok.com/@{username}"
        if data.get('profile_picture'):
            bot.send_photo(chat_id, data['profile_picture'], caption=caption)
        else:
            bot.send_message(chat_id, caption)
        return "✅ تم"
    except Exception as e:
        return f"❌ {str(e)}"

def check_wallet(number, chat_id):
    show_progress(chat_id)
    try:
        url = "https://fep.kashier.io/v3/orders"
        payload = {"apiOperation": "INITIATE_R2P", "paymentMethod": {"type": "wallet"}, "customer": {"mobilePhone": number}, "order": {"reference": "34d82fe7-6923-4c1f-abfb-7989d9973ebd", "amount": "5", "currency": "EGP"}}
        headers = {'Kashier-Hash': "24a66f31d9e032af51f629553f156cfa8477e8952cdafa356a8389cd64051056", 'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers)
        msg = r.json().get("response", {}).get("transactionResponseMessage", {}).get("ar", "")
        if "غير مسجل" in msg:
            return "❌ الرقم غير مسجل في محفظة"
        return "✅ الرقم مسجل في محفظة" if r.json().get("response", {}).get("status") == "SUCCESS" else f"⚠️ {msg}"
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
    bot.send_message(message.chat.id, "👨‍💻 لوحة التحكم", reply_markup=InlineKeyboardMarkup(keyboard))

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
    text = f"📊 الإحصائيات:\nأدمن: {len(ADMINS)}\nمستخدمين: {len(APPROVED_USERS)}\nمحظورين: {len(BANNED_USERS)}\nحالة البوت: {'نشط' if BOT_ACTIVE else 'متوقف'}"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast')
def broadcast_prompt(call):
    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "غير مسموح", show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id, "أرسل رسالتك:")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(message):
    if message.from_user.id not in ADMINS:
        return
    for uid in APPROVED_USERS + ADMINS:
        try:
            bot.send_message(uid, f"📢 إعلان:\n{message.text}")
        except:
            pass
    bot.reply_to(message, "✅ تم الإرسال")

# دوال إدارة المستخدمين (إضافة، حذف، حظر)
@bot.callback_query_handler(func=lambda call: call.data == 'list_users')
def list_users(call):
    if call.from_user.id not in ADMINS:
        return
    txt = "المستخدمون:\n" + "\n".join(str(u) for u in APPROVED_USERS) if APPROVED_USERS else "لا يوجد"
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='user_mgmt')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'add_user')
def add_user_prompt(call):
    if call.from_user.id not in ADMINS:
        return
    msg = bot.send_message(call.message.chat.id, "أرسل معرف المستخدم:")
    bot.register_next_step_handler(msg, add_user_exec)

def add_user_exec(message):
    if message.from_user.id not in ADMINS:
        return
    try:
        uid = int(message.text)
        if uid not in APPROVED_USERS and uid not in ADMINS:
            APPROVED_USERS.append(uid)
            bot.reply_to(message, f"✅ تم إضافة {uid}")
        else:
            bot.reply_to(message, "موجود بالفعل")
    except:
        bot.reply_to(message, "خطأ في المعرف")

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
        uid = int(message.text)
        if uid in APPROVED_USERS:
            APPROVED_USERS.remove(uid)
            bot.reply_to(message, f"✅ تم إزالة {uid}")
        else:
            bot.reply_to(message, "غير موجود")
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
        uid = int(message.text)
        if uid not in BANNED_USERS and uid not in ADMINS:
            BANNED_USERS.append(uid)
            if uid in APPROVED_USERS:
                APPROVED_USERS.remove(uid)
            bot.reply_to(message, f"✅ تم حظر {uid}")
        else:
            bot.reply_to(message, "محظور بالفعل أو أدمن")
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
        uid = int(message.text)
        if uid in BANNED_USERS:
            BANNED_USERS.remove(uid)
            bot.reply_to(message, f"✅ تم إلغاء حظر {uid}")
        else:
            bot.reply_to(message, "غير محظور")
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
        bot.reply_to(message, "البوت متوقف للصيانة")
        return
    if not is_user_subscribed(user.id):
        keyboard = [[InlineKeyboardButton("📢 اشترك هنا", url=f'https://t.me/{CHANNEL_USERNAME}')], [InlineKeyboardButton("✅ تأكد", callback_data='check_sub')]]
        bot.send_message(message.chat.id, "⚠️ يجب الاشتراك في القناة أولاً:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    keyboard = []
    if SERVICE_STATUS['orange']: keyboard.append([InlineKeyboardButton("🟠 Orange", callback_data='orange')])
    if SERVICE_STATUS['etisalat']: keyboard.append([InlineKeyboardButton("🟢 Etisalat", callback_data='etisalat')])
    if SERVICE_STATUS['vodafone']: keyboard.append([InlineKeyboardButton("🔴 Vodafone", callback_data='vodafone')])
    if SERVICE_STATUS['we']: keyboard.append([InlineKeyboardButton("🔵 WE", callback_data='we')])
    if SERVICE_STATUS['other']: keyboard.append([InlineKeyboardButton("🟣 خدمات أخرى", callback_data='other_services')])
    keyboard.append([InlineKeyboardButton("ℹ️ معلومات البوت", callback_data='bot_info')])
    keyboard.append([InlineKeyboardButton("👨‍💻 المطور @AMI_EG", url='https://t.me/AMI_EG')])
    bot.send_message(message.chat.id, f"اهلا بيك يا {user.first_name} في بوت MIDO\nاختر الخدمه التي تريدها ومتنسناش ب اسكرين", reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_sub(call):
    if is_user_subscribed(call.from_user.id):
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "لم تشترك بعد", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'bot_info')
def bot_info(call):
    bot.edit_message_text("🤖 بوت MIDO للخدمات المجانية\n💡 إصدار 2.0\n📅 تم التطوير بواسطة @AMI_EG\n📢 قناة البوت: @midooojiokjj", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='back')]]))

# ========== معالجة أزرار الخدمات الرئيسية ==========
@bot.callback_query_handler(func=lambda call: call.data == 'orange')
def orange_menu(call):
    if not SERVICE_STATUS['orange']:
        bot.answer_callback_query(call.id, "الخدمة معطلة", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("عرض الـ5G", callback_data='orange_1000mg')],
        [InlineKeyboardButton("عجلة الحظ", callback_data='orange_wheel')],
        [InlineKeyboardButton("Business Gifts", callback_data='orange_business')],
        [InlineKeyboardButton("2000MB", callback_data='orange_2000mb')],
        [InlineKeyboardButton("Fawazeer", callback_data='orange_fawazeer')],
        [InlineKeyboardButton("استخراج أسئلة Fawazeer", callback_data='orange_extract')],
        [InlineKeyboardButton("معرفة الرصيد", callback_data='orange_balance')],
        [InlineKeyboardButton("اشتراك WatchIT", callback_data='orange_watchit')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Orange:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat')
def etisalat_menu(call):
    if not SERVICE_STATUS['etisalat']:
        bot.answer_callback_query(call.id, "الخدمة معطلة", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("500 ميجا سوشيال", callback_data='etisalat_500')],
        [InlineKeyboardButton("500 ميجا ستريمنج", callback_data='etisalat_stream')],
        [InlineKeyboardButton("هدية 100 وحدة", callback_data='etisalat_100')],
        [InlineKeyboardButton("الهدية اليومية", callback_data='etisalat_daily')],
        [InlineKeyboardButton("اشتراك شاهد VIP", callback_data='etisalat_shahid')],
        [InlineKeyboardButton("حذف حساب ماي اتصالات", callback_data='etisalat_delete')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Etisalat:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone')
def vodafone_menu(call):
    if not SERVICE_STATUS['vodafone']:
        bot.answer_callback_query(call.id, "الخدمة معطلة", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("خصم فليكس 260", callback_data='vodafone_flex')],
        [InlineKeyboardButton("كوبونات فودافون", callback_data='vodafone_gifts')],
        [InlineKeyboardButton("خصم Plus 20,000", callback_data='vodafone_plus')],
        [InlineKeyboardButton("هدايا الصيف 1000MG", callback_data='vodafone_summer')],
        [InlineKeyboardButton("توزيع الفليكسات", callback_data='vodafone_distribute')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات Vodafone:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'we')
def we_menu(call):
    if not SERVICE_STATUS['we']:
        bot.answer_callback_query(call.id, "الخدمة معطلة", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("معلومات الخط", callback_data='we_info')],
        [InlineKeyboardButton("معرفة الاستهلاك", callback_data='we_usage')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات WE:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'other_services')
def other_menu(call):
    if not SERVICE_STATUS['other']:
        bot.answer_callback_query(call.id, "الخدمات الأخرى معطلة", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("🔍 TikTok Search", callback_data='tiktok')],
        [InlineKeyboardButton("📧 بريد مؤقت", callback_data='temp_email')],
        [InlineKeyboardButton("💳 معرفة المحفظة", callback_data='wallet')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ]
    bot.edit_message_text("خدمات أخرى:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== معالجة أزرار Orange الفرعية ==========
@bot.callback_query_handler(func=lambda call: call.data == 'orange_1000mg')
def orange_1000mg(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, '1000mg'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_wheel')
def orange_wheel(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, 'wheel'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_business')
def orange_business(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, 'business'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_2000mb')
def orange_2000mb(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, get_orange_2000mb_number)

@bot.callback_query_handler(func=lambda call: call.data == 'orange_fawazeer')
def orange_fawazeer(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, 'fawazeer'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_extract')
def orange_extract(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, 'extract'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_balance')
def orange_balance(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, 'balance'))

@bot.callback_query_handler(func=lambda call: call.data == 'orange_watchit')
def orange_watchit(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Orange:")
    bot.register_next_step_handler(msg, lambda m: get_orange_pass(m, 'watchit'))

def get_orange_pass(message, service):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: exec_orange_service(m, number, service))

def exec_orange_service(message, number, service):
    password = message.text.strip()
    chat_id = message.chat.id
    if service == '1000mg':
        result = redeem_500mg(number, password, chat_id)
    elif service == 'wheel':
        result = spin_wheel(number, password, chat_id)
    elif service == 'business':
        result = redeem_orange_business_gifts(number, password, chat_id)
    elif service == 'fawazeer':
        result = redeem_orange_fawazeer(number, password, chat_id)
    elif service == 'extract':
        result = extract_fawazeer_questions(number, password, chat_id)
    elif service == 'watchit':
        result = activate_watchit(number, password, chat_id)
    elif service == 'balance':
        result = check_orange_balance(number, chat_id)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='orange')]]))

def get_orange_2000mb_number(message):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    msg = bot.reply_to(message, "أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_orange_2000mb_pass(m, number))

def get_orange_2000mb_pass(message, number):
    password = message.text.strip()
    msg = bot.reply_to(message, "أدخل الرقم التسلسلي للشريحة:")
    bot.register_next_step_handler(msg, lambda m: exec_orange_2000mb(m, number, password))

def exec_orange_2000mb(message, number, password):
    serial = message.text.strip()
    result = activate_orange_2000mb(number, password, serial, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='orange')]]))

# ========== معالجة أزرار Etisalat الفرعية ==========
def get_etisalat_credentials(message, service):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل رقم الهاتف وكلمة المرور (مثال: 01123456789 pass)")
        return
    number = parts[0]
    password = parts[1]
    msg = bot.reply_to(message, "أدخل البريد الإلكتروني:")
    bot.register_next_step_handler(msg, lambda m: exec_etisalat_service(m, number, password, service))

def exec_etisalat_service(message, number, password, service):
    email = message.text.strip()
    chat_id = message.chat.id
    if service == '500':
        result = redeem_etisalat_500mg(number, password, email, chat_id)
    elif service == 'stream':
        result = redeem_etisalat_streaming(number, password, email, chat_id)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_500')
def etisalat_500(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Etisalat وكلمة المرور (مفصولين بمسافة):")
    bot.register_next_step_handler(msg, lambda m: get_etisalat_credentials(m, '500'))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_stream')
def etisalat_stream(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Etisalat وكلمة المرور (مفصولين بمسافة):")
    bot.register_next_step_handler(msg, lambda m: get_etisalat_credentials(m, 'stream'))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_100')
def etisalat_100(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني وكلمة المرور (مفصولين بمسافة):")
    bot.register_next_step_handler(msg, lambda m: exec_etisalat_100(m))

def exec_etisalat_100(message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل البريد وكلمة المرور")
        return
    email = parts[0]
    password = ' '.join(parts[1:])
    result = redeem_etisalat_100_units(email, password, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_daily')
def etisalat_daily(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: exec_etisalat_daily(m))

def exec_etisalat_daily(message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل البريد وكلمة المرور")
        return
    email = parts[0]
    password = ' '.join(parts[1:])
    result = redeem_etisalat_daily_gift(email, password, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_shahid')
def etisalat_shahid(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: exec_etisalat_shahid(m))

def exec_etisalat_shahid(message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل البريد وكلمة المرور")
        return
    email = parts[0]
    password = ' '.join(parts[1:])
    result = activate_shahid_vip(email, password, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'etisalat_delete')
def etisalat_delete(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: exec_etisalat_delete(m))

def exec_etisalat_delete(message):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل البريد وكلمة المرور")
        return
    email = parts[0]
    password = ' '.join(parts[1:])
    result = delete_etisalat_account(email, password, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='etisalat')]]))

# ========== معالجة أزرار Vodafone الفرعية ==========
def get_vodafone_creds(message, service):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل رقم الهاتف وكلمة المرور (مفصولين بمسافة)")
        return
    number = parts[0]
    password = parts[1]
    chat_id = message.chat.id
    if service == 'flex':
        result = redeem_vodafone_flex_discount(number, password, chat_id)
    elif service == 'gifts':
        result = redeem_vodafone_gifts(number, password, chat_id)
    elif service == 'plus':
        result = redeem_vodafone_plus_discount(number, password, chat_id)
    elif service == 'summer':
        result = redeem_vodafone_summer_gift(number, password, chat_id)
    else:
        result = "خدمة غير معروفة"
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='vodafone')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_flex')
def vf_flex(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Vodafone وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_vodafone_creds(m, 'flex'))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_gifts')
def vf_gifts(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Vodafone وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_vodafone_creds(m, 'gifts'))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_plus')
def vf_plus(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Vodafone وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_vodafone_creds(m, 'plus'))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_summer')
def vf_summer(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم Vodafone وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_vodafone_creds(m, 'summer'))

@bot.callback_query_handler(func=lambda call: call.data == 'vodafone_distribute')
def vf_distribute(call):
    msg = bot.send_message(call.message.chat.id, "أدخل: رقم المالك كلمة_المرور الرقم_المستهدف النسبة (مثال: 01234567890 pass 01111111111 50)")
    bot.register_next_step_handler(msg, exec_vf_distribute)

def exec_vf_distribute(message):
    parts = message.text.strip().split()
    if len(parts) < 4:
        bot.reply_to(message, "بيانات غير كافية")
        return
    owner = parts[0]
    owner_pass = parts[1]
    target = parts[2]
    try:
        percent = int(parts[3])
    except:
        bot.reply_to(message, "النسبة يجب أن تكون رقماً")
        return
    result = distribute_vodafone_flexes(owner, owner_pass, target, percent, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='vodafone')]]))

# ========== معالجة أزرار WE ==========
def get_we_creds(message, service):
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "أدخل رقم الهاتف وكلمة المرور (مفصولين بمسافة)")
        return
    number = parts[0]
    password = parts[1]
    chat_id = message.chat.id
    if service == 'info':
        result = get_we_line_info(number, password, chat_id)
    else:
        result = get_we_usage_info(number, password, chat_id)
    bot.send_message(chat_id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='we')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'we_info')
def we_info(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم WE وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_we_creds(m, 'info'))

@bot.callback_query_handler(func=lambda call: call.data == 'we_usage')
def we_usage(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم WE وكلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: get_we_creds(m, 'usage'))

# ========== معالجة الخدمات الأخرى ==========
@bot.callback_query_handler(func=lambda call: call.data == 'tiktok')
def tiktok_search(call):
    msg = bot.send_message(call.message.chat.id, "أدخل اسم المستخدم (بدون @):")
    bot.register_next_step_handler(msg, exec_tiktok)

def exec_tiktok(message):
    username = message.text.strip()
    result = get_tiktok_info(username, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'temp_email')
def temp_email_menu(call):
    keyboard = [
        [InlineKeyboardButton("إنشاء بريد عشوائي", callback_data='temp_random')],
        [InlineKeyboardButton("إنشاء بريد مخصص", callback_data='temp_custom')],
        [InlineKeyboardButton("عرض الرسائل", callback_data='temp_messages')],
        [InlineKeyboardButton("حذف بريد", callback_data='temp_delete')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]
    ]
    bot.edit_message_text("البريد المؤقت:", call.message.chat.id, call.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard))

@bot.callback_query_handler(func=lambda call: call.data == 'temp_random')
def temp_random(call):
    email = create_random_temp_email()
    if email:
        bot.edit_message_text(f"✅ بريدك: `{email}`", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')]]))
    else:
        bot.edit_message_text("❌ فشل", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'temp_custom')
def temp_custom(call):
    msg = bot.send_message(call.message.chat.id, "أدخل اسم المستخدم (بدون @ والنطاق):")
    bot.register_next_step_handler(msg, get_temp_domain)

def get_temp_domain(message):
    username = message.text.strip()
    domains = get_temp_email_domains()
    if not domains:
        bot.reply_to(message, "لا توجد نطاقات")
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
        bot.edit_message_text(f"✅ بريدك: `{created}`", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')]]))
    else:
        bot.edit_message_text("❌ فشل", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'temp_messages')
def temp_messages(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني:")
    bot.register_next_step_handler(msg, show_temp_messages)

def show_temp_messages(message):
    email = message.text.strip()
    msgs = get_temp_email_messages(email)
    if msgs:
        txt = f"رسائل {email}:\n"
        for m in msgs[:5]:
            txt += f"من: {m.get('from')}\nموضوع: {m.get('subject')}\n\n"
        bot.send_message(message.chat.id, txt)
    else:
        bot.send_message(message.chat.id, "لا توجد رسائل")
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='temp_email')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'temp_delete')
def temp_delete(call):
    msg = bot.send_message(call.message.chat.id, "أدخل البريد الإلكتروني للحذف:")
    bot.register_next_step_handler(msg, delete_temp_mail)

def delete_temp_mail(message):
    email = message.text.strip()
    if delete_temp_email(email):
        bot.send_message(message.chat.id, "✅ تم الحذف")
    else:
        bot.send_message(message.chat.id, "❌ فشل الحذف")
    bot.send_message(message.chat.id, "🔙", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data='temp_email')]]))

@bot.callback_query_handler(func=lambda call: call.data == 'wallet')
def wallet_check(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رقم الهاتف (11 رقم):")
    bot.register_next_step_handler(msg, exec_wallet)

def exec_wallet(message):
    number = message.text.strip()
    if not re.match(r'^01[0-9]{9}$', number):
        bot.reply_to(message, "رقم غير صحيح")
        return
    result = check_wallet(number, message.chat.id)
    bot.send_message(message.chat.id, result, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]]))

# ========== زر الرجوع العام ==========
@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_to_main(call):
    start(call.message)

# ========== تشغيل البوت ==========
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
