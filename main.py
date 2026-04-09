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
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (status INTEGER)''')
    c.execute('SELECT status FROM settings')
    if not c.fetchone():
        c.execute('INSERT INTO settings VALUES (1)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_bot_status():
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
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
        res = "🕌 مواقيت الصلاة (القاهرة):\n\n"
        res += f"الفجر: {data['Fajr']}\nالشروق: {data['Sunrise']}\n"
        res += f"الظهر: {data['Dhuhr']}\nالعصر: {data['Asr']}\n"
        res += f"المغرب: {data['Maghrib']}\nالعشاء: {data['Isha']}"
        return res
    except: return "عذراً، تعذر جلب المواقيت حالياً."

# --- [ الكيبوردات - الأزرار تحت بعضها ] ---
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🍊 خدمات أورانج", callback_data="orange_menu"),
        types.InlineKeyboardButton("🛠️ خدمات إضافية", callback_data="extra_menu"),
        types.InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USER[1:]}")
    )
    return m

def orange_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🎁 هدية 500 ميجا", callback_data="gift_500"),
        types.InlineKeyboardButton("🧩 حل الفوازير", callback_data="solve_faw"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="home")
    )
    return m

def extra_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_times"),
        types.InlineKeyboardButton("🎨 رسم صورة AI", callback_data="draw_image"),
        types.InlineKeyboardButton("🔙 العودة للرئيسية", callback_data="home")
    )
    return m

def admin_menu():
    conn = sqlite3.connect('netmido_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    m = types.InlineKeyboardMarkup(row_width=1)
    status_label = "إيقاف البوت" if get_bot_status() == 1 else "تشغيل البوت"
    m.add(
        types.InlineKeyboardButton(f"👥 المشتركين: {count}", callback_data="none"),
        types.InlineKeyboardButton(status_label, callback_data="toggle_bot"),
        types.InlineKeyboardButton("📣 إرسال إذاعة للكل", callback_data="admin_br")
    )
    return m

# --- [ تنفيذ خدمات أورانج بالأكواد الأصلية ] ---
def run_orange(num, pwd, mode):
    session = requests.Session()
    # الهيدرز والبيانات الأصلية التي طلبتها
    headers = {'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8"}
    try:
        login_url = "https://services.orange.eg/SignIn.svc/SignInUser"
        l_pay = {"appVersion": "8.8.5", "channel": {"ChannelName": "MobinilAndMe", "Password": "ig3yh*mk5l42@oj7QAR8yF"},
                 "dialNumber": num, "isAndroid": True, "lang": "ar", "password": pwd}
        r1 = session.post(login_url, json=l_pay, timeout=15).json()
        if 'SignInUserResult' not in r1: return "البيانات غير صحيحة."
        uid = r1['SignInUserResult']['UserData']['UserID']

        t_url = "https://services.orange.eg/GetToken.svc/GenerateToken"
        r2 = session.post(t_url, data='{"channel":{"ChannelName":"MobinilAndMe","Password":"ig3yh*mk5l42@oj7QAR8yF"}}', timeout=15).json()
        ctv = r2['GenerateTokenResult']['Token']
        htv = hashlib.sha256((ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").encode()).hexdigest().upper()

        if mode == "gift":
            f_url = "https://services.orange.eg/APIs/Promotions/api/CAF/Redeem"
            p = {"Language":"ar","PromoCode":"رمضان كريم","dial":num,"password":pwd,"Channelname":"MobinilAndMe","ChannelPassword":"ig3yh*mk5l42@oj7QAR8yF"}
        else:
            f_url = "https://services.orange.eg/APIs/Promotions/api/Fawazeer/Solve"
            p = {"Language":"ar","dial":num,"password":pwd,"Channelname":"MobinilAndMe"}

        h = {"_ctv": ctv, "_htv": htv, "UserId": uid, "Content-Type": "application/json"}
        r3 = session.post(f_url, headers=h, json=p, timeout=15).json()
        
        res = r3.get('ErrorDescription', '')
        return "تمت العملية بنجاح." if res == "Success" else f"رد النظام: {res}"
    except: return "فشل الاتصال بسيرفر الشركة."

# --- [ الهاندلرز ] ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    if get_bot_status() == 0 and message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "البوت متوقف حالياً للصيانة.")
        return
    bot.send_message(message.chat.id, f"أهلاً بك في {BOT_NAME}\nاختر ما تحتاجه من القائمة:", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    cid, mid = call.message.chat.id, call.message.message_id
    
    if call.data == "home":
        bot.edit_message_text("القائمة الرئيسية:", cid, mid, reply_markup=main_menu())
    elif call.data == "orange_menu":
        bot.edit_message_text("قسم خدمات أورانج:", cid, mid, reply_markup=orange_menu())
    elif call.data == "extra_menu":
        bot.edit_message_text("قسم الخدمات الإضافية:", cid, mid, reply_markup=extra_menu())
    elif call.data == "prayer_times":
        bot.edit_message_text(get_prayer_times(), cid, mid, reply_markup=extra_menu())
    elif call.data == "draw_image":
        msg = bot.send_message(cid, "أدخل وصف الصورة بالإنجليزية:")
        bot.register_next_step_handler(msg, step_draw)
    elif call.data in ["gift_500", "solve_faw"]:
        mode = "gift" if call.data == "gift_500" else "fawazeer"
        msg = bot.send_message(cid, "أدخل رقم الهاتف:")
        bot.register_next_step_handler(msg, step_num, mode)
    elif call.data == "toggle_bot" and call.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('netmido_final.db')
        c = conn.cursor()
        new_s = 0 if get_bot_status() == 1 else 1
        c.execute('UPDATE settings SET status = ?', (new_s,))
        conn.commit()
        bot.edit_message_reply_markup(cid, mid, reply_markup=admin_menu())
    elif call.data == "admin_br" and call.from_user.id == ADMIN_ID:
        msg = bot.send_message(cid, "أدخل رسالة الإذاعة:")
        bot.register_next_step_handler(msg, step_br)

def step_num(message, mode):
    num = message.text.strip()
    if len(num) != 11: bot.send_message(message.chat.id, "الرقم خطأ."); return
    msg = bot.send_message(message.chat.id, "أدخل الباسوورد:")
    bot.register_next_step_handler(msg, step_pass, num, mode)

def step_pass(message, num, mode):
    pwd = message.text.strip()
    wait = bot.send_message(message.chat.id, "جاري التنفيذ...")
    res = run_orange(num, pwd, mode)
    bot.send_message(message.chat.id, res, reply_markup=main_menu())

def step_draw(message):
    prompt = message.text
    bot.reply_to(message, "جاري الرسم...")
    try:
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true"
        bot.send_photo(message.chat.id, url, caption="تم بواسطة Netmido", reply_markup=main_menu())
    except: bot.send_message(message.chat.id, "فشل الرسم.")

def step_br(message):
    conn = sqlite3.connect('netmido_final.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = [u[0] for u in c.fetchall()]
    for u in users:
        try: bot.send_message(u, message.text)
        except: pass
    bot.send_message(ADMIN_ID, "تمت الإذاعة.")

if __name__ == "__main__":
    bot.infinity_polling()
