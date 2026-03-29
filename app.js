const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const crypto = require('crypto');
const serverless = require('serverless-http');
const app = express();

app.use(bodyParser.json());

// ========== الإعدادات والصور ==========
const BG_URL = "https://i.postimg.cc/zvQsfRp6/0b2e491cf363fb13fe72f199a1c0cde1.jpg";
const VODAFONE_ICON = "https://i.postimg.cc/SR7ZjRH4/Screenshot-20260213-154727-Google.jpg";
const ORANGE_ICON = "https://i.postimg.cc/MTT2tnyL/IMG-20260219-104918-030.jpg";
const ETISALAT_ICON = "https://i.postimg.cc/63Mrnrkh/Screenshot-20260328-235637-Google.jpg";
const TG_CHANNEL = "https://t.me/mido90femeah";
const DEVELOPER_USER = "@AMI_EG";

// ========== [ الدوال البرمجية المحدثة ] ==========

// 1. استعلام رصيد أورانج المحدث
async function checkOrangeBalance(phone) {
    try {
        const res = await axios.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", 
        { SelectedUserDial: null, IsForAnotherRecipient: true, RecipientDial: phone, Dial: phone },
        { headers: { "lang": "en" } });
        if (res.data.CreditBalance !== undefined) return { success: true, msg: `رصيدك الحالي هو: ${res.data.CreditBalance} جنيهاً` };
        return { success: false, msg: "تعذر جلب الرصيد، تأكد من الرقم" };
    } catch (e) { return { success: false, msg: "خطأ في الاتصال بسيرفر أورانج" }; }
}

// 2. تفعيل 500 ميجا أورانج (الهدية الجديدة)
async function runOrange500(phone, password) {
    try {
        const login = await axios.post("https://services.orange.eg/SignIn.svc/SignInUser", {
            appVersion: "8.8.5", channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" },
            dialNumber: phone, isAndroid: true, lang: "ar", password: password
        });
        const userId = login.data.SignInUserResult.UserData.UserID;
        const tokenRes = await axios.post("https://services.orange.eg/GetToken.svc/GenerateToken", { channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" } });
        const ctv = tokenRes.data.GenerateTokenResult.Token;
        const htv = crypto.createHash('sha256').update(ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").digest('hex').toUpperCase();
        
        const redeem = await axios.post("https://services.orange.eg/APIs/Promotions/api/CAF/Redeem", 
            { Language: "ar", OSVersion: "Android7.0", PromoCode: "رمضان كريم", dial: phone, password: password, Channelname: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF" },
            { headers: { "_ctv": ctv, "_htv": htv, "UserId": userId } });
        
        if (redeem.data.ErrorDescription === "Success") return { success: true, msg: "مبروك! استلمت 500 ميجا بنجاح 🎉" };
        return { success: false, msg: redeem.data.ErrorDescription || "العرض غير متاح حالياً" };
    } catch (e) { return { success: false, msg: "حدث خطأ أثناء التفعيل" }; }
}

// 3. تفعيل هدايا اتصالات (سوشيال / استريمينج)
async function runEtisalatGift(email, password, giftType) {
    try {
        const auth = Buffer.from(`${email}:${password}`).toString('base64');
        const login = await axios.post("https://mab.etisalat.com.eg:11003/Saytar/rest/authentication/loginWithPlan", 
            "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><loginRequest><platform>Android</platform></loginRequest>",
            { headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'text/xml', 'applicationName': 'MAB' } });
        
        const dialMatch = login.data.match(/<dial>(.*?)<\/dial>/);
        if (!dialMatch) return { success: false, msg: "البريد أو الباسورد خطأ" };
        const number = dialMatch[1];

        let url = giftType === 'social' ? "https://mab.etisalat.com.eg:11003/Saytar/rest/rtim/rtimSubmitOrder" : "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2";
        let payload = giftType === 'social' 
            ? `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><rtimSubmitOrder><extraProductId>22932</extraProductId><offerId>22932</offerId><operationId>REDEEM</operationId><productId>RTIM_OFFERS=Offer_ID:22932;isRTIM:Y</productId><subscriberNumber>${number}</subscriberNumber></rtimSubmitOrder>`
            : `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><msisdn>${number}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>`;

        await axios.post(url, payload, { headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'text/xml', 'applicationName': 'MAB' } });
        return { success: true, msg: "تم إرسال طلب تفعيل الهدية بنجاح ✅" };
    } catch (e) { return { success: false, msg: "فشل في تفعيل عرض اتصالات" }; }
}

// ========== [ الواجهة الأمامية - UI ] ==========

app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO - تليكوم 2026</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Orbitron:wght@600;900&display=swap');
        
        :root {
            --neon-blue: #00d2ff;
            --neon-red: #ff0055;
            --glass-bg: rgba(0, 0, 0, 0.7);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Cairo', sans-serif;
            background: #050505 url('${BG_URL}') no-repeat center center fixed;
            background-size: cover;
            min-height: 100vh;
            color: white; display: flex; justify-content: center; align-items: center;
            overflow-x: hidden;
        }

        .main-wrapper {
            width: 95%; max-width: 450px;
            backdrop-filter: blur(8px);
            padding: 20px; text-align: center;
        }

        h1 {
            font-family: 'Orbitron', sans-serif; font-size: 3.5rem;
            margin-bottom: 40px; letter-spacing: 10px;
            text-shadow: 0 0 10px var(--neon-blue), 0 0 20px var(--neon-red);
        }

        .view-panel { display: none; animation: fadeIn 0.5s ease; }
        .view-panel.active { display: block; }

        @keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

        /* أزرار بدون حدود (Borderless) */
        .neon-btn {
            width: 100%; padding: 20px; margin-bottom: 20px;
            background: var(--glass-bg);
            border: none; border-left: 4px solid var(--neon-blue);
            color: white; font-size: 1.3rem; font-weight: 900;
            cursor: pointer; display: flex; align-items: center; justify-content: space-between;
            transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border-radius: 10px 40px 40px 10px;
        }

        .neon-btn:active {
            transform: perspective(500px) rotateX(10deg) rotateY(-15deg) translateY(8px);
            box-shadow: -10px 10px 30px rgba(0, 210, 255, 0.4);
            background: rgba(0, 210, 255, 0.1);
        }

        .neon-btn img { width: 45px; height: 45px; border-radius: 50%; border: 2px solid white; }

        .sub-btn {
            width: 100%; padding: 15px; margin-bottom: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--neon-red); color: white;
            border-radius: 15px; cursor: pointer; transition: 0.2s;
            font-weight: bold;
        }

        .sub-btn:hover { background: var(--neon-red); box-shadow: 0 0 15px var(--neon-red); }

        .input-box {
            width: 100%; padding: 15px; margin-bottom: 10px;
            background: rgba(0,0,0,0.8); border: 1px solid #333;
            color: white; border-radius: 12px; text-align: center;
        }

        /* شات بوت */
        #chat-trigger {
            position: fixed; bottom: 30px; right: 30px;
            width: 65px; height: 65px; background: var(--neon-blue);
            border-radius: 50%; display: flex; justify-content: center; align-items: center;
            font-size: 2rem; cursor: pointer; box-shadow: 0 0 20px var(--neon-blue);
            z-index: 1000;
        }

        footer { margin-top: 30px; font-size: 0.75rem; opacity: 0.5; letter-spacing: 2px; }
        .links { margin-top: 15px; display: flex; justify-content: center; gap: 20px; }
        .links a { color: var(--neon-blue); font-size: 1.5rem; text-decoration: none; }

    </style>
</head>
<body>

<div class="main-wrapper">
    <h1>MIDO</h1>

    <div id="home" class="view-panel active">
        <button class="neon-btn" onclick="showView('voda')">
            <span>فودافون</span>
            <img src="${VODAFONE_ICON}">
        </button>
        <button class="neon-btn" onclick="showView('orange')" style="border-left-color: #ff6600;">
            <span>أورانج</span>
            <img src="${ORANGE_ICON}">
        </button>
        <button class="neon-btn" onclick="showView('etisalat')" style="border-left-color: #719c30;">
            <span>اتصالات</span>
            <img src="${ETISALAT_ICON}">
        </button>
        
        <div class="links">
            <a href="https://t.me/mido90femeah" target="_blank" title="القناة"><i class="fab fa-telegram"></i></a>
            <a href="https://t.me/AMI_EG" target="_blank" title="المطور"><i class="fas fa-code"></i></a>
        </div>
    </div>

    <div id="voda" class="view-panel">
        <button onclick="showView('home')" style="background:none; border:none; color:#888; cursor:pointer; margin-bottom:20px;">رجوع للرئيسية</button>
        <button class="sub-btn" onclick="openForm('vodaSummer', 'هدية الصيف 2026')">هدية الصيف (1000 ميجا)</button>
        <button class="sub-btn" onclick="openForm('voda500', 'هدية 500 ميجا')">تفعيل 500 ميجا مجاناً</button>
    </div>

    <div id="orange" class="view-panel">
        <button onclick="showView('home')" style="background:none; border:none; color:#888; cursor:pointer; margin-bottom:20px;">رجوع للرئيسية</button>
        <button class="sub-btn" onclick="openForm('orange500', 'هدية 500 ميجا أورانج')">تفعيل 500 ميجا (رمضان)</button>
        <button class="sub-btn" onclick="openForm('orangeBalance', 'معرفة الرصيد مجاناً')">استعلام الرصيد (تحديث 2026)</button>
        <button class="sub-btn" onclick="openForm('orangeFawazeer', 'حل الفوازير')">حل فوازير رمضان</button>
    </div>

    <div id="etisalat" class="view-panel">
        <button onclick="showView('home')" style="background:none; border:none; color:#888; cursor:pointer; margin-bottom:20px;">رجوع للرئيسية</button>
        <button class="sub-btn" onclick="openForm('etisalatSocial', '500M سوشيال')">500 ميجا سوشيال</button>
        <button class="sub-btn" onclick="openForm('etisalatStream', '500M استريمينج')">500 ميجا استريمينج</button>
    </div>

    <div id="form-view" class="view-panel">
        <h2 id="form-title" style="margin-bottom:20px; color:var(--neon-blue);"></h2>
        <input type="tel" id="u_phone" class="input-box" placeholder="رقم الهاتف">
        <input type="password" id="u_pass" class="input-box" placeholder="كلمة المرور">
        <input type="email" id="u_email" class="input-box" placeholder="البريد الإلكتروني" style="display:none;">
        <button class="sub-btn" style="background:var(--neon-blue); border:none; margin-top:10px;" onclick="process()">تفعيل العرض ⚡</button>
        <button onclick="showView('home')" style="background:none; border:none; color:#ff0055; cursor:pointer; margin-top:15px;">إلغاء</button>
    </div>

    <footer>حقوق المطور ${DEVELOPER_USER} محفوظة © 2026</footer>
</div>

<div id="chat-trigger" onclick="openChat()"><i class="fas fa-comment-dots"></i></div>

<script>
    let activeType = '';
    function showView(id) {
        document.querySelectorAll('.view-panel').forEach(v => v.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    function openForm(type, title) {
        activeType = type;
        document.getElementById('form-title').innerText = title;
        document.getElementById('u_email').style.display = (type.includes('etisalat')) ? 'block' : 'none';
        document.getElementById('u_pass').style.display = (type === 'orangeBalance') ? 'none' : 'block';
        showView('form-view');
    }

    async function process() {
        const phone = document.getElementById('u_phone').value;
        const pass = document.getElementById('u_pass').value;
        const email = document.getElementById('u_email').value;

        Swal.fire({ title: 'جاري المعالجة...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

        try {
            const res = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ type: activeType, phone, pass, email })
            });
            const data = await res.json();
            Swal.fire(data.success ? 'تم بنجاح' : 'خطأ', data.msg, data.success ? 'success' : 'error');
        } catch(e) { Swal.fire('خطأ', 'فشل في الاتصال بالسيرفر', 'error'); }
    }

    async function openChat() {
        const { value: query } = await Swal.fire({
            title: 'مساعد MIDO الذكي',
            input: 'text',
            inputPlaceholder: 'اسأل عن عروض، مواقيت الصلاة، المطور...',
            showCancelButton: true, confirmButtonText: 'إرسال', background: '#000', color: '#fff'
        });

        if(query) {
            let reply = "أنا مساعد MIDO، اسأل عن (عروض، صلاة، مطور)";
            const q = query.toLowerCase();
            if(q.includes('صلاة')) reply = "مواقيت الصلاة لليوم (القاهرة): الفجر 4:20، الظهر 12:05، العصر 3:40، المغرب 6:15، العشاء 7:40.";
            else if(q.includes('عروض')) reply = "عندنا عروض 500 ميجا لأورانج واتصالات، و1000 ميجا لفودافون! اختار شركتك وجرب.";
            else if(q.includes('مطور')) reply = "المطور هو @AMI_EG، تقدر تكلمه لو واجهت أي مشكلة في التفعيل.";
            
            Swal.fire({ title: 'الرد:', text: reply, icon: 'info', background: '#000', color: '#00d2ff' });
        }
    }
</script>
</body>
</html>
    `);
});

app.post('/submit', async (req, res) => {
    const { type, phone, pass, email } = req.body;
    let out = { success: false, msg: "الخدمة تحت الصيانة" };
    try {
        if (type === 'orangeBalance') out = await checkOrangeBalance(phone);
        else if (type === 'orange500') out = await runOrange500(phone, pass);
        else if (type === 'etisalatSocial') out = await runEtisalatGift(email, pass, 'social');
        else if (type === 'etisalatStream') out = await runEtisalatGift(email, pass, 'stream');
        // هنا يتم استدعاء باقي الوظائف بنفس النمط
    } catch(e) { out.msg = "حدث خطأ غير متوقع"; }
    res.json(out);
});

module.exports = app;
module.exports.handler = serverless(app);
