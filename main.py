import telebot
import requests
import sqlite3
import hashlib
import urllib.parse
import random
from telebot import types

# --- [ الإعدادات الأساسية ] ---
API_TOKEN = '8599996419:AAFLd4JA6mDm0aw4Yzk2F0JBHjyJcuHmcSk'
ADMIN_ID = 7721807760
DEV_USER = '@AMI_EG'
BOT_NAME = "Netmido"
bot = telebot.TeleBot(API_TOKEN)

# --- [ قاعدة البيانات ] ---
def init_db():
    conn = sqlite3.connect('netmido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('netmido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    conn = sqlite3.connect('netmido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT status FROM settings')
    res = c.fetchone()
    conn.close()
    return res[0] if res else 1

init_db()

# --- [ موديول مواقيت الصلاة ] ---
def get_prayer_times():
    try:
        url = "http://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5"
        data = requests.get(url, timeout=10).json()['data']['timings']
        res = "✨ **مواقيت الصلاة - القاهرة** ✨\n"
        res += "─── • ─── • ───\n"
        res += f"🕒 الفجر: `{data['Fajr']}`\n"
        res += f"☀️ الشروق: `{data['Sunrise']}`\n"
        res += f"🕛 الظهر: `{data['Dhuhr']}`\n"
        res += f"🕒 العصر: `{data['Asr']}`\n"
        res += f"🌆 المغرب: `{data['Maghrib']}`\n"
        res += f"🌃 العشاء: `{data['Isha']}`\n"
        res += "─── • ─── • ───"
        return res
    except: return "❌ عذراً، فشل الاتصال بسيرفر المواقيت."

# --- [ الكيبوردات - تصميم مرصوص ومنظم ] ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🔸 قـسـم أورانـج 🔸", callback_data="orange_sec"),
        types.InlineKeyboardButton("🕌 مـواقـيـت الـصـلاة 🕌", callback_data="prayer_sec"),
        types.InlineKeyboardButton("🎨 رصـام الـذكـاء الاصـطـناعي 🎨", callback_data="draw_sec"),
        types.InlineKeyboardButton("👤 الـمـطـور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return m

def orange_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🎁 هـديـة 500 مـيـجـا", callback_data="gift_500"),
        types.InlineKeyboardButton("🧩 حـل الـفـوازير", callback_data="solve_faw"),
        types.InlineKeyboardButton("🔙 الـعـودة لـلـرئـيـسـيـة", callback_data="home")
    )
    return m

def admin_menu():
    conn = sqlite3.connect('netmido_ultra.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    m = types.InlineKeyboardMarkup(row_width=1)
    bot_s = "✅ الـبوت شـغـال" if get_bot_status() == 1 else "❌ الـبوت مـتـوقف"
    m.add(
        types.InlineKeyboardButton(f"📊 الـمـشـتركـين: {count}", callback_data="none"),
        types.InlineKeyboardButton(bot_s, callback_data="toggle_bot"),
        types.InlineKeyboardButton("📢 إذاعـة لـلـجـمـيـع", callback_data="broadcast"),
        types.InlineKeyboardButton("🔄 تـحـديـث الإحصائيات", callback_data="refresh_admin")
    )
    return m

# --- [ منطق أورانج البرمجي ] ---
def orange_logic(num, pwd, mode):
    session = requests.Session()
    headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
    try:
        # تسجيل الدخول
        login_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        l_data = {"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
                  "dialNumber": num, "isAndroid": True, "lang": "ar", "password": pwd}
        r1 = session.post(login_url, json=l_data, timeout=15).json()
        if 'SignInUserResult' not in r1: return "❌ البيانات غلط، راجع الرقم والباسوورد."
        uid = r1['SignInUserResult']['UserData']['UserID']

        # جلب التوكن
        t_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        r2 = session.post(t_url, data='{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}', timeout=15).json()
        ctv = r2['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        # تنفيذ الطلب
        if mode == "gift":
            f_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
            p = {"Language":"ar","PromoCode":"رمضان كريم","dial":num,"password":pwd,"Channelname":"MobinilAndMe","ChannelPassword":"ig3yh*mk5l42@oj7QAR8yF"}
        else:
            f_url = "https://services.orange.eg/APIs/Promotions/api/Fawazeer/Solve"
            p = {"Language":"ar","dial":num,"password":pwd,"Channelname":"MobinilAndMe"}

        h_final = {"_ctv": ctv, "_htv": htv, "UserId": uid, "Content-Type": "application/json"}
        r3 = session.post(f_url, headers=h_final, json=p, timeout=15).json()
        
        res = r3.get('ErrorDescription', '')
        return "✅ تمت العملية بنجاح!" if res == "Success" else f"⚠️ رد النظام: {res}"
    except: return "❌ حدث خطأ في الاتصال بسيرفر الشركة."

# --- [ معالجات البوت ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if get_bot_status() == 0 and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⚠️ الـبوت في صـيـانـة مـؤقـتـة.")
        return
    welcome = f"🌟 **مـرحـباً بـك فـي {BOT_NAME}** 🌟\n\nاخـتر مـن القـائـمـة أدناه لـلبدء:"
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠 **لوحـة تحـكم المـدير**", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    cid, mid = call.message.chat.id, call.message.message_id
    
    if call.data == "home":
        bot.edit_message_text("🌟 القائمة الرئيسية:", cid, mid, reply_markup=main_menu())
    elif call.data == "orange_sec":
        bot.edit_message_text("🍊 خدمات أورانج المتميزة:", cid, mid, reply_markup=orange_menu())
    elif call.data == "prayer_sec":
        bot.edit_message_text(get_prayer_times(), cid, mid, reply_markup=main_menu(), parse_mode="Markdown")
    elif call.data == "draw_sec":
        bot.delete_message(cid, mid)
        msg = bot.send_message(cid, "🎨 أرسل وصف الصورة (بالإنجليزي):")
        bot.register_next_step_handler(msg, draw_step)
    elif call.data in ["gift_500", "solve_faw"]:
        mode = "gift" if call.data == "gift_500" else "fawazeer"
        bot.delete_message(cid, mid)
        msg = bot.send_message(cid, "📱 أدخل رقم الهاتف (11 رقم):")
        bot.register_next_step_handler(msg, num_step, mode)
    elif call.data == "toggle_bot" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('netmido_ultra.db')
        c = conn.cursor()
        new_s = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,))
        conn.commit()
        bot.edit_message_reply_markup(cid, mid, reply_markup=admin_menu())
    elif call.data == "broadcast" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(cid, "📝 اكتب رسالة الإذاعة:")
        bot.register_next_step_handler(msg, broadcast_step)
    elif call.data == "refresh_admin" and call.from_user.id == ADMIN_ID:
        bot.edit_message_reply_markup(cid, mid, reply_markup=admin_menu())

def num_step(message, mode):
    num = message.text.strip()
    if len(num) != 11: bot.send_message(message.chat.id, "❌ الرقم غلط."); return
    msg = bot.send_message(message.chat.id, "🔐 أدخل باسوورد My Orange:")
    bot.register_next_step_handler(msg, pass_step, num, mode)

def pass_step(message, num, mode):
    pwd = message.text.strip()
    wait = bot.send_message(message.chat.id, "⏳ جاري تنفيذ طلبك...")
    res = orange_logic(num, pwd, mode)
    bot.send_message(message.chat.id, res, reply_markup=main_menu())

def draw_step(message):
    prompt = message.text
    wait = bot.reply_to(message, "🎨 جاري الإبداع...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
        bot.send_photo(message.chat.id, url, caption="✨ تم الرسم بواسطة Netmido", reply_markup=main_menu())
    except: bot.send_message(message.chat.id, "❌ فشل الرسم.")

def broadcast_step(message):
    conn = sqlite3.connect('netmido_ultra.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = [u[0] for u in c.fetchall()]
    for u in users:
        try: bot.send_message(u, message.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ تم الإرسال للجميع.")

if __name__ == "__main__":
    bot.infinity_polling()
