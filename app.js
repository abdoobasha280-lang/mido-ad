const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const crypto = require('crypto');
const serverless = require('serverless-http'); // المكتبة المطلوبة لـ Netlify
const app = express();

app.use(bodyParser.json());

// ========== إعدادات الموقع ==========
const BG_URL = "https://i.postimg.cc/756bfgS0/Screenshot-20260211-182825-Telegram.jpg";
const TG_CHANNEL = "https://t.me/mido90femeah";
const DEVELOPER_USER = "@AMI_EG";

const api = axios.create({
    timeout: 15000,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
});

// ========== دوال الخدمات (Orange, Vodafone, Etisalat, WE) ==========

async function runOrange500(phone, password) {
    try {
        const login = await api.post("https://services.orange.eg/SignIn.svc/SignInUser", {
            appVersion: "9.0.0",
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" },
            dialNumber: phone, isAndroid: true, lang: "ar", password: password
        });
        if (!login.data.SignInUserResult || !login.data.SignInUserResult.UserData) return { success: false, msg: "فشل تسجيل الدخول" };
        const userId = login.data.SignInUserResult.UserData.UserID;
        const tokenRes = await api.post("https://services.orange.eg/GetToken.svc/GenerateToken", {
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" }
        });
        const ctv = tokenRes.data.GenerateTokenResult.Token;
        const htv = crypto.createHash('sha256').update(ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").digest('hex').toUpperCase();
        const redeem = await api.post("https://services.orange.eg/APIs/Promotions/api/CAF/Redeem", {
            Language: "ar", OSVersion: "Android7.0", PromoCode: "رمضان كريم",
            dial: phone, password: password, Channelname: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF"
        }, { headers: { "_ctv": ctv, "_htv": htv, "UserId": userId } });
        if(redeem.data.ErrorDescription === "Success" || redeem.data.ErrorCode === 0) return { success: true, msg: "تم التفعيل بنجاح ✅" };
        return { success: false, msg: redeem.data.ErrorDescription || "العرض غير متاح" };
    } catch (e) { return { success: false, msg: "خطأ في الاتصال بالخدمة" }; }
}

async function runOrangeWheel(phone, password) {
    try {
        const tokenRes = await api.post("https://services.orange.eg/GetToken.svc/GenerateToken", {
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" }
        });
        const ctv = tokenRes.data.GenerateTokenResult.Token;
        const htv = crypto.createHash('sha256').update(ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk").digest('hex').toUpperCase();
        const headers = { 'User-Agent': "okhttp/3.14.9", '_ctv': ctv, '_htv': htv, 'Content-Type': "application/json" };
        const spinRes = await api.post("https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin", {
            ChannelName: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", Dial: phone, Language: "en", Password: password, ServiceClassId: "1033"
        }, { headers });
        if (!spinRes.data.OfferDetails) return { success: false, msg: "انتهت محاولاتك أو غير مؤهل" };
        const { OfferId, OfferName } = spinRes.data.OfferDetails;
        await api.post("https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill", {
            CategoryId: spinRes.data.SecondryButtonDetails?.CategoryId || "0", 
            ChannelName: "MobinilAndMe", ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", Dial: phone, Language: "en", OfferId, Password: password, ServiceClassId: "1033"
        }, { headers });
        return { success: true, msg: `مبروك! كسبت: ${OfferName} ✅` };
    } catch (e) { return { success: false, msg: "خطأ في الخادم" }; }
}

async function checkOrangeBalance(phone) {
    try {
        const res = await api.post("https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers", {
            SelectedUserDial: null, IsForAnotherRecipient: true, RecipientDial: phone, Dial: phone
        });
        if (res.data.ErrorCode === 0) return { success: true, msg: `الرصيد: ${res.data.CreditBalance} ${res.data.Currency}` };
        return { success: false, msg: "تعذر جلب الرصيد" };
    } catch (e) { return { success: false, msg: "خطأ في الاتصال" }; }
}

async function runVodafoneSummer(phone, password) {
    try {
        const auth = await api.post("https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${phone}&password=${password}&client_secret=95fd95fb-7489-4958&client_id=ana-vodafone-app`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        const res = await api.post("https://web.vodafone.com.eg/services/dxl/promo/promotion", {
            "@type": "Promo", "channel": {"id": "5"}, "context": {"type": "massSummerPromo25"},
            "pattern": [{ "characteristics": [{ "name": "numberOfFaces", "value": 0 }, { "name": "giftId", "value": "18" }] }]
        }, { headers: { 'Authorization': `Bearer ${auth.data.access_token}`, 'msisdn': phone, 'clientId': "WebsiteConsumer" } });
        return { success: true, msg: "تم إضافة هدية فودافون ✅" };
    } catch (e) { return { success: false, msg: "العرض غير متاح أو بيانات خاطئة" }; }
}

async function runVodafoneDiscount(phone, password) {
    try {
        const auth = await api.post("https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${phone}&password=${password}&client_secret=95fd95fb-7489-4958&client_id=ana-vodafone-app`,
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
        const res = await api.post("https://mobile.vodafone.com.eg/services/dxl/pom/productOrder", {
            channel: { name: "MobileApp" }, orderItem: [{ action: "add", id: "Flex_2021_523", "@type": "Access fees Discount",
            product: { relatedParty: [{ id: phone, role: "Subscriber" }] } }]
        }, { headers: { 'Authorization': `Bearer ${auth.data.access_token}`, 'msisdn': phone } });
        return { success: true, msg: "تم تفعيل خصم 50% ✅" };
    } catch (e) { return { success: false, msg: "غير مؤهل للخصم" }; }
}

async function runEtisalat500(phone, email, password) {
    try {
        const auth = Buffer.from(`${email}:${password}`).toString('base64');
        const msisdn = phone.startsWith('0') ? phone.substring(1) : phone;
        const payload = `<submitOrderRequest><msisdn>${msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName></submitOrderRequest>`;
        const res = await api.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", payload, 
            { headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'text/xml', 'applicationName': 'MAB' } });
        if (res.data.includes("Success")) return { success: true, msg: "تم تفعيل اتصالات سوشيال ✅" };
        return { success: false, msg: "فشل التفعيل" };
    } catch (e) { return { success: false, msg: "بيانات خاطئة" }; }
}

async function runEtisalatStreaming(phone, email, password) {
    try {
        const auth = Buffer.from(`${email}:${password}`).toString('base64');
        const msisdn = phone.startsWith('0') ? phone.substring(1) : phone;
        const payload = `<submitOrderRequest><msisdn>${msisdn}</msisdn><operation>REDEEM</operation><productName>DOWNLOAD_GIFT_2_STREAMING_UNITS</productName></submitOrderRequest>`;
        const res = await api.post("https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", payload, 
            { headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'text/xml', 'applicationName': 'MAB' } });
        if (res.data.includes("Success")) return { success: true, msg: "تم تفعيل اتصالات ستريمنج ✅" };
        return { success: false, msg: "فشل التفعيل" };
    } catch (e) { return { success: false, msg: "بيانات خاطئة" }; }
}

async function getWEUsage(phone, password) {
    try {
        const login = await api.post("https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate", 
            { acctId: phone.startsWith('0') ? phone.substring(1) : phone, password: password, isSelfcare: "Y" });
        const usageRes = await api.post("https://my.te.eg/echannel/service/besapp/base/rest/busiservice/cz/cbs/bb/queryFreeUnit", 
            { subscriberId: login.data.body.subscriber.subscriberId, needQueryPoint: true }, 
            { headers: { 'csrftoken': login.data.body.token } });
        let resText = "📊 استهلاك WE:\n";
        usageRes.data.body.forEach(pkg => resText += `⦿ ${pkg.offerName}: ${pkg.remain}/${pkg.total}\n`);
        return { success: true, msg: resText };
    } catch (e) { return { success: false, msg: "تعذر جلب بيانات WE" }; }
}

// ========== المسارات (Routes) ==========

app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIDO_AD - خدمات رمضان</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        body { font-family: 'Cairo', sans-serif; background: url('${BG_URL}') no-repeat center center fixed; background-size: cover; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 12px; }
        .card { background: rgba(0, 20, 10, 0.7); backdrop-filter: blur(15px); padding: 30px; border-radius: 35px; width: 100%; max-width: 450px; text-align: center; color: white; border: 2px solid rgba(255, 215, 0, 0.4); }
        h1 { color: #ffd700; text-shadow: 0 0 15px #ffd700; }
        input { width: 100%; padding: 14px; margin-bottom: 12px; border-radius: 20px; border: none; text-align: center; }
        .btn { width: 100%; padding: 15px; border-radius: 50px; border: 1.5px solid #ffd700; background: linear-gradient(145deg, #0a4d2e, #1e6b3b); color: white; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-label { font-size: 14px; text-align: right; margin: 15px 5px 5px 0; color: #ffd700; }
        .loading { display: none; color: #ffd700; margin: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div id="home-view">
            <div style="color:#ffd700">🌙 رمضان كريم 🌙</div>
            <h1>MIDO_AD</h1>
            <div class="btn-label">أورانج 500 ميجا</div>
            <button class="btn" onclick="showForm('orange500')">تفعيل</button>
            <div class="btn-label">عجلة أورانج</div>
            <button class="btn" onclick="showForm('orangeWheel')">لف العجلة</button>
            <div class="btn-label">استعلام رصيد أورانج</div>
            <button class="btn" onclick="showForm('orangeBalance')">استعلام</button>
            <div class="btn-label">فودافون هدية الصيف</div>
            <button class="btn" onclick="showForm('vodafoneSummer')">تفعيل</button>
            <div class="btn-label">اتصالات 500 ميجا</div>
            <button class="btn" onclick="showForm('etisalat500')">تفعيل</button>
            <div class="btn-label">استهلاك WE</div>
            <button class="btn" onclick="showForm('weUsage')">استعلام</button>
            <br><br>
            <a href="${TG_CHANNEL}" style="color:gold; font-size:30px;"><i class="fab fa-telegram"></i></a>
        </div>

        <div id="form-view" style="display:none;">
            <h2 id="form-title" style="color:gold"></h2>
            <input type="tel" id="phone" placeholder="رقم الهاتف">
            <input type="email" id="email" placeholder="البريد (لاتصالات فقط)" style="display:none;">
            <input type="password" id="pass" placeholder="كلمة المرور">
            <div class="loading" id="loading">جاري المعالجة...</div>
            <button class="btn" onclick="submitData()">إرسال الطلب</button>
            <button class="btn" style="background:grey" onclick="location.reload()">رجوع</button>
        </div>
    </div>

    <script>
        let currentType = '';
        function showForm(type) {
            currentType = type;
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('form-view').style.display = 'block';
            document.getElementById('form-title').innerText = type.toUpperCase();
            document.getElementById('email').style.display = type.includes('etisalat') ? 'block' : 'none';
            if(type === 'orangeBalance') document.getElementById('pass').style.display = 'none';
        }

        async function submitData() {
            const data = {
                type: currentType,
                phone: document.getElementById('phone').value,
                pass: document.getElementById('pass').value,
                email: document.getElementById('email').value
            };
            document.getElementById('loading').style.display = 'block';
            try {
                const res = await fetch('/.netlify/functions/app/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                Swal.fire(result.success ? 'نجاح' : 'خطأ', result.msg, result.success ? 'success' : 'error');
            } catch(e) { Swal.fire('خطأ', 'تعذر الاتصال بالخادم', 'error'); }
            document.getElementById('loading').style.display = 'none';
        }
    </script>
</body>
</html>
    `);
});

app.post('/submit', async (req, res) => {
    const { type, phone, pass, email } = req.body;
    let result = { success: false, msg: "خدمة غير معروفة" };
    try {
        if (type === 'orange500') result = await runOrange500(phone, pass);
        else if (type === 'orangeWheel') result = await runOrangeWheel(phone, pass);
        else if (type === 'orangeBalance') result = await checkOrangeBalance(phone);
        else if (type === 'vodafoneSummer') result = await runVodafoneSummer(phone, pass);
        else if (type === 'vodafoneDiscount') result = await runVodafoneDiscount(phone, pass);
        else if (type === 'etisalat500') result = await runEtisalat500(phone, email, pass);
        else if (type === 'etisalatStreaming') result = await runEtisalatStreaming(phone, email, pass);
        else if (type === 'weUsage') result = await getWEUsage(phone, pass);
    } catch (e) { result = { success: false, msg: "حدث خطأ داخلي" }; }
    res.json(result);
});

// تصدير الكود لـ Netlify
module.exports.handler = serverless(app);
