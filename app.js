const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const crypto = require('crypto');
const serverless = require('serverless-http'); // مهم جداً للرفع على نيتليفاي
const app = express();

app.use(bodyParser.json());

// ========== إعدادات الموقع الثابتة ==========
const BG_URL = "https://i.postimg.cc/zvQsfRp6/0b2e491cf363fb13fe72f199a1c0cde1.jpg";
const VODAFONE_ICON = "https://i.postimg.cc/SR7ZjRH4/Screenshot-20260213-154727-Google.jpg";
const ORANGE_ICON = "https://i.postimg.cc/MTT2tnyL/IMG-20260219-104918-030.jpg";
const TG_CHANNEL = "https://t.me/mido90femeah";
const DEVELOPER_USER = "@AMI_EG";

const api = axios.create({ 
    timeout: 15000,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
});

// ========== [ الدوال البرمجية الكاملة ] ==========

// 1. فوازير أورانج
async function runOrangeFawazeer(phone, password) {
    try {
        const session = axios.create({ headers: { 'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json; charset=UTF-8" } });
        const auth = await session.post("https://services.orange.eg/SignIn.svc/SignInUser", {
            appVersion: "9.0.1",
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" },
            dialNumber: phone, isAndroid: true, lang: "ar", password: password
        });
        const accToken = auth.data.SignInUserResult.AccessToken;
        const gen = await session.post("https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate", 
            { ChannelName: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", Dial: phone, Language: "ar", Module: "0", Password: password },
            { headers: { 'Token': accToken } });
        const token = gen.data.Token;
        const qRes = await session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions", { Dial: phone, Language: "ar", Token: token }, { headers: { 'Token': accToken } });
        if (qRes.data.ErrorCode === 1) return { success: false, msg: "لقد شاركت اليوم بالفعل، جرب غداً." };
        const answers = qRes.data.Questions.map(q => {
            const correct = q.Answers.find(a => a.IsCorrect);
            return { QuestionId: correct.QuestionId, AnswerId: correct.Id };
        });
        const submit = await session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit", { Dial: phone, Language: "ar", Token: token, Answers: answers }, { headers: { 'Token': accToken } });
        if (submit.data.ErrorDescription === "FawazeerSuccess") return { success: true, msg: "تم حل الفوازير واستلام 250 ميجا ✅" };
        return { success: false, msg: submit.data.ErrorDescription };
    } catch (e) { return { success: false, msg: "فشل في تسجيل الدخول، تأكد من البيانات" }; }
}

// 2. هدية صيف فودافون 1000 ميجا
async function runVodafoneSummer(phone, password) {
    try {
        const auth = await api.post("https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${phone}&password=${password}&client_secret=95fd95fb-7489-4958-8ae6-d31a525cd20a&client_id=ana-vodafone-app`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        const token = auth.data.access_token;
        await api.post("https://web.vodafone.com.eg/services/dxl/promo/promotion", 
            {"@type":"Promo","channel":{"id":"5"},"context":{"type":"massSummerPromo25"},"pattern":[{"characteristics":[{"name":"numberOfFaces","value":0},{"name":"giftId","value":"18"}]}]},
            { headers: { 'Authorization': `Bearer ${token}`, 'msisdn': phone, 'channel': 'APP_PORTAL', 'clientId': 'WebsiteConsumer' } });
        return { success: true, msg: "تم إضافة 1000 ميجا بنجاح ✅" };
    } catch (e) { return { success: false, msg: "العرض غير متاح حالياً أو تم استلامه مسبقاً" }; }
}

// 3. عجلة أورانج
async function runOrangeWheel(phone, password) {
    try {
        const tokenRes = await api.post("https://services.orange.eg/GetToken.svc/GenerateToken", { channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" } });
        const ctv = tokenRes.data.GenerateTokenResult.Token;
        const htv = crypto.createHash('sha256').update(ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").digest('hex').toUpperCase();
        const headers = { '_ctv': ctv, '_htv': htv, 'Content-Type': "application/json" };
        const spin = await api.post("https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin", { ChannelName: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", Dial: phone, Language: "en", Password: password, ServiceClassId: "1033" }, { headers });
        if (!spin.data.OfferDetails) return { success: false, msg: "لا توجد محاولات اليوم" };
        const { OfferId, OfferName } = spin.data.OfferDetails;
        await api.post("https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill", { CategoryId: "0", ChannelName: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", Dial: phone, Language: "en", OfferId, Password: password, ServiceClassId: "1033" }, { headers });
        return { success: true, msg: `كسبت: ${OfferName} ✅` };
    } catch (e) { return { success: false, msg: "حدث خطأ في تشغيل العجلة" }; }
}

// 4. رصيد أورانج
async function checkOrangeBalance(phone) {
    try {
        const res = await api.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", { RecipientDial: phone, Dial: phone });
        if (res.data.ErrorCode === 0) return { success: true, msg: `رصيدك الحالي: ${res.data.CreditBalance} ج` };
        return { success: false, msg: res.data.ErrorDescription || "تعذر الاستعلام" };
    } catch (e) { return { success: false, msg: "خطأ في الاتصال بالخدمة" }; }
}

// 5. اتصالات 500 ميجا
async function runEtisalat500(phone, email, password) {
    try {
        const auth = Buffer.from(`${email}:${password}`).toString('base64');
        const msisdn = phone.startsWith('0') ? phone.substring(1) : phone;
        const payload = `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><submitOrderRequest><msisdn>${msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>`;
        const res = await api.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", payload, { headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'text/xml', 'applicationName': 'MAB' } });
        if (res.data.includes("success") || res.data.includes("true")) return { success: true, msg: "تم تفعيل 500 ميجا بنجاح ✅" };
        return { success: false, msg: "البيانات غير صحيحة أو العرض غير متاح" };
    } catch (e) { return { success: false, msg: "فشل الاتصال بسيرفر اتصالات" }; }
}

// ========== [ الواجهة الأمامية - UI ] ==========

app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO - خدمات الشبكات</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Orbitron:wght@500;800&display=swap');
        
        :root {
            --main-bg: #050505;
            --neon-red: #ff003c;
            --neon-blue: #008cff;
            --neon-black: #111;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Cairo', sans-serif;
            background: var(--main-bg) url('${BG_URL}') no-repeat center center fixed;
            background-size: cover;
            min-height: 100vh;
            display: flex; justify-content: center; align-items: center;
            color: white; overflow-x: hidden;
        }

        .main-card {
            width: 95%; max-width: 480px;
            background: rgba(0, 0, 0, 0.85);
            border-radius: 25px;
            padding: 30px;
            border: 2px solid var(--neon-blue);
            box-shadow: 0 0 15px var(--neon-blue), inset 0 0 10px rgba(0, 140, 255, 0.2);
            backdrop-filter: blur(15px);
            animation: pulse-border 4s infinite;
        }

        @keyframes pulse-border {
            0%, 100% { border-color: var(--neon-blue); box-shadow: 0 0 15px var(--neon-blue); }
            50% { border-color: var(--neon-red); box-shadow: 0 0 25px var(--neon-red); }
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem; text-align: center; margin-bottom: 25px;
            background: linear-gradient(to right, var(--neon-blue), var(--neon-red));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: 8px; font-weight: 800;
        }

        .company-box {
            background: var(--neon-black);
            margin-bottom: 15px; border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden; transition: 0.3s;
        }

        .company-header {
            padding: 15px 20px; display: flex; align-items: center; justify-content: space-between;
            cursor: pointer; background: rgba(255,255,255,0.02);
        }

        .company-header:hover { background: rgba(255,255,255,0.05); }

        .company-info { display: flex; align-items: center; gap: 12px; font-weight: 900; font-size: 1.1rem; }
        .company-logo { width: 35px; height: 35px; border-radius: 50%; border: 1.5px solid var(--neon-blue); box-shadow: 0 0 8px var(--neon-blue); }
        .fa-bolt { color: #fcc203; animation: blink 1s infinite; }

        @keyframes blink { 50% { opacity: 0.2; } }

        .offers-area { display: none; padding: 15px; flex-direction: column; gap: 10px; background: rgba(0,0,0,0.4); border-top: 1px solid rgba(255,255,255,0.05); }

        .btn-neon {
            background: transparent; border: 1px solid var(--neon-blue);
            color: white; padding: 12px; border-radius: 12px;
            cursor: pointer; transition: 0.3s; font-weight: bold;
            display: flex; align-items: center; justify-content: center; gap: 10px;
        }

        .btn-neon:hover {
            background: var(--neon-blue); color: black;
            box-shadow: 0 0 15px var(--neon-blue); transform: translateY(-2px);
        }

        .input-group {
            display: none; margin-top: 25px; padding: 20px;
            background: rgba(20,20,20,0.9); border-radius: 15px;
            border: 1px solid var(--neon-red); animation: fadeIn 0.4s;
        }

        input {
            width: 100%; padding: 14px; margin-bottom: 12px;
            background: #000; border: 1px solid #333;
            color: white; border-radius: 10px; text-align: center; font-family: 'Cairo';
        }

        input:focus { border-color: var(--neon-blue); outline: none; box-shadow: 0 0 10px var(--neon-blue); }

        .btn-submit { background: var(--neon-red); border: none; color: white; width: 100%; padding: 15px; border-radius: 12px; font-weight: bold; cursor: pointer; box-shadow: 0 0 10px var(--neon-red); }

        #bot-icon {
            position: fixed; bottom: 25px; right: 25px;
            width: 65px; height: 65px; background: var(--neon-blue);
            border-radius: 50%; display: flex; justify-content: center; align-items: center;
            font-size: 1.8rem; cursor: pointer; box-shadow: 0 0 20px var(--neon-blue);
            transition: 0.3s; z-index: 1000;
        }

        #bot-icon:hover { transform: scale(1.1) rotate(10deg); background: var(--neon-red); box-shadow: 0 0 20px var(--neon-red); }

        footer { text-align: center; margin-top: 25px; font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; }
        .tg-btn { color: var(--neon-blue); font-size: 1.8rem; display: block; margin-top: 10px; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

<div class="main-card">
    <h1>MIDO</h1>

    <div class="company-box">
        <div class="company-header" onclick="toggleSection('vf-list')">
            <div class="company-info"><i class="fas fa-bolt"></i> VODAFONE</div>
            <img src="${VODAFONE_ICON}" class="company-logo">
        </div>
        <div id="vf-list" class="offers-area">
            <button class="btn-neon" onclick="showForm('vodafoneSummer', 'هدية الصيف 1000M')"><i class="fas fa-gift"></i> هدية الصيف 1000M</button>
            <button class="btn-neon" onclick="showForm('vodafoneDiscount', 'خصم 50% فليكس')"><i class="fas fa-percent"></i> خصم 50% على الباقة</button>
        </div>
    </div>

    <div class="company-box">
        <div class="company-header" onclick="toggleSection('or-list')">
            <div class="company-info"><i class="fas fa-bolt"></i> ORANGE</div>
            <img src="${ORANGE_ICON}" class="company-logo">
        </div>
        <div id="or-list" class="offers-area">
            <button class="btn-neon" onclick="showForm('orangeFawazeer', 'حل الفوازير 250M')"><i class="fas fa-lightbulb"></i> حل فوازير رمضان</button>
            <button class="btn-neon" onclick="showForm('orangeWheel', 'لف عجلة الحظ')"><i class="fas fa-sync-alt"></i> عجلة الحظ</button>
            <button class="btn-neon" onclick="showForm('orangeBalance', 'استعلام الرصيد')"><i class="fas fa-coins"></i> استعلام الرصيد</button>
        </div>
    </div>

    <div class="company-box">
        <div class="company-header" onclick="toggleSection('et-list')">
            <div class="company-info"><i class="fas fa-bolt"></i> ETISALAT</div>
            <div style="font-size: 1.5rem;">💚</div>
        </div>
        <div id="et-list" class="offers-area">
            <button class="btn-neon" onclick="showForm('etisalat500', 'هدية 500M')"><i class="fas fa-mobile"></i> تفعيل 500 ميجا</button>
        </div>
    </div>

    <div id="dynamic-form" class="input-group">
        <h3 id="form-title" style="text-align:center; color:var(--neon-blue); margin-bottom:15px;"></h3>
        <input type="tel" id="u_phone" placeholder="رقم الموبايل">
        <input type="password" id="u_pass" placeholder="كلمة المرور">
        <input type="email" id="u_email" placeholder="البريد الإلكتروني" style="display:none;">
        <button class="btn-submit" onclick="execute()">تفعيل الخدمة ⚡</button>
        <button class="btn-neon" style="width:100%; margin-top:8px; border-color:#444;" onclick="hideForm()">إلغاء</button>
    </div>

    <footer>
        <p>المطور: ${DEVELOPER_USER} | 2026</p>
        <a href="${TG_CHANNEL}" class="tg-btn"><i class="fab fa-telegram"></i></a>
    </footer>
</div>

<div id="bot-icon" onclick="botHelp()"><i class="fas fa-robot"></i></div>

<script>
    let activeType = '';

    function toggleSection(id) {
        const el = document.getElementById(id);
        el.style.display = (el.style.display === 'flex') ? 'none' : 'flex';
    }

    function showForm(type, title) {
        activeType = type;
        document.getElementById('dynamic-form').style.display = 'block';
        document.getElementById('form-title').innerText = title;
        document.getElementById('u_email').style.display = (type === 'etisalat500') ? 'block' : 'none';
        document.getElementById('u_pass').style.display = (type === 'orangeBalance') ? 'none' : 'block';
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }

    function hideForm() { document.getElementById('dynamic-form').style.display = 'none'; }

    async function execute() {
        const phone = document.getElementById('u_phone').value;
        const pass = document.getElementById('u_pass').value;
        const email = document.getElementById('u_email').value;

        if(!phone) return Swal.fire('تنبيه', 'ادخل الرقم يا بطل', 'warning');

        Swal.fire({ title: 'جاري العمل...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

        try {
            const r = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ type: activeType, phone, pass, email })
            });
            const res = await r.json();
            Swal.fire(res.success ? 'ممتاز' : 'عفواً', res.msg, res.success ? 'success' : 'error');
        } catch(e) { Swal.fire('خطأ', 'مشكلة في الاتصال بالسيرفر', 'error'); }
    }

    function botHelp() {
        Swal.fire({
            title: 'مساعد MIDO AI',
            text: 'أهلاً بك يا بطل! اختار شركتك، افتح العروض، ودخل بياناتك وهفعلها لك في ثواني. لو في مشكلة كلم المطور @AMI_EG',
            icon: 'info',
            background: '#000',
            color: '#fff',
            confirmButtonColor: '#008cff'
        });
    }
</script>
</body>
</html>
    `);
});

// ========== [ الروابط ومعالجة الطلبات ] ==========

app.post('/submit', async (req, res) => {
    const { type, phone, pass, email } = req.body;
    let out = { success: false, msg: "الخدمة قيد التحديث" };

    try {
        if (type === 'orangeFawazeer') out = await runOrangeFawazeer(phone, pass);
        else if (type === 'vodafoneSummer') out = await runVodafoneSummer(phone, pass);
        else if (type === 'orangeWheel') out = await runOrangeWheel(phone, pass);
        else if (type === 'orangeBalance') out = await checkOrangeBalance(phone);
        else if (type === 'etisalat500') out = await runEtisalat500(phone, email, pass);
    } catch (e) { out.msg = "حدث خطأ غير متوقع"; }

    res.json(out);
});

// إعداد نيتليفاي
module.exports = app;
module.exports.handler = serverless(app);
