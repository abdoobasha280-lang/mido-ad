import telebot
import requests
import json
import sqlite3
import time
import hashlib
import random
import urllib.parse
from telebot import types

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'
BOT_NAME = "Netmido"
bot = telebot.TeleBot(API_TOKEN)

# إحصائيات
stats = {"success": 0, "failed": 0}
user_step_data = {}

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

init_db()

def add_user(user_id):
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

# --- [ موديول الصلاة - API مباشر ] ---
def get_prayer_times():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
        data = requests.get(url, timeout=10).json()['data']['timings']
        res = f"🕌 **مواقيت الصلاة | {BOT_NAME}**\n\n"
        res += f"🔹 الفجر: `{data['Fajr']}`\n🔹 الشروق: `{data['Sunrise']}`\n"
        res += f"🔹 الظهر: `{data['Dhuhr']}`\n🔹 العصر: `{data['Asr']}`\n"
        res += f"🔹 المغرب: `{data['Maghrib']}`\n🔹 العشاء: `{data['Isha']}`"
        return res
    except: return "❌ فشل اتصال السيرفر بالمواقيت."

# --- [ الكيبوردات (أزرار تحت بعضها) ] ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🍊 خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_services"),
        types.InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return m

def orange_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="gift_500"),
        types.InlineKeyboardButton("🧩 حل فوازير شريهان", callback_data="solve_fawazeer"),
        types.InlineKeyboardButton("🔙 العودة", callback_data="main_home")
    )
    return m

def extra_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🎨 رسم صورة AI", callback_data="draw_image"),
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times"),
        types.InlineKeyboardButton("🔙 العودة", callback_data="main_home")
    )
    return m

# --- [ منطق أورانج البرمجي الكامل ] ---
def orange_api_call(number, password, mode):
    session = requests.Session()
    headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
    
    try:
        # 1. Login
        login_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        login_data = {
            "appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
            "dialNumber": number, "isAndroid": True, "lang": "ar", "password": password
        }
        r1 = session.post(login_url, json=login_data, timeout=15).json()
        if 'SignInUserResult' not in r1: return "❌ الباسوورد أو الرقم غلط."
        uid = r1['SignInUserResult']['UserData']['UserID']

        # 2. Token Generation
        t_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        t_payload = '{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}'
        r2 = session.post(t_url, headers=headers, data=t_payload, timeout=15).json()
        ctv = r2['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        # 3. Execution (Gift or Fawazeer)
        if mode == "gift":
            final_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
            payload = {"Language":"ar","PromoCode":"رمضان كريم","dial":number,"password":password,"Channelname":"MobinilAndMe","ChannelPassword":"ig3yh*mk5l42@oj7QAR8yF"}
        else:
            final_url = "https://services.orange.eg/APIs/Promotions/api/Fawazeer/Solve"
            payload = {"Language":"ar","dial":number,"password":password,"Channelname":"MobinilAndMe"}

        h_final = {"_ctv": ctv, "_htv": htv, "UserId": uid, "Content-Type": "application/json"}
        r3 = session.post(final_url, headers=h_final, json=payload, timeout=15).json()
        
        desc = r3.get('ErrorDescription', 'تمت العملية')
        if desc == "Success": return "✅ مبروك! العملية تمت بنجاح."
        return f"⚠️ رد أورانج: {desc}"
    except: return "❌ عذراً، سيرفر أورانج لا يستجيب حالياً."

# --- [ المعالجات Handlers ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    bot.send_message(message.chat.id, f"✨ أهلاً بك في **{BOT_NAME}**\nأسرع بوت لخدمات أورانج والذكاء الاصطناعي.", reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid = call.message.chat.id
    if call.data == "main_home":
        bot.edit_message_text("✨ القائمة الرئيسية:", cid, call.message.message_id, reply_markup=main_menu())
    elif call.data == "orange_menu":
        bot.edit_message_text("🍊 خدمات أورانج:", cid, call.message.message_id, reply_markup=orange_menu())
    elif call.data == "extra_services":
        bot.edit_message_text("🛠️ خدمات إضافية:", cid, call.message.message_id, reply_markup=extra_menu())
    elif call.data == "prayer_times":
        bot.edit_message_text(get_prayer_times(), cid, call.message.message_id, reply_markup=extra_menu(), parse_mode="Markdown")
    elif call.data == "gift_500" or call.data == "solve_fawazeer":
        mode = "gift" if call.data == "gift_500" else "fawazeer"
        bot.delete_message(cid, call.message.message_id)
        msg = bot.send_message(cid, "📱 أرسل رقم أورانج الآن:")
        bot.register_next_step_handler(msg, get_num, mode)
    elif call.data == "draw_image":
        bot.delete_message(cid, call.message.message_id)
        msg = bot.send_message(cid, "🎨 أرسل وصف الصورة (بالإنجليزي أفضل):")
        bot.register_next_step_handler(msg, process_draw)

def get_num(message, mode):
    num = message.text.strip()
    if len(num) != 11: 
        bot.send_message(message.chat.id, "❌ الرقم غلط.")
        return
    msg = bot.send_message(message.chat.id, "🔐 أرسل كلمة سر My Orange:")
    bot.register_next_step_handler(msg, get_pass, num, mode)

def get_pass(message, num, mode):
    pwd = message.text.strip()
    wait = bot.send_message(message.chat.id, "⏳ جاري التنفيذ... فكك من التقل ده البوت طلقة!")
    res = orange_api_call(num, pwd, mode)
    bot.edit_message_text(res, message.chat.id, wait.message_id, reply_markup=main_menu())

def process_draw(message):
    prompt = message.text
    wait = bot.reply_to(message, "🎨 نانو بنانا بيرسم...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={random.randint(1,99)}&nologo=true"
        bot.send_photo(message.chat.id, url, caption=f"✨ تم بواسطة {BOT_NAME}", reply_markup=main_menu())
        bot.delete_message(message.chat.id, wait.message_id)
    except: bot.edit_message_text("❌ خطأ بالرسم.", message.chat.id, wait.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
