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
CHANNEL_ID = '@midooojiokjj'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'

bot = telebot.TeleBot(API_TOKEN)
bot_active = True

# ================== قاعدة البيانات والملفات ==================
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
    if is_admin(user_id):
        return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ================== لوحة الأدمن ==================
def admin_panel_markup():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"👥 المستخدمين: {count}", callback_data="admin_stats"),
        InlineKeyboardButton("🟢 تشغيل/إيقاف", callback_data="admin_toggle"),
        InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast"),
        InlineKeyboardButton("⛔ حظر", callback_data="admin_block"),
        InlineKeyboardButton("✅ إلغاء حظر", callback_data="admin_unblock"),
        InlineKeyboardButton("➕ إضافة أدمن", callback_data="admin_add"),
        InlineKeyboardButton("➖ حذف أدمن", callback_data="admin_remove")
    )
    return markup

# ================== القوائم ==================
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
        InlineKeyboardButton("🖼 إنشاء صورة", callback_data="generate_image"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return markup

# ================== خدمات أورانج ==================
def orange_250(chat_id, number, password):
    msg = bot.send_message(chat_id, "⏳ جاري حل الفوازير...")
    session = requests.Session()
    headers = {'User-Agent': 'okhttp/4.10.0', 'Content-Type': 'application/json'}
    try:
        auth = session.post('https://services.orange.eg/SignIn.svc/SignInUser', json={
            'appVersion': '9.0.1', 'channel': {'ChannelName': 'MobinilAndMe', 'Password': 'ig3yh*mk5l42@oj7QAR8yF'},
            'dialNumber': number, 'isAndroid': True, 'lang': 'ar', 'password': password
        }, timeout=15).json()
        acc_token = auth['SignInUserResult']['AccessToken']
        headers['Token'] = acc_token
        gen = session.post('https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate', json={
            'ChannelName': 'MobinilAndMe', 'ChannelPassword': 'ig3yh*mk5l42@oj7QAR8yF',
            'Dial': number, 'Language': 'ar', 'Module': '0', 'Password': password
        }, timeout=15).json()
        token = gen['Token']
        q = session.post('https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions',
                         json={'Dial': number, 'Language': 'ar', 'Token': token}, timeout=15).json()
        if q.get('ErrorCode') == 1:
            bot.edit_message_text('❌ لقد شاركت اليوم بالفعل، جرب غداً.', chat_id, msg.message_id, reply_markup=orange_menu())
            return
        answers = []
        for ques in q['Questions']:
            for ans in ques['Answers']:
                if ans['IsCorrect']:
                    answers.append({'QuestionId': ans['QuestionId'], 'AnswerId': ans['Id']})
                    break
        sub = session.post('https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit',
                           json={'Dial': number, 'Language': 'ar', 'Token': token, 'Answers': answers}, timeout=15).json()
        if sub.get('ErrorDescription') == 'FawazeerSuccess':
            bot.edit_message_text('✅ تم حل الفوازير! استلمت 250 ميجا.', chat_id, msg.message_id, reply_markup=orange_menu())
        else:
            bot.edit_message_text(f'⚠️ {sub.get("ErrorDescription")}', chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f'❌ خطأ: {str(e)}', chat_id, msg.message_id, reply_markup=orange_menu())

def orange_500(chat_id, number, password):
    msg = bot.send_message(chat_id, '⏳ جاري استرداد 500 ميجا...')
    try:
        url = 'https://services.orange.eg/SignIn.svc/SignInUser'
        payload = {'appVersion': '8.8.5', 'channel': {'ChannelName': 'MobinilAndMe', 'Password': 'ig3yh*mk5l42@oj7QAR8yF'},
                   'dialNumber': number, 'isAndroid': True, 'lang': 'ar', 'password': password}
        resp = requests.post(url, json=payload, timeout=15).json()
        if 'SignInUserResult' not in resp:
            bot.edit_message_text('❌ رقم أو كلمة مرور خاطئة', chat_id, msg.message_id, reply_markup=orange_menu())
            return
        user_id = resp['SignInUserResult']['UserData']['UserID']
        turl = 'https://services.orange.eg/GetToken.svc/GenerateToken'
        tdata = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        tresp = requests.post(turl, headers={'Content-Type': 'application/json'}, data=tdata, timeout=15).json()
        ctv = tresp['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ',{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk').encode()).hexdigest().upper()
        rurl = 'https://services.orange.eg/APIs/Promotions/api/CAF/Redeem'
        rheaders = {'_ctv': ctv, '_htv': htv, 'isEasyLogin': 'false', 'UserId': user_id, 'Content-Type': 'application/json'}
        rjson = {'Language': 'ar', 'OSVersion': 'Android7.0', 'PromoCode': 'رمضان كريم', 'dial': number,
                 'password': password, 'Channelname': 'MobinilAndMe', 'ChannelPassword': 'ig3yh*mk5l42@oj7QAR8yF'}
        rresp = requests.post(rurl, headers=rheaders, json=rjson, timeout=15).json()
        err = rresp.get('ErrorDescription', '')
        if err == 'Success':
            bot.edit_message_text('✅ تم استلام 500 ميجا!', chat_id, msg.message_id, reply_markup=orange_menu())
        elif err == 'User is redeemed before':
            bot.edit_message_text('⚠️ لقد استلمت هذه الهدية مسبقاً.', chat_id, msg.message_id, reply_markup=orange_menu())
        else:
            bot.edit_message_text(f'❌ {err}', chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f'❌ خطأ: {str(e)}', chat_id, msg.message_id, reply_markup=orange_menu())

def orange_balance(chat_id, number, password):
    msg = bot.send_message(chat_id, '⏳ جاري جلب الرصيد...')
    try:
        url = 'https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers'
        data = {'SelectedUserDial': None, 'IsForAnotherRecipient': True, 'RecipientDial': number, 'Dial': number}
        resp = requests.post(url, json=data, headers={'lang': 'en'}, timeout=15).json()
        balance = resp.get('CreditBalance', 'غير متاح')
        bot.edit_message_text(f'💰 رصيدك: {balance} جنيه', chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f'❌ فشل: {str(e)}', chat_id, msg.message_id, reply_markup=orange_menu())

def orange_wheel(chat_id, number, password):
    msg = bot.send_message(chat_id, '🎡 جاري تشغيل العجلة...\n[░░░░░░░░░░] 0%')
    try:
        for i, p in enumerate(['░░░░░░░░░░', '▓▓░░░░░░░░', '▓▓▓▓░░░░░░', '▓▓▓▓▓▓░░░░', '▓▓▓▓▓▓▓▓▓▓']):
            time.sleep(0.8)
            bot.edit_message_text(f'🎡 جاري التشغيل...\n[{p}] {(i+1)*20}%', chat_id, msg.message_id)
        turl = 'https://services.orange.eg/GetToken.svc/GenerateToken'
        tdata = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        tresp = requests.post(turl, headers={'Content-Type': 'application/json'}, data=tdata, timeout=15).json()
        ctv = tresp['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ',{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk').encode()).hexdigest().upper()
        spin_url = 'https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin'
        spin_payload = {'ChannelName': 'MobinilAndMe', 'ChannelPassword': 'ig3yh*mk5l42@oj7QAR8yF',
                        'Dial': number, 'Language': 'en', 'Password': password, 'ServiceClassId': '1033'}
        spin_headers = {'_ctv': ctv, '_htv': htv, 'Content-Type': 'application/json'}
        spin_resp = requests.post(spin_url, json=spin_payload, headers=spin_headers, timeout=15).json()
        if 'ErrorDescription' in spin_resp:
            bot.edit_message_text(f'⚠️ {spin_resp["ErrorDescription"]}', chat_id, msg.message_id, reply_markup=orange_menu())
            return
        offer = spin_resp['OfferDetails']['OfferId']
        cat = spin_resp['SecondryButtonDetails']['CategoryId']
        offer_name = spin_resp['OfferDetails']['OfferName']
        tresp2 = requests.post(turl, headers={'Content-Type': 'application/json'}, data=tdata, timeout=15).json()
        ctv2 = tresp2['GenerateTokenResult']['Token']
        htv2 = hashlib.sha256((ctv2 + ',{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk').encode()).hexdigest().upper()
        fulfill_url = 'https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill'
        fulfill_payload = {'CategoryId': cat, 'ChannelName': 'MobinilAndMe', 'ChannelPassword': 'ig3yh*mk5l42@oj7QAR8yF',
                           'Dial': number, 'Language': 'en', 'OfferId': offer, 'Password': password, 'ServiceClassId': '1033'}
        fulfill_headers = {'_ctv': ctv2, '_htv': htv2, 'Content-Type': 'application/json'}
        fulfill_resp = requests.post(fulfill_url, json=fulfill_payload, headers=fulfill_headers, timeout=15).json()
        if 'Already opted in' in str(fulfill_resp):
            result = f'🎡 {offer_name}\n⚠️ أنت مشترك بالفعل'
        else:
            result = f'🎡 {offer_name}\n✅ تم الاشتراك بنجاح'
        bot.edit_message_text(result, chat_id, msg.message_id, reply_markup=orange_menu())
    except Exception as e:
        bot.edit_message_text(f'❌ خطأ في العجلة: {str(e)}', chat_id, msg.message_id, reply_markup=orange_menu())

# ================== خدمات إتصالات ==================
def etisalat_500(chat_id, email, password):
    msg = bot.send_message(chat_id, '⏳ جاري استرداد 500 ميجا سوشيل...')
    try:
        token = base64.b64encode(f'{email}:{password}'.encode()).decode()
        headers = {'Authorization': f'Basic {token}', 'Content-Type': 'text/xml; charset=UTF-8',
                   'User-Agent': 'okhttp/5.0.0-alpha.11', 'Language': 'ar'}
        login_xml = '<?xml version="1.0" encoding="UTF-8"?><loginRequest><deviceId></deviceId><firstLoginAttempt>false</firstLoginAttempt><modelType></modelType><osVersion></osVersion><platform>Android</platform><udid></udid></loginRequest>'
        login_resp = requests.post('https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan', data=login_xml, headers=headers, timeout=15)
        root = ET.fromstring(login_resp.text)
        number = root.find('dial').text
        redeem_xml = f'<?xml version="1.0" encoding="UTF-8"?><rtimSubmitOrder><extraProductId>22932</extraProductId><offerId>22932</offerId><operationId>REDEEM</operationId><productId>RTIM_OFFERS=Offer_ID:22932;isRTIM:Y</productId><rtimFlag>true</rtimFlag><subscriberNumber>{number}</subscriberNumber></rtimSubmitOrder>'
        redeem_resp = requests.post('https://mab.etisalat.com.eg:11003/Saytar/rest/rtim/rtimSubmitOrder', data=redeem_xml, headers=headers, timeout=15)
        if 'success' in redeem_resp.text.lower():
            bot.edit_message_text('✅ تم استلام 500 ميجا سوشيل!', chat_id, msg.message_id, reply_markup=etisalat_menu())
        else:
            bot.edit_message_text('❌ فشل الاسترداد (ربما استلمتها مسبقاً)', chat_id, msg.message_id, reply_markup=etisalat_menu())
    except Exception as e:
        bot.edit_message_text(f'❌ خطأ: {str(e)}', chat_id, msg.message_id, reply_markup=etisalat_menu())

# ================== خدمات مجانية ==================
def prayer_times(chat_id, city='Cairo'):
    msg = bot.send_message(chat_id, '⏳ جلب مواقيت الصلاة...')
    try:
        resp = requests.get(f'http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5', timeout=10).json()
        timings = resp['data']['timings']
        text = f'🕌 مواقيت الصلاة في {city}:\n'
        for name, t in timings.items():
            text += f'{name}: {t}\n'
        bot.edit_message_text(text, chat_id, msg.message_id, reply_markup=free_menu())
    except Exception as e:
        bot.edit_message_text(f'❌ خطأ: {str(e)}', chat_id, msg.message_id, reply_markup=free_menu())

def generate_image(chat_id, text):
    msg = bot.send_message(chat_id, '🖼 جاري إنشاء الصورة...')
    try:
        url = f'https://quickchart.io/chart?cht=tx&chl={requests.utils.quote(text)}&chs=600x200'
        bot.send_photo(chat_id, url, caption='✅ تم إنشاء الصورة', reply_markup=free_menu())
        bot.delete_message(chat_id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f'❌ خطأ: {str(e)}', chat_id, msg.message_id, reply_markup=free_menu())

# ================== معالجة الأزرار والرسائل ==================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    add_user(message.from_user.id)
    if is_blocked(message.from_user.id):
        bot.reply_to(message, '⛔ أنت محظور.')
        return
    if not bot_active and not is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ البوت في صيانة حالياً.')
        return
    if check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f'مرحباً {message.from_user.first_name}!\nاختر خدمة:', reply_markup=main_menu())
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_ID[1:]}'))
        markup.add(InlineKeyboardButton('✅ تحقق', callback_data='check_sub'))
        bot.send_message(message.chat.id, '⚠️ يجب الاشتراك في القناة أولاً:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if is_blocked(call.from_user.id):
        bot.answer_callback_query(call.id, 'محظور', show_alert=True)
        return
    if not bot_active and not is_admin(call.from_user.id) and call.data not in ['check_sub', 'back_main']:
        bot.answer_callback_query(call.id, 'البوت متوقف', show_alert=True)
        return

    if call.data == 'check_sub':
        if check_sub(call.from_user.id):
            bot.edit_message_text('✅ تم التحقق! اختر خدمة:', call.message.chat.id, call.message.message_id, reply_markup=main_menu())
        else:
            bot.answer_callback_query(call.id, 'لم تشترك بعد!', show_alert=True)
        return

    # أوامر الأدمن
    if call.data.startswith('admin_'):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, 'غير مصرح', show_alert=True)
            return
        if call.data == 'admin_stats':
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users')
            count = c.fetchone()[0]
            conn.close()
            bot.edit_message_text(f'📊 إحصائيات:\n👥 مستخدمين: {count}\n👮 أدمنة: {len(admins)}\n⛔ محظورين: {len(blocked_users)}',
                                  call.message.chat.id, call.message.message_id, reply_markup=admin_panel_markup())
        elif call.data == 'admin_toggle':
            global bot_active
            new = 0 if get_bot_status() == 1 else 1
            set_bot_status(new)
            bot_active = (new == 1)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=admin_panel_markup())
            bot.answer_callback_query(call.id, f'تم {"تشغيل" if new==1 else "إيقاف"} البوت')
        elif call.data == 'admin_broadcast':
            msg = bot.send_message(call.message.chat.id, 'أرسل نص الإذاعة:')
            bot.register_next_step_handler(msg, broadcast_process)
        elif call.data == 'admin_block':
            msg = bot.send_message(call.message.chat.id, 'أرسل ID المستخدم لحظره:')
            bot.register_next_step_handler(msg, block_user)
        elif call.data == 'admin_unblock':
            msg = bot.send_message(call.message.chat.id, 'أرسل ID المستخدم لإلغاء حظره:')
            bot.register_next_step_handler(msg, unblock_user)
        elif call.data == 'admin_add':
            if str(call.from_user.id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, 'المطور فقط', show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, 'أرسل ID المستخدم لإضافته كأدمن:')
            bot.register_next_step_handler(msg, add_admin)
        elif call.data == 'admin_remove':
            if str(call.from_user.id) != str(ADMIN_ID):
                bot.answer_callback_query(call.id, 'المطور فقط', show_alert=True)
                return
            msg = bot.send_message(call.message.chat.id, 'أرسل ID المستخدم لحذفه من الأدمنة:')
            bot.register_next_step_handler(msg, remove_admin)
        return

    # التنقل بين القوائم
    if call.data == 'back_main':
        bot.edit_message_text('القائمة الرئيسية:', call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == 'orange_menu':
        bot.edit_message_text('🍊 خدمات أورانج:', call.message.chat.id, call.message.message_id, reply_markup=orange_menu())
    elif call.data == 'etisalat_menu':
        bot.edit_message_text('📱 خدمات إتصالات:', call.message.chat.id, call.message.message_id, reply_markup=etisalat_menu())
    elif call.data == 'free_menu':
        bot.edit_message_text('⚙ خدمات مجانية:', call.message.chat.id, call.message.message_id, reply_markup=free_menu())

    # أزرار أورانج
    elif call.data == 'orange_250':
        msg = bot.send_message(call.message.chat.id, 'أدخل رقم أورانج (11 رقم):')
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, 'orange_250'))
    elif call.data == 'orange_500':
        msg = bot.send_message(call.message.chat.id, 'أدخل رقم أورانج (11 رقم):')
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, 'orange_500'))
    elif call.data == 'orange_balance':
        msg = bot.send_message(call.message.chat.id, 'أدخل رقم أورانج:')
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, 'orange_balance'))
    elif call.data == 'orange_wheel':
        msg = bot.send_message(call.message.chat.id, 'أدخل رقم أورانج لعجلة الحظ:')
        bot.register_next_step_handler(msg, lambda m: get_number_password(m, 'orange_wheel'))

    # إتصالات
    elif call.data == 'etisalat_500':
        msg = bot.send_message(call.message.chat.id, 'أدخل البريد الإلكتروني (إيميل حساب إتصالات):')
        bot.register_next_step_handler(msg, get_etisalat_password)

    # خدمات مجانية
    elif call.data == 'prayer_times':
        msg = bot.send_message(call.message.chat.id, 'أدخل اسم المدينة (مثال: Cairo):')
        bot.register_next_step_handler(msg, lambda m: prayer_times(m.chat.id, m.text))
    elif call.data == 'generate_image':
        msg = bot.send_message(call.message.chat.id, 'أدخل النص الذي تريد تحويله إلى صورة:')
        bot.register_next_step_handler(msg, lambda m: generate_image(m.chat.id, m.text))

# دوال مساعدة للخطوات
def get_number_password(message, service):
    num = message.text.strip()
    if not (num.isdigit() and len(num) == 11 and num.startswith('01')):
        bot.reply_to(message, 'رقم غير صالح! أدخل 11 رقمًا يبدأ بـ 01')
        return
    msg = bot.send_message(message.chat.id, 'أدخل كلمة المرور:')
    bot.register_next_step_handler(msg, lambda m: process_orange(m, num, service))

def process_orange(message, number, service):
    pwd = message.text.strip()
    if service == 'orange_250':
        orange_250(message.chat.id, number, pwd)
    elif service == 'orange_500':
        orange_500(message.chat.id, number, pwd)
    elif service == 'orange_balance':
        orange_balance(message.chat.id, number, pwd)
    elif service == 'orange_wheel':
        orange_wheel(message.chat.id, number, pwd)

def get_etisalat_password(message):
    email = message.text.strip()
    msg = bot.send_message(message.chat.id, 'أدخل كلمة مرور حساب إتصالات:')
    bot.register_next_step_handler(msg, lambda m: etisalat_500(m.chat.id, email, m.text))

# دوال معالجة أوامر الأدمن
def broadcast_process(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()
    success = 0
    for uid in users:
        try:
            bot.send_message(uid[0], f'📢 إعلان:\n{message.text}')
            success += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f'✅ تم الإرسال لـ {success} مستخدم', reply_markup=admin_panel_markup())

def block_user(message):
    uid = message.text.strip()
    if uid not in blocked_users:
        blocked_users.append(uid)
        save_json('blocked_users.json', blocked_users)
        bot.reply_to(message, f'⛔ تم حظر {uid}')
    else:
        bot.reply_to(message, 'محظور بالفعل')
    send_admin_panel(message.chat.id)

def unblock_user(message):
    uid = message.text.strip()
    if uid in blocked_users:
        blocked_users.remove(uid)
        save_json('blocked_users.json', blocked_users)
        bot.reply_to(message, f'✅ تم إلغاء حظر {uid}')
    else:
        bot.reply_to(message, 'ليس في قائمة المحظورين')
    send_admin_panel(message.chat.id)

def add_admin(message):
    uid = message.text.strip()
    if uid not in admins:
        admins.append(uid)
        save_json('admins.json', admins)
        bot.reply_to(message, f'✅ تمت إضافة {uid} كأدمن')
    else:
        bot.reply_to(message, 'هذا المستخدم أدمن بالفعل')
    send_admin_panel(message.chat.id)

def remove_admin(message):
    uid = message.text.strip()
    if uid in admins:
        admins.remove(uid)
        save_json('admins.json', admins)
        bot.reply_to(message, f'✅ تم حذف {uid} من الأدمنة')
    else:
        bot.reply_to(message, 'ليس أدمن')
    send_admin_panel(message.chat.id)

def send_admin_panel(chat_id):
    bot.send_message(chat_id, '🛠 لوحة التحكم', reply_markup=admin_panel_markup())

@bot.message_handler(func=lambda m: True)
def fallback(m):
    if m.text and not m.text.startswith('/'):
        start_cmd(m)

# ================== تشغيل البوت ==================
if __name__ == '__main__':
    print('✅ البوت يعمل بنجاح...')
    print(f'📢 القناة: {CHANNEL_ID}')
    print(f'👑 المطور: {ADMIN_ID}')
    bot.infinity_polling(timeout=60)
