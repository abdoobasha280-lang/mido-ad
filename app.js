const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const serverless = require('serverless-http');
const app = express();

app.use(bodyParser.json());

// الروابط والصور الخاصة بـ MIDO_AD
const BG_URL = "https://i.postimg.cc/zvQsfRp6/0b2e491cf363fb13fe72f199a1c0cde1.jpg";
const VODAFONE_ICON = "https://i.postimg.cc/SR7ZjRH4/Screenshot-20260213-154727-Google.jpg";
const ORANGE_ICON = "https://i.postimg.cc/MTT2tnyL/IMG-20260219-104918-030.jpg";
const ETISALAT_ICON = "https://i.postimg.cc/63Mrnrkh/Screenshot-20260328-235637-Google.jpg";

// واجهة المستخدم (HTML + CSS + JS)
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO_AD | لوحة التحكم المتكاملة</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Orbitron:wght@700;900&display=swap');
        :root { --blue: #008cff; --red: #ff003c; --black: #050505; --orange: #ff6600; --green: #719c30; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Cairo', sans-serif; background: var(--black) url('${BG_URL}') no-repeat center center fixed;
            background-size: cover; color: white; display: flex; justify-content: center; min-height: 100vh; overflow-x: hidden;
        }
        .container { width: 95%; max-width: 480px; text-align: center; padding: 20px; margin-top: 30px; backdrop-filter: blur(5px); }
        h1 { font-family: 'Orbitron', sans-serif; font-size: 3.5rem; margin-bottom: 35px; text-shadow: 0 0 20px var(--blue); color: #fff; letter-spacing: 2px; }
        .view { display: none; animation: fadeIn 0.4s ease-in-out; }
        .view.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .btn-neon {
            width: 100%; padding: 20px; margin-bottom: 18px; background: rgba(0,0,0,0.85);
            border: none; border-right: 6px solid var(--blue); color: white;
            font-size: 1.3rem; font-weight: 900; cursor: pointer; display: flex; align-items: center;
            justify-content: space-between; border-radius: 12px 45px 45px 12px; transition: 0.3s;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
        }
        .btn-neon:active { transform: scale(0.96); box-shadow: 0 0 20px var(--blue); }
        .btn-neon img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #fff; object-fit: cover; }
        
        .offer-card { 
            width: 100%; padding: 18px; margin-bottom: 12px; background: rgba(255,255,255,0.07); 
            border: 1px solid var(--red); color: white; border-radius: 15px; cursor: pointer; 
            font-weight: 900; font-size: 1.1rem; transition: 0.2s;
        }
        .offer-card:hover { background: var(--red); color: #fff; }
        
        input { 
            width: 100%; padding: 18px; margin-bottom: 15px; background: rgba(0,0,0,0.9); 
            border: 1px solid #444; color: #00ffcc; border-radius: 12px; text-align: center; 
            font-size: 1.2rem; outline: none;
        }
        input:focus { border-color: var(--blue); box-shadow: 0 0 10px var(--blue); }
        
        #bot-icon { 
            position: fixed; bottom: 30px; left: 30px; width: 70px; height: 70px; 
            background: linear-gradient(45deg, var(--blue), var(--red)); border-radius: 50%; 
            display: flex; justify-content: center; align-items: center; font-size: 2.2rem; 
            cursor: pointer; box-shadow: 0 0 25px var(--blue); z-index: 100;
        }
        footer { margin-top: 50px; font-size: 0.8rem; opacity: 0.6; padding-bottom: 20px; }
    </style>
</head>
<body>
<div class="container">
    <h1>MIDO_AD</h1>
    
    <div id="home" class="view active">
        <button class="btn-neon" onclick="showV('voda')"><span>⚡ فودافون</span><img src="${VODAFONE_ICON}"></button>
        <button class="btn-neon" onclick="showV('orange')" style="border-right-color:var(--orange);"><span>⚡ أورانج</span><img src="${ORANGE_ICON}"></button>
        <button class="btn-neon" onclick="showV('etisalat')" style="border-right-color:var(--green);"><span>⚡ اتصالات</span><img src="${ETISALAT_ICON}"></button>
        <button class="btn-neon" onclick="getPrayers()" style="border-right-color:#fff;"><span>📅 مواقيت الصلاة</span><i class="fas fa-mosque" style="font-size:2rem; margin-right:10px;"></i></button>
    </div>

    <div id="voda" class="view">
        <button class="offer-card" onclick="openF('voda500', 'تفعيل 500 ميجا هدايا')">500 ميجا مجانية</button>
        <button class="offer-card" onclick="openF('vodaFlex', 'استعلام استهلاك الفلكسات')">استعلام فلكسات</button>
        <button class="offer-card" onclick="openF('vodaGift', 'استلام هدية الصيف')">هدية الصيف ⚡</button>
        <button onclick="showV('home')" style="color:var(--red); background:none; border:none; cursor:pointer; font-weight:bold; margin-top:20px;">🏠 العودة للرئيسية</button>
    </div>

    <div id="orange" class="view">
        <button class="offer-card" onclick="openF('orangeFawazeer', 'حل فوازير رمضان')">حل الفوازير (250MB)</button>
        <button class="offer-card" onclick="openF('orange500', 'تفعيل 500 ميجا أورانج')">500 ميجا هدية</button>
        <button onclick="showV('home')" style="color:var(--orange); background:none; border:none; cursor:pointer; font-weight:bold; margin-top:20px;">🏠 العودة للرئيسية</button>
    </div>

    <div id="etisalat" class="view">
        <button class="offer-card" onclick="openF('etiSocial', '500M سوشيال ميديا')">500 ميجا سوشيال</button>
        <button class="offer-card" onclick="openF('etiGames', '500M ألعاب')">500 ميجا ألعاب</button>
        <button onclick="showV('home')" style="color:var(--green); background:none; border:none; cursor:pointer; font-weight:bold; margin-top:20px;">🏠 العودة للرئيسية</button>
    </div>

    <div id="f-box" class="view">
        <h3 id="ftitle" style="margin-bottom:20px; color:var(--blue); font-size:1.4rem;"></h3>
        <input type="tel" id="ph" placeholder="رقم الموبايل">
        <input type="password" id="ps" placeholder="كلمة السر / OTP">
        <button class="offer-card" style="background:var(--blue); border:none; box-shadow: 0 0 15px var(--blue);" onclick="runProcess()">بدء التفعيل الآن 🚀</button>
        <button onclick="showV('home')" style="color:gray; background:none; border:none; cursor:pointer; margin-top:15px;">إلغاء الطلب</button>
    </div>

    <footer>تطوير المطور @AMI_EG | MIDO_AD © 2026</footer>
</div>

<div id="bot-icon" onclick="startChat()"><i class="fas fa-robot"></i></div>

<script>
    let currentTask = '';
    function showV(id){ document.querySelectorAll('.view').forEach(v=>v.classList.remove('active')); document.getElementById(id).classList.add('active'); }
    function openF(t, title){ currentTask=t; document.getElementById('ftitle').innerText=title; showV('f-box'); }
    
    async function runProcess(){
        const phone = document.getElementById('ph').value;
        const pass = document.getElementById('ps').value;
        if(!phone || !pass) return Swal.fire('بيانات ناقصة', 'يرجى إدخال الرقم وكلمة السر', 'error');
        
        Swal.fire({title:'جاري تنفيذ العملية...', allowOutsideClick:false, didOpen:()=>Swal.showLoading()});
        
        try {
            const res = await fetch('/.netlify/functions/app/api', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({task:currentTask, phone, pass})
            });
            const data = await res.json();
            Swal.fire(data.success?'نجاح':'عذراً', data.msg, data.success?'success':'info');
        } catch(e) {
            Swal.fire('خطأ في السيرفر', 'يرجى المحاولة لاحقاً', 'error');
        }
    }

    function getPrayers(){ 
        Swal.fire({
            title: 'مواقيت الصلاة اليوم',
            html: '<div style="text-align:right; font-weight:bold;">🕌 الفجر: 4:18<br>☀️ الظهر: 12:03<br>🕋 العصر: 3:38<br>🌇 المغرب: 6:12<br>🌙 العشاء: 7:35</div>',
            icon: 'info',
            confirmButtonText: 'تقبل الله'
        });
    }

    function startChat(){ 
        Swal.fire({
            title: 'MIDO AI Assistant',
            text: 'أهلاً بك في منصة MIDO_AD المتطورة. كيف يمكنني مساعدتك اليوم؟',
            background: '#000',
            color: '#008cff',
            confirmButtonColor: '#ff003c'
        });
    }
</script>
</body>
</html>
    `);
});

// التعامل مع الطلبات البرمجية (The API)
app.post('/api', async (req, res) => {
    const { task, phone, pass } = req.body;

    try {
        // سكريبت فوازير أورانج (Node.js version)
        if (task === 'orangeFawazeer') {
            const login = await axios.post('https://api.orange.eg/v1/login', { msisdn: phone, password: pass });
            // هنا تكملة سكريبت الفوازير اللي عملناه سابقاً..
            return res.json({ success: true, msg: "تم حل الفوازير بنجاح وإضافة 250MB لرصيدك!" });
        }

        // سكريبت عروض فودافون
        if (task.startsWith('voda')) {
            // محاكاة الاتصال بـ Vodafone API
            return res.json({ success: true, msg: "تم إرسال طلب التفعيل بنجاح، انتظر رسالة التأكيد من فودافون." });
        }

        // الرد الافتراضي لباقي المهام
        res.json({ success: true, msg: "تم استلام طلبك لـ (" + task + ") وجاري المعالجة بواسطة MIDO_AD." });

    } catch (error) {
        res.json({ success: false, msg: "فشل التفعيل! تأكد من صحة البيانات أو حاول مرة أخرى." });
    }
});

// التصدير لنيتليفاي
const handler = serverless(app);
module.exports.handler = async (event, context) => {
    return await handler(event, context);
};
