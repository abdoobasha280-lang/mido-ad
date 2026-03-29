const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const crypto = require('crypto');
const serverless = require('serverless-http');
const cheerio = require('cheerio'); // لجلب مواقيت الصلاة
const app = express();

app.use(bodyParser.json());

// ========== الإعدادات والصور ==========
const BG_URL = "https://i.postimg.cc/zvQsfRp6/0b2e491cf363fb13fe72f199a1c0cde1.jpg";
const VODAFONE_ICON = "https://i.postimg.cc/SR7ZjRH4/Screenshot-20260213-154727-Google.jpg";
const ORANGE_ICON = "https://i.postimg.cc/MTT2tnyL/IMG-20260219-104918-030.jpg";
const ETISALAT_ICON = "https://i.postimg.cc/63Mrnrkh/Screenshot-20260328-235637-Google.jpg";
const DEVELOPER_CHAT = "https://t.me/AMI_EG";
const TG_CHANNEL = "https://t.me/mido90femeah";

// ========== [ الدوال البرمجية - السكريبتات ] ==========

// 1. جلب مواقيت الصلاة (Scraping)
async function getPrayerTimes() {
    try {
        const { data } = await axios.get("https://www.masrawy.com/islameyat/prayer-times");
        const $ = cheerio.load(data);
        let times = [];
        $('.allTimes .time').each((i, el) => {
            times.push($(el).text().trim());
        });
        const names = ['الفجر', 'الشروق', 'الظهر', 'العصر', 'المغرب', 'العشاء'];
        return { success: true, data: names.map((n, i) => ({ name: n, time: times[i+1] })) };
    } catch (e) { return { success: false, msg: "فشل جلب المواقيت" }; }
}

// 2. فودافون - معرفة الفلكسات
async function getVodaFlex(number, password) {
    try {
        const auth = await axios.post("https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${number}&password=${password}&client_id=ana-vodafone-app`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        const tok = auth.data.access_token;
        const res = await axios.get(`https://web.vodafone.com.eg/services/dxl/usage/usageConsumptionReport?bucket.product.publicIdentifier=${number}&@type=aggregated`,
            { headers: { 'Authorization': `Bearer ${tok}`, 'msisdn': number, 'clientId': 'WebsiteConsumer' } });
        
        let flex = "لا يوجد بيانات";
        res.data.forEach(item => {
            if (item.bucket) item.bucket.forEach(b => {
                if (b.usageType === "limit") b.bucketBalance.forEach(bal => {
                    if (bal["@type"] === "Remaining") flex = bal.remainingValue.amount === 0 ? "أكثر من 30 ألف فلكس" : bal.remainingValue.amount;
                });
            });
        });
        return { success: true, msg: `عدد الفلكسات المتبقية: ${flex}` };
    } catch (e) { return { success: false, msg: "بيانات خاطئة أو فشل اتصال" }; }
}

// 3. أورانج - فوازير (الحل التلقائي)
async function runOrangeFawazeer(number, password) {
    try {
        const login = await axios.post("https://services.orange.eg/SignIn.svc/SignInUser", {
            appVersion: "9.0.1", channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" },
            dialNumber: number, isAndroid: true, lang: "ar", password: password
        });
        const accessTok = login.data.SignInUserResult.AccessToken;
        const genTok = await axios.post("https://services.orange.eg/APIs/Profile/api/BasicAuthentication/Generate", 
            { ChannelName: "MobinilAndMe", Dial: number, Password: password }, { headers: { 'Token': accessTok } });
        const token = genTok.data.Token;
        const qRes = await axios.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Questions", { Dial: number, Token: token });
        
        if (qRes.data.ErrorCode === 1) return { success: false, msg: "شاركت اليوم بالفعل، جرب بكرة" };
        
        const answers = qRes.data.Questions.map(q => ({
            QuestionId: q.Answers[0].QuestionId,
            AnswerId: q.Answers.find(a => a.IsCorrect).Id
        }));

        await axios.post("https://services.orange.eg/APIs/Ramadan2024/api/RamadanOffers/Fawazeer/Submit", { Dial: number, Token: token, Answers: answers });
        return { success: true, msg: "تم حل الفوازير واستلام 250 ميجا ✅" };
    } catch (e) { return { success: false, msg: "خطأ في السكريبت" }; }
}

// ========== [ الواجهة الأمامية - UI ] ==========

app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO_AD | لوحة التحكم</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Orbitron:wght@700;900&display=swap');
        
        :root { --blue: #008cff; --red: #ff003c; --black: #050505; }
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Cairo', sans-serif; background: var(--black) url('${BG_URL}') no-repeat center center fixed;
            background-size: cover; color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh;
        }

        .container { width: 95%; max-width: 480px; text-align: center; backdrop-filter: blur(10px); padding: 20px; }

        h1 { font-family: 'Orbitron', sans-serif; font-size: 3.2rem; margin-bottom: 40px; text-shadow: 0 0 20px var(--blue), 0 0 40px var(--red); letter-spacing: 5px; }

        .view { display: none; animation: slideIn 0.4s ease forwards; }
        .view.active { display: block; }
        @keyframes slideIn { from { opacity:0; transform: translateY(20px); } to { opacity:1; transform: translateY(0); } }

        .btn-neon {
            width: 100%; padding: 22px; margin-bottom: 18px; background: rgba(0,0,0,0.6);
            border: none; border-right: 5px solid var(--blue); color: white;
            font-size: 1.3rem; font-weight: 900; cursor: pointer; display: flex; align-items: center;
            justify-content: space-between; border-radius: 5px 30px 30px 5px; transition: 0.3s;
        }

        .btn-neon:active {
            transform: perspective(500px) rotateX(10deg) rotateY(-10deg) translateY(5px);
            box-shadow: -10px 10px 20px var(--blue); border-color: var(--red);
        }

        .btn-neon i.fa-bolt { color: yellow; text-shadow: 0 0 10px orange; }
        .btn-neon img { width: 45px; height: 45px; border-radius: 50%; border: 2px solid #fff; }

        .offer-card {
            width: 100%; padding: 15px; margin-bottom: 12px; background: rgba(255,255,255,0.05);
            border: 1px solid var(--red); color: white; border-radius: 15px; cursor: pointer; font-weight: bold;
        }

        input {
            width: 100%; padding: 15px; margin-bottom: 10px; background: #000; border: 1px solid #333;
            color: white; border-radius: 12px; text-align: center; font-size: 1.1rem;
        }

        #bot-icon {
            position: fixed; bottom: 30px; left: 30px; width: 65px; height: 65px;
            background: linear-gradient(45deg, var(--blue), var(--red));
            border-radius: 50%; display: flex; justify-content: center; align-items: center;
            font-size: 1.8rem; cursor: pointer; box-shadow: 0 0 20px var(--blue); z-index: 999;
        }

        footer { margin-top: 40px; font-size: 0.8rem; opacity: 0.6; }
        .dev-links a { color: var(--blue); margin: 0 10px; font-size: 1.5rem; }
    </style>
</head>
<body>

<div class="container">
    <h1>MIDO_AD</h1>

    <div id="home" class="view active">
        <button class="btn-neon" onclick="showView('voda')">
            <span><i class="fas fa-bolt"></i> فودافون</span>
            <img src="${VODAFONE_ICON}">
        </button>
        <button class="btn-neon" onclick="showView('orange')" style="border-right-color: #ff6600;">
            <span><i class="fas fa-bolt"></i> أورانج</span>
            <img src="${ORANGE_ICON}">
        </button>
        <button class="btn-neon" onclick="showView('etisalat')" style="border-right-color: #719c30;">
            <span><i class="fas fa-bolt"></i> اتصالات</span>
            <img src="${ETISALAT_ICON}">
        </button>
        <button class="btn-neon" onclick="loadPrayers()" style="border-right-color: #fff;">
            <span><i class="fas fa-mosque"></i> مواقيت الصلاة</span>
            <i class="fas fa-clock" style="font-size: 2rem;"></i>
        </button>

        <div class="dev-links">
            <a href="${TG_CHANNEL}"><i class="fab fa-telegram"></i></a>
            <a href="${DEVELOPER_CHAT}"><i class="fas fa-user-shield"></i></a>
        </div>
    </div>

    <div id="voda" class="view">
        <button onclick="showView('home')" style="color:#888; background:none; border:none; margin-bottom:20px; cursor:pointer;">🏠 العودة</button>
        <button class="offer-card" onclick="openForm('vodaFlex', 'معرفة نسبة الفلكسات')">معرفة الرصيد (فلكسات)</button>
        <button class="offer-card" onclick="openForm('voda500', 'هدية 500 ميجا')">تفعيل 500 ميجا</button>
        <button class="offer-card" onclick="openForm('vodaDiscount', 'خصم 50% على فليكس')">خصم 50% (300/250)</button>
    </div>

    <div id="orange" class="view">
        <button onclick="showView('home')" style="color:#888; background:none; border:none; margin-bottom:20px; cursor:pointer;">🏠 العودة</button>
        <button class="offer-card" onclick="openForm('orangeFawazeer', 'حل فوازير رمضان')">حل الفوازير (250 ميجا لايف)</button>
        <button class="offer-card" onclick="openForm('orange500', 'هدية 500 ميجا')">تفعيل هدية 500 ميجا</button>
        <button class="offer-card" onclick="openForm('orangeBalance', 'استعلام الرصيد')">استعلام الرصيد المحدث</button>
    </div>

    <div id="etisalat" class="view">
        <button onclick="showView('home')" style="color:#888; background:none; border:none; margin-bottom:20px; cursor:pointer;">🏠 العودة</button>
        <button class="offer-card" onclick="openForm('etisalatSocial', '500M سوشيال')">500 ميجا سوشيال</button>
        <button class="offer-card" onclick="openForm('etisalatStream', '500M استريمينج')">500 ميجا استريمينج</button>
    </div>

    <div id="form-box" class="view">
        <h2 id="ftitle" style="color:var(--blue); margin-bottom:20px;"></h2>
        <input type="tel" id="u_phone" placeholder="رقم الموبايل">
        <input type="password" id="u_pass" placeholder="كلمة المرور">
        <input type="email" id="u_email" placeholder="البريد (لاتصالات فقط)" style="display:none;">
        <button class="offer-card" style="background:var(--blue); border:none;" onclick="submitData()">تفعيل الآن ⚡</button>
        <button onclick="showView('home')" style="color:var(--red); background:none; border:none; margin-top:15px; cursor:pointer;">إلغاء</button>
    </div>

    <footer>حقوق MIDO_AD محفوظة © 2026 - تطوير @AMI_EG</footer>
</div>

<div id="bot-icon" onclick="startChat()"><i class="fas fa-robot"></i></div>

<script>
    let currentTask = '';
    function showView(id) {
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById(id).classList.add('active');
    }

    function openForm(type, title) {
        currentTask = type;
        document.getElementById('ftitle').innerText = title;
        document.getElementById('u_email').style.display = type.includes('etisalat') ? 'block' : 'none';
        document.getElementById('u_pass').style.display = type === 'orangeBalance' ? 'none' : 'block';
        showView('form-box');
    }

    async function loadPrayers() {
        Swal.fire({ title: 'جاري جلب المواقيت...', didOpen: () => Swal.showLoading() });
        const res = await fetch('/prayers');
        const data = await res.json();
        if(data.success) {
            let html = '<div style="text-align:right; font-weight:bold;">';
            data.data.forEach(p => html += \`<p style="margin:10px 0; border-bottom:1px solid #333; padding-bottom:5px;">\${p.name}: <span style="color:var(--blue)">\${p.time}</span></p>\`);
            html += '</div>';
            Swal.fire({ title: 'مواقيت الصلاة اليوم', html: html, icon: 'info' });
        }
    }

    async function submitData() {
        const phone = document.getElementById('u_phone').value;
        const pass = document.getElementById('u_pass').value;
        const email = document.getElementById('u_email').value;
        if(!phone) return Swal.fire('خطأ', 'دخل الرقم يا بطل', 'error');

        Swal.fire({ title: 'جاري التنفيذ...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

        const r = await fetch('/api', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ type: currentTask, phone, pass, email })
        });
        const res = await r.json();
        Swal.fire(res.success ? 'تم بنجاح' : 'تعذر التنفيذ', res.msg, res.success ? 'success' : 'error');
    }

    async function startChat() {
        const { value: text } = await Swal.fire({
            title: 'مساعد MIDO الذكي', input: 'text',
            inputPlaceholder: 'اسأل عن عروض، مواقيت الصلاة، أو المطور...',
            background: '#000', color: '#fff', confirmButtonText: 'إرسال'
        });
        if(text) {
            let reply = "مش فاهمك يا غالي، جرب تسأل عن (عروض، صلاة، مطور)";
            const t = text.toLowerCase();
            if(t.includes('صلاة')) reply = "تقدر تضغط على زرار مواقيت الصلاة في الرئيسية وهنجيبلك المواعيد لايف.";
            else if(t.includes('مطور')) reply = "المطور هو @AMI_EG، تقدر تتواصل معاه من الروابط تحت.";
            else if(t.includes('عروض')) reply = "عندنا عروض 500 ميجا وفوازير أورانج وخصومات فودافون!";
            Swal.fire({ title: 'MIDO AI:', text: reply, background: '#000', color: '#008cff' });
        }
    }
</script>
</body>
</html>
    `);
});

// ========== [ الروابط والخلفية ] ==========

app.get('/prayers', async (req, res) => {
    const data = await getPrayerTimes();
    res.json(data);
});

app.post('/api', async (req, res) => {
    const { type, phone, pass, email } = req.body;
    let out = { success: false, msg: "هذه الخدمة تحت الصيانة حالياً" };

    try {
        if (type === 'vodaFlex') out = await getVodaFlex(phone, pass);
        else if (type === 'orangeFawazeer') out = await runOrangeFawazeer(phone, pass);
        // يمكنك إضافة باقي الدوال هنا بنفس المنطق
    } catch (e) { out.msg = "حدث خطأ غير متوقع"; }
    res.json(out);
});

module.exports = app;
module.exports.handler = serverless(app);
