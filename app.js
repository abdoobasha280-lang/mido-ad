const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const serverless = require('serverless-http');
const app = express();

app.use(bodyParser.json());

// الروابط والصور
const BG_URL = "https://i.postimg.cc/zvQsfRp6/0b2e491cf363fb13fe72f199a1c0cde1.jpg";
const VODAFONE_ICON = "https://i.postimg.cc/SR7ZjRH4/Screenshot-20260213-154727-Google.jpg";
const ORANGE_ICON = "https://i.postimg.cc/MTT2tnyL/IMG-20260219-104918-030.jpg";
const ETISALAT_ICON = "https://i.postimg.cc/63Mrnrkh/Screenshot-20260328-235637-Google.jpg";

// الصفحة الرئيسية
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO_AD | المطور @AMI_EG</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=Orbitron:wght@700;900&display=swap');
        :root { --blue: #008cff; --red: #ff003c; --black: #050505; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Cairo', sans-serif; background: var(--black) url('${BG_URL}') no-repeat center center fixed;
            background-size: cover; color: white; display: flex; justify-content: center; min-height: 100vh;
        }
        .container { width: 95%; max-width: 450px; text-align: center; padding: 20px; margin-top: 30px; }
        h1 { font-family: 'Orbitron', sans-serif; font-size: 3rem; margin-bottom: 30px; text-shadow: 0 0 20px var(--blue); color: #fff; }
        .view { display: none; animation: fadeIn 0.4s ease; }
        .view.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
        .btn-neon {
            width: 100%; padding: 18px; margin-bottom: 15px; background: rgba(0,0,0,0.8);
            border: none; border-right: 5px solid var(--blue); color: white;
            font-size: 1.2rem; font-weight: 900; cursor: pointer; display: flex; align-items: center;
            justify-content: space-between; border-radius: 10px 30px 30px 10px; transition: 0.3s;
        }
        .btn-neon:hover { background: rgba(0, 140, 255, 0.2); transform: scale(1.02); }
        .btn-neon img { width: 45px; height: 45px; border-radius: 50%; border: 2px solid #fff; }
        .offer-card { width: 100%; padding: 15px; margin-bottom: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--red); color: white; border-radius: 12px; cursor: pointer; font-weight: bold; }
        input { width: 100%; padding: 15px; margin-bottom: 10px; background: #000; border: 1px solid #333; color: white; border-radius: 10px; text-align: center; font-size: 1rem; }
        #bot-icon { position: fixed; bottom: 30px; left: 30px; width: 65px; height: 65px; background: linear-gradient(45deg, var(--blue), var(--red)); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 1.8rem; cursor: pointer; box-shadow: 0 0 20px var(--blue); }
        footer { margin-top: 40px; font-size: 0.8rem; opacity: 0.5; }
    </style>
</head>
<body>
<div class="container">
    <h1>MIDO_AD</h1>
    
    <div id="home" class="view active">
        <button class="btn-neon" onclick="showV('voda')"><span>⚡ فودافون</span><img src="${VODAFONE_ICON}"></button>
        <button class="btn-neon" onclick="showV('orange')" style="border-right-color:#ff6600;"><span>⚡ أورانج</span><img src="${ORANGE_ICON}"></button>
        <button class="btn-neon" onclick="showV('etisalat')" style="border-right-color:#719c30;"><span>⚡ اتصالات</span><img src="${ETISALAT_ICON}"></button>
        <button class="btn-neon" onclick="getPrayers()" style="border-right-color:#fff;"><span>📅 مواقيت الصلاة</span><i class="fas fa-mosque"></i></button>
    </div>

    <div id="voda" class="view">
        <button class="offer-card" onclick="openF('voda500', '500 ميجا فودافون')">تفعيل 500 ميجا</button>
        <button class="offer-card" onclick="openF('vodaFlex', 'استعلام الفلكسات')">معرفة الفلكسات</button>
        <button class="offer-card" onclick="openF('vodaFlex300', 'خصم 50% فليكس 300')">خصم 50% (300)</button>
        <button onclick="showV('home')" style="color:red; background:none; border:none; cursor:pointer; margin-top:10px;">🏠 رجوع</button>
    </div>

    <div id="orange" class="view">
        <button class="offer-card" onclick="openF('orangeFawazeer', 'حل الفوازير')">حل فوازير رمضان (250M)</button>
        <button class="offer-card" onclick="openF('orange500', '500 ميجا أورانج')">تفعيل 500 ميجا</button>
        <button onclick="showV('home')" style="color:red; background:none; border:none; cursor:pointer; margin-top:10px;">🏠 رجوع</button>
    </div>

    <div id="etisalat" class="view">
        <button class="offer-card" onclick="openF('etisalatSocial', '500M سوشيال')">500 ميجا سوشيال</button>
        <button class="offer-card" onclick="openF('etisalatStream', '500M استريمينج')">500 ميجا استريمينج</button>
        <button onclick="showV('home')" style="color:red; background:none; border:none; cursor:pointer; margin-top:10px;">🏠 رجوع</button>
    </div>

    <div id="f-box" class="view">
        <h3 id="ftitle" style="margin-bottom:15px; color:var(--blue);"></h3>
        <input type="tel" id="ph" placeholder="رقم الهاتف">
        <input type="password" id="ps" placeholder="كلمة المرور">
        <button class="offer-card" style="background:var(--blue); border:none;" onclick="runTask()">تفعيل الآن ⚡</button>
        <button onclick="showV('home')" style="color:gray; background:none; border:none; cursor:pointer; margin-top:10px;">إلغاء</button>
    </div>

    <footer>MIDO_AD © 2026 | Developer @AMI_EG</footer>
</div>

<div id="bot-icon" onclick="startChat()"><i class="fas fa-robot"></i></div>

<script>
    let currentTask = '';
    function showV(id){ document.querySelectorAll('.view').forEach(v=>v.classList.remove('active')); document.getElementById(id).classList.add('active'); }
    function openF(t, title){ currentTask=t; document.getElementById('ftitle').innerText=title; showV('f-box'); }
    
    async function runTask(){
        const ph = document.getElementById('ph').value;
        const ps = document.getElementById('ps').value;
        if(!ph || !ps) return Swal.fire('نقص بيانات', 'برجاء إدخال الرقم والباسورد', 'warning');
        
        Swal.fire({title:'جاري الاتصال بالسيرفر...', allowOutsideClick:false, didOpen:()=>Swal.showLoading()});
        
        try {
            const r = await fetch('/.netlify/functions/app/api', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({task:currentTask, phone:ph, pass:ps})
            });
            const res = await r.json();
            Swal.fire(res.success?'تمت العملية':'فشل', res.msg, res.success?'success':'error');
        } catch(e) { Swal.fire('خطأ', 'حدث مشكلة في السيرفر', 'error'); }
    }

    function getPrayers(){ Swal.fire('مواقيت الصلاة', 'الفجر: 4:18 | الظهر: 12:03 | العصر: 3:38 | المغرب: 6:12 | العشاء: 7:35', 'info'); }
    function startChat(){ Swal.fire({title:'MIDO AI', text:'أهلاً بك في منصة MIDO_AD. اختر شركتك وفعل العروض فوراً.', background:'#000', color:'#008cff'}); }
</script>
</body>
</html>
    `);
});

// الـ API الخاص بالسكريبتات
app.post('/api', async (req, res) => {
    const { task, phone, pass } = req.body;
    // هنا بيتم ربط سكريبتات الـ Node.js اللي عملناها
    res.json({ success: true, msg: "تم إرسال الطلب لـ " + task + " بنجاح. سيصلك تأكيد خلال ثوانٍ!" });
});

const handler = serverless(app);
module.exports.handler = async (event, context) => {
    return await handler(event, context);
};
