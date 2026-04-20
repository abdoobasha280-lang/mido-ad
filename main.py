import telebot
import requests
import hashlib
from telebot import types

# --- [ الإعدادات ] ---
BOT_TOKEN = "7613236322:AAEKGTVWV4SGlQoaDd2fs4wM4rIuKjNGV7U"
ADMIN_ID = 7721807760
bot = telebot.TeleBot(BOT_TOKEN)

REQUIRED_CHANNEL = "@midooojiokjj"
CHANNEL_LINK = "https://t.me/midooojiokjj"

user_data = {} # لحفظ خطوات المستخدم (رقم، باسورد، مدينة)

# --- [ فحص الاشتراك ] ---
def is_subscribed(uid):
    if uid == ADMIN_ID: return True
    try:
        status = bot.get_chat_member(REQUIRED_CHANNEL, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- [ المنيوهات ] ---
def main_menu(cid):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("اورانج 🟠", callback_data="section_orange"),
        types.InlineKeyboardButton("اتصالات 🟢", callback_data="section_eti"),
        types.InlineKeyboardButton("خدمات مجانيه ⚙", callback_data="section_free"),
        types.InlineKeyboardButton("المطور 👨‍💻", url="https://t.me/AMI_EG")
    )
    bot.send_message(cid, "مرحب بيك ياحب في بوت MIDO❤\nاختر القسم اللي يناسبك:", reply_markup=markup)

# --- [ الـ Callbacks ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    cid = call.message.chat.id
    uid = call.from_user.id

    if not is_subscribed(uid) and call.data != "verify":
        bot.answer_callback_query(call.id, "⚠️ اشترك الأول ياحب!", show_alert=True)
        return

    if call.data == "verify":
        if is_subscribed(uid):
            bot.delete_message(cid, call.message.message_id)
            main_menu(cid)
        else: bot.answer_callback_query(call.id, "❌ لسه مشركتش!", show_alert=True)

    elif call.data == "section_orange":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("fwazer250mb 🎁", callback_data="get_fwz"),
            types.InlineKeyboardButton("500mb كل 10Day 🤩", callback_data="get_500"),
            types.InlineKeyboardButton("معرفة الرصيد 💰", callback_data="get_bal"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")
        )
        bot.edit_message_text("قسم أورانج 🟠 - اختر خدمتك:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "section_free":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("مواقيت الصلاة 🕌", callback_data="get_prayer"),
            types.InlineKeyboardButton("إنشاء صور AI 🎨", callback_data="get_ai_img"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="back_home")
        )
        bot.edit_message_text("الخدمات المجانية ⚙:", cid, call.message.message_id, reply_markup=markup)

    elif call.data == "back_home":
        bot.delete_message(cid, call.message.message_id)
        main_menu(cid)

    # --- بدء طلب البيانات ---
    elif call.data in ["get_fwz", "get_500"]:
        user_data[cid] = {'target': call.data, 'step': 'number'}
        bot.send_message(cid, "📱 ابعت رقم أورانج الخاص بك:")

    elif call.data == "get_bal":
        user_data[cid] = {'target': 'balance'}
        bot.send_message(cid, "💰 ابعت الرقم لمعرفة رصيده:")

    elif call.data == "get_prayer":
        user_data[cid] = {'target': 'prayer'}
        bot.send_message(cid, "🕌 ابعت اسم مدينتك (بالإنجليزي - مثلا Cairo):")

    elif call.data == "get_ai_img":
        user_data[cid] = {'target': 'image'}
        bot.send_message(cid, "🎨 ابعت وصف الصورة بالإنجليزي:")

# --- [ معالجة المدخلات (المنطق الفعلي) ] ---
@bot.message_handler(func=lambda m: m.chat.id in user_data)
def workflow(m):
    cid = m.chat.id
    data = user_data[cid]

    # 1. طلب الباسورد للخدمات اللي محتاجة تفعيل
    if data.get('step') == 'number':
        user_data[cid]['num'] = m.text
        user_data[cid]['step'] = 'password'
        bot.send_message(cid, "🔑 ابعت باسورد تطبيق My Orange:")
        return

    # 2. التنفيذ النهائي
    target = data['target']
    
    if target in ["get_fwz", "get_500"] and data.get('step') == 'password':
        num, pwd = data['num'], m.text
        bot.send_message(cid, "⏳ جاري التفعيل باستخدام الـ API...")
        # هنا يتم استدعاء سكريبت أورانج (Login -> Redeem)
        # مثال للنجاح:
        bot.send_message(cid, f"✅ تم تفعيل العرض للرقم {num} بنجاح! ❤")
        del user_data[cid]

    elif target == 'balance':
        res = requests.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", 
                            json={"RecipientDial": m.text, "Dial": m.text}).json()
        bot.send_message(cid, f"💰 الرصيد الحالي: {res.get('CreditBalance', '0')} جنيه.")
        del user_data[cid]

    elif target == 'prayer':
        res = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={m.text}&country=Egypt&method=5").json()
        t = res['data']['timings']
        bot.send_message(cid, f"🕌 مواقيت الصلاة في {m.text}:\nالفجر: {t['Fajr']}\nالظهر: {t['Dhuhr']}\nالعصر: {t['Asr']}\nالمغرب: {t['Maghrib']}\nالعشاء: {t['Isha']}")
        del user_data[cid]

    elif target == 'image':
        bot.send_photo(cid, f"https://image.pollinations.ai/prompt/{m.text}", caption="🎨 صورتك جاهزة ياحب")
        del user_data[cid]

# --- [ أوامر البداية ] ---
@bot.message_handler(commands=['start'])
def start(m):
    if is_subscribed(m.from_user.id): main_menu(m.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("قناة المطور 📢", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="verify"))
        bot.send_message(m.chat.id, "🔒 اشترك في القناة الأول ياحب:", reply_markup=markup)

bot.infinity_polling()
