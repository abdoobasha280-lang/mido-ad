const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const crypto = require('crypto');
const app = express();

app.use(bodyParser.json());

// ========== إعدادات الموقع ==========
const BG_URL = "https://i.postimg.cc/756bfgS0/Screenshot-20260211-182825-Telegram.jpg";
const TG_CHANNEL = "https://t.me/mido90femeah";
const DEVELOPER_USER = "@AMI_EG";

// إعداد axios
const api = axios.create({
    timeout: 15000,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
});

// ========== دوال Orange ==========
async function runOrange500(phone, password) {
    try {
        console.log(`تشغيل أورانج 500 للرقم: ${phone}`);
        
        const login = await api.post("https://services.orange.eg/SignIn.svc/SignInUser", {
            appVersion: "9.0.0",
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" },
            dialNumber: phone, 
            isAndroid: true, 
            lang: "ar", 
            password: password
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!login.data.SignInUserResult || !login.data.SignInUserResult.UserData) {
            return { success: false, msg: "فشل تسجيل الدخول" };
        }
        
        const userId = login.data.SignInUserResult.UserData.UserID;
        console.log('تسجيل الدخول ناجح، UserID:', userId);
        
        const tokenRes = await api.post("https://services.orange.eg/GetToken.svc/GenerateToken", {
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" }
        });
        
        const ctv = tokenRes.data.GenerateTokenResult.Token;
        const htv = crypto.createHash('sha256')
            .update(ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk")
            .digest('hex')
            .toUpperCase();
        
        const redeem = await api.post("https://services.orange.eg/APIs/Promotions/api/CAF/Redeem", {
            Language: "ar", 
            OSVersion: "Android7.0", 
            PromoCode: "رمضان كريم",
            dial: phone, 
            password: password, 
            Channelname: "MobinilAndMe", 
            ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF"
        }, { 
            headers: { 
                "_ctv": ctv, 
                "_htv": htv, 
                "UserId": userId,
                'Content-Type': 'application/json'
            } 
        });
        
        console.log('استجابة التفعيل:', redeem.data);
        
        if(redeem.data.ErrorDescription === "Success" || redeem.data.ErrorCode === 0) {
            return { success: true, msg: "تم التفعيل بنجاح ✅" };
        }
        return { success: false, msg: redeem.data.ErrorDescription || "العرض غير متاح" };
    } catch (error) { 
        console.error('خطأ في أورانج 500:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
            return { success: false, msg: "كلمة المرور خاطئة" };
        }
        if (error.code === 'ECONNABORTED') {
            return { success: false, msg: "انتهت مهلة الاتصال" };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

async function runOrangeWheel(phone, password) {
    try {
        console.log(`تشغيل عجلة أورانج للرقم: ${phone}`);
        
        const tokenRes = await api.post("https://services.orange.eg/GetToken.svc/GenerateToken", {
            channel: { ChannelName: "MobinilAndMe", Password: "ig3yh*mk5l42@oj7QAR8yF" }
        });
        
        const ctv = tokenRes.data.GenerateTokenResult.Token;
        const htv = crypto.createHash('sha256')
            .update(ctv + ",{.c][o^uecnlkijh*.iomv:QzCFRcd;drof/zx}w;ls.e85T^#ASwa?=(lk")
            .digest('hex')
            .toUpperCase();
        
        const headers = { 
            'User-Agent': "okhttp/3.14.9", 
            '_ctv': ctv, 
            '_htv': htv, 
            'Content-Type': "application/json" 
        };
        
        const spinRes = await api.post(
            "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Spin",
            {
                ChannelName: "MobinilAndMe", 
                ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", 
                Dial: phone, 
                Language: "en", 
                Password: password, 
                ServiceClassId: "1033"
            }, 
            { headers }
        );
        
        console.log('استجابة عجلة الحظ:', spinRes.data);
        
        if (!spinRes.data.OfferDetails) {
            return { success: false, msg: "انتهت محاولاتك اليومية أو حسابك غير مؤهل" };
        }
        
        const { OfferId, OfferName } = spinRes.data.OfferDetails;
        const CategoryId = spinRes.data.SecondryButtonDetails?.CategoryId || "0";
        
        await api.post(
            "https://services.orange.eg/APIs/Gaming/api/WheelOfFortune/Fulfill",
            {
                CategoryId, 
                ChannelName: "MobinilAndMe", 
                ChannelPassword: "ig3yh*mk5l42@oj7QAR8yF", 
                Dial: phone, 
                Language: "en", 
                OfferId, 
                Password: password, 
                ServiceClassId: "1033"
            }, 
            { headers }
        );
        
        return { success: true, msg: `مبروك! كسبت: ${OfferName} ✅` };
    } catch (error) { 
        console.error('خطأ في عجلة أورانج:', error.response?.data || error.message);
        
        if (error.response?.data?.ErrorDescription) {
            return { success: false, msg: error.response.data.ErrorDescription };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

async function checkOrangeBalance(phone) {
    try {
        console.log(`التحقق من رصيد أورانج للرقم: ${phone}`);
        
        const res = await api.post(
            "https://www.orange.eg/apis/gsm/gsmonlinepayment/api/payment/rechargecheckeligibilityForOthers",
            {
                SelectedUserDial: null, 
                IsForAnotherRecipient: true, 
                RecipientDial: phone, 
                Dial: phone
            }, 
            {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                    'Content-Type': 'application/json', 
                    'lang': 'en',
                    'Accept': 'application/json'
                }
            }
        );
        
        console.log('استجابة الرصيد:', res.data);
        
        if (res.data.ErrorCode === 0) {
            const balance = res.data.CreditBalance || 0;
            const currency = res.data.Currency || "جنيه";
            return { success: true, msg: `الرصيد الحالي: ${balance} ${currency}` };
        }
        
        return { success: false, msg: res.data.ErrorDescription || "لا يمكن معرفة الرصيد" };
    } catch (error) { 
        console.error('خطأ في التحقق من الرصيد:', error.response?.data || error.message);
        
        if (error.response?.data?.ErrorDescription) {
            return { success: false, msg: error.response.data.ErrorDescription };
        }
        
        return { success: false, msg: "حدث خطأ في الاتصال بالخادم" }; 
    }
}

// ========== دوال Vodafone ==========
async function runVodafoneSummer(phone, password) {
    try {
        console.log(`تشغيل فودافون صيف للرقم: ${phone}`);
        
        const authRes = await api.post(
            "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${phone}&password=${password}&client_secret=95fd95fb-7489-4958&client_id=ana-vodafone-app`,
            { 
                headers: { 
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                } 
            }
        );
        
        const token = authRes.data.access_token;
        
        const promoRes = await api.post(
            "https://web.vodafone.com.eg/services/dxl/promo/promotion",
            {
                "@type": "Promo", 
                "channel": {"id": "5"}, 
                "context": {"type": "massSummerPromo25"},
                "pattern": [{ 
                    "characteristics": [
                        { "name": "numberOfFaces", "value": 0 }, 
                        { "name": "giftId", "value": "18" }
                    ] 
                }]
            }, 
            { 
                headers: { 
                    'Authorization': `Bearer ${token}`, 
                    'msisdn': phone, 
                    'Content-Type': "application/json", 
                    'clientId': "WebsiteConsumer", 
                    'channel': "APP_PORTAL"
                } 
            }
        );
        
        console.log('استجابة هدية الصيف:', promoRes.data);
        
        if (promoRes.status === 200) {
            return { success: true, msg: "تم إضافة الهدية بنجاح ✅" };
        }
        
        return { success: false, msg: "العرض غير متاح لحسابك" };
    } catch (error) { 
        console.error('خطأ في فودافون صيف:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
            return { success: false, msg: "كلمة المرور خاطئة" };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

async function runVodafoneDiscount(phone, password) {
    try {
        console.log(`تشغيل خصم فودافون للرقم: ${phone}`);
        
        const authRes = await api.post(
            "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token", 
            `grant_type=password&username=${phone}&password=${password}&client_secret=95fd95fb-7489-4958&client_id=ana-vodafone-app`,
            { 
                headers: { 
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                } 
            }
        );
        
        const token = authRes.data.access_token;
        
        const res = await api.post(
            "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder",
            {
                channel: { name: "MobileApp" },
                orderItem: [{
                    action: "add", 
                    id: "Flex_2021_523", 
                    "@type": "Access fees Discount",
                    itemPrice: [{ 
                        name: "OriginalPrice", 
                        price: { 
                            taxIncludedAmount: { 
                                unit: "LE", 
                                value: "130.0" 
                            } 
                        } 
                    }],
                    product: {
                        characteristic: [
                            { name: "offerRank", value: "1" }, 
                            { name: "TariffID", value: "523" }
                        ],
                        productSpecification: [{ 
                            id: "Retention With Offer", 
                            name: "Category" 
                        }],
                        relatedParty: [{ 
                            id: phone, 
                            name: "MSISDN", 
                            "@referredType": "prepaid", 
                            role: "Subscriber" 
                        }]
                    }, 
                    eCode: 0
                }], 
                "@type": "InterventionTariff"
            }, 
            { 
                headers: { 
                    'Authorization': `Bearer ${token}`, 
                    'Content-Type': 'application/json', 
                    'msisdn': phone,
                    'Accept': 'application/json'
                } 
            }
        );
        
        console.log('استجابة الخصم:', res.data);
        
        if (res.data.reason === "Success With Grace" || res.data.reason === "Success") {
            return { success: true, msg: "تم تفعيل خصم 50% بنجاح ✅" };
        }
        
        return { success: false, msg: res.data.reason || "العرض غير متاح" };
    } catch (error) { 
        console.error('خطأ في خصم فودافون:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
            return { success: false, msg: "كلمة المرور خاطئة" };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

// ========== دوال Etisalat ==========
async function runEtisalat500(phone, email, password) {
    try {
        console.log(`تشغيل اتصالات 500 للرقم: ${phone}`);
        
        const auth = Buffer.from(`${email}:${password}`).toString('base64');
        const msisdn = phone.startsWith('0') ? phone.substring(1) : phone;
        
        const payload = `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
            <submitOrderRequest>
                <mabOperation></mabOperation>
                <msisdn>${msisdn}</msisdn>
                <operation>REDEEM</operation>
                <productName>DOWNLOAD_GIFT_1_SOCIAL_UNITS</productName>
            </submitOrderRequest>`;
        
        const res = await api.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", 
            payload, 
            {
                headers: { 
                    'Authorization': `Basic ${auth}`, 
                    'Content-Type': 'text/xml', 
                    'applicationName': 'MAB',
                    'Accept': 'application/xml'
                }
            }
        );
        
        console.log('استجابة اتصالات 500:', res.data);
        
        if (res.data.includes("success") || res.data.includes("true") || res.data.includes("Success")) {
            return { success: true, msg: "تم التفعيل بنجاح ✅" };
        }
        
        if (res.data.includes("error") || res.data.includes("Error")) {
            return { success: false, msg: "فشل التفعيل - بيانات الدخول غير صحيحة" };
        }
        
        return { success: false, msg: "العرض غير متاح لحسابك" };
    } catch (error) { 
        console.error('خطأ في اتصالات 500:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
            return { success: false, msg: "البريد الإلكتروني أو كلمة المرور خاطئة" };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

async function runEtisalatStreaming(phone, email, password) {
    try {
        console.log(`تشغيل اتصالات ستريمنج للرقم: ${phone}`);
        
        const auth = Buffer.from(`${email}:${password}`).toString('base64');
        const msisdn = phone.startsWith('0') ? phone.substring(1) : phone;
        
        const payload = `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
            <submitOrderRequest>
                <mabOperation></mabOperation>
                <msisdn>${msisdn}</msisdn>
                <operation>REDEEM</operation>
                <productName>DOWNLOAD_GIFT_2_STREAMING_UNITS</productName>
            </submitOrderRequest>`;
        
        const res = await api.post(
            "https://mab.etisalat.com.eg:11003/Saytar/rest/servicemanagement/submitOrderV2", 
            payload, 
            {
                headers: { 
                    'Authorization': `Basic ${auth}`, 
                    'Content-Type': 'text/xml', 
                    'applicationName': 'MAB',
                    'Accept': 'application/xml'
                }
            }
        );
        
        console.log('استجابة اتصالات ستريمنج:', res.data);
        
        if (res.data.includes("success") || res.data.includes("true") || res.data.includes("Success")) {
            return { success: true, msg: "تم التفعيل بنجاح ✅" };
        }
        
        if (res.data.includes("error") || res.data.includes("Error")) {
            return { success: false, msg: "فشل التفعيل - بيانات الدخول غير صحيحة" };
        }
        
        return { success: false, msg: "العرض غير متاح لحسابك" };
    } catch (error) { 
        console.error('خطأ في اتصالات ستريمنج:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
            return { success: false, msg: "البريد الإلكتروني أو كلمة المرور خاطئة" };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

// ========== دوال WE ==========
async function getWEUsage(phone, password) {
    try {
        console.log(`جلب استهلاك WE للرقم: ${phone}`);
        
        const loginRes = await api.post(
            "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/v1/auth/userAuthenticate", 
            {
                acctId: phone.startsWith('0') ? phone.substring(1) : phone,
                password: password, 
                appLocale: "en-US", 
                isSelfcare: "Y", 
                isMobile: "N", 
                recaptchaToken: ""
            }, 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }
        );
        
        if (!loginRes.data.body || !loginRes.data.body.token) {
            return { success: false, msg: "فشل تسجيل الدخول" };
        }
        
        const token = loginRes.data.body.token;
        
        const usageRes = await api.post(
            "https://my.te.eg/echannel/service/besapp/base/rest/busiservice/cz/cbs/bb/queryFreeUnit", 
            {
                subscriberId: loginRes.data.body.subscriber.subscriberId, 
                needQueryPoint: true
            }, 
            { 
                headers: { 
                    'csrftoken': token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                } 
            }
        );
        
        console.log('استجابة استهلاك WE:', usageRes.data);
        
        if (!usageRes.data.body || !Array.isArray(usageRes.data.body)) {
            return { success: false, msg: "لا توجد بيانات استهلاك متاحة" };
        }
        
        let result = "📊 معلومات استهلاك WE:\n\n";
        usageRes.data.body.forEach((pkg, index) => {
            result += `⦿ ${pkg.offerName || 'باقة غير معروفة'}:\n`;
            result += `   المتبقي: ${pkg.remain || 0}\n`;
            result += `   الإجمالي: ${pkg.total || 0}\n`;
            if (index < usageRes.data.body.length - 1) result += "\n";
        });
        
        return { success: true, msg: result };
    } catch (error) { 
        console.error('خطأ في استهلاك WE:', error.response?.data || error.message);
        
        if (error.response?.status === 401) {
            return { success: false, msg: "كلمة المرور خاطئة" };
        }
        
        if (error.response?.data?.message) {
            return { success: false, msg: error.response.data.message };
        }
        
        return { success: false, msg: "حدث خطأ في الخادم" }; 
    }
}

// ========== CORS Middleware ==========
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

// ========== Health Check ==========
app.get('/health', (req, res) => {
    res.json({ 
        status: 'online', 
        services: [
            'Orange 500MB',
            'Orange Wheel', 
            'Orange Balance',
            'Vodafone Summer',
            'Vodafone Discount',
            'Etisalat 500MB Social',
            'Etisalat 500MB Streaming',
            'WE Usage'
        ]
    });
});

// ========== Home Page - تصميم متجاوب بالكامل ==========
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.5, user-scalable=yes">
    <title>MIDO_AD - خدمات رمضان</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        
        /* reset وضبط شامل */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Cairo', sans-serif;
            background: url('${BG_URL}') no-repeat center center fixed;
            background-size: cover;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            position: relative;
            overflow-x: hidden;
        }

        /* الهلال المتحرك - متجاوب */
        .moving-crescent {
            position: fixed;
            top: 5%;
            right: 5%;
            color: rgba(255, 215, 0, 0.6);
            font-size: clamp(3rem, 15vw, 7rem);
            text-shadow: 0 0 30px rgba(255, 223, 0, 0.8);
            animation: floatCrescent 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 5;
        }

        @keyframes floatCrescent {
            0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.6; }
            50% { transform: translateY(-25px) rotate(10deg); opacity: 1; }
        }

        /* البطاقة الرئيسية - مرنة 100% */
        .card {
            background: rgba(0, 20, 10, 0.7);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            padding: clamp(20px, 5vw, 35px);
            border-radius: 35px;
            width: 100%;
            max-width: 450px;
            margin: 0 auto;
            text-align: center;
            color: white;
            border: 2px solid rgba(255, 215, 0, 0.4);
            box-shadow: 0 15px 40px rgba(0,0,0,0.5);
            position: relative;
            z-index: 10;
            transition: all 0.3s;
        }

        /* تحسينات للشاشات الصغيرة جدًا */
        @media (max-width: 380px) {
            .card {
                padding: 18px;
                border-radius: 25px;
            }
        }

        .ramadan-greeting {
            color: #ffd700;
            font-size: clamp(18px, 6vw, 24px);
            font-weight: 900;
            margin-bottom: 8px;
            text-shadow: 0 0 10px rgba(255,215,0,0.6);
            letter-spacing: 1px;
        }

        h1 {
            margin: 0 0 20px 0;
            font-size: clamp(28px, 8vw, 40px);
            color: #fff;
            text-shadow: 0 0 15px #ffd700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        h1 i {
            color: #ffd700;
            font-size: clamp(24px, 7vw, 35px);
        }

        .btn-label {
            font-size: clamp(13px, 4vw, 15px);
            text-align: right;
            margin: 20px 5px 8px 0;
            color: #ffd700;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px dashed rgba(255,215,0,0.3);
            padding-bottom: 5px;
        }

        .btn-label i {
            font-size: clamp(14px, 4.5vw, 18px);
            color: #ffaa00;
        }

        /* حقول الإدخال - متجاوبة */
        input {
            width: 100%;
            padding: clamp(12px, 4vw, 16px);
            margin-bottom: 12px;
            border-radius: 20px;
            border: none;
            background: rgba(255, 255, 255, 0.96);
            color: #222;
            text-align: center;
            font-family: 'Cairo';
            font-size: clamp(14px, 4vw, 16px);
            border: 2px solid transparent;
            transition: all 0.3s;
        }

        input:focus {
            outline: none;
            border: 2px solid #ffd700;
            box-shadow: 0 0 20px rgba(255,215,0,0.6);
            background: #fff;
        }

        /* الأزرار - متجاوبة وثابتة */
        .btn {
            width: 100%;
            padding: clamp(14px, 4.5vw, 18px);
            border-radius: 50px;
            border: none;
            background: linear-gradient(145deg, #0a4d2e, #1e6b3b);
            color: white;
            font-weight: bold;
            cursor: pointer;
            font-size: clamp(15px, 4.5vw, 18px);
            margin-top: 10px;
            transition: all 0.3s;
            border: 1.5px solid #ffd700;
            box-shadow: 0 6px 15px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .btn i {
            color: #ffd700;
            font-size: clamp(16px, 5vw, 20px);
        }

        .btn:hover {
            transform: scale(1.02);
            background: linear-gradient(145deg, #1e6b3b, #0a4d2e);
            box-shadow: 0 0 25px rgba(255,215,0,0.7);
            border-color: #fff;
        }

        .btn:active {
            transform: scale(0.98);
        }

        /* رابط العودة */
        .back-link {
            font-size: clamp(14px, 4vw, 16px);
            margin-top: 22px;
            cursor: pointer;
            display: inline-block;
            color: #ffd700;
            text-decoration: none;
            transition: 0.3s;
            padding: 5px 15px;
            border-radius: 30px;
            background: rgba(0,0,0,0.2);
        }

        .back-link i {
            margin-left: 6px;
        }

        .back-link:hover {
            color: #fff;
            background: rgba(255,215,0,0.2);
            text-shadow: 0 0 8px gold;
        }

        /* التحميل */
        .loading {
            display: none;
            color: #ffd700;
            margin: 12px 0;
            font-size: clamp(14px, 4vw, 16px);
            font-weight: bold;
        }

        .form-container {
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* رابط التليجرام */
        .telegram-link {
            color: #ffd700;
            font-size: clamp(36px, 10vw, 48px);
            margin-top: 25px;
            display: inline-block;
            transition: 0.3s;
        }

        .telegram-link:hover {
            transform: scale(1.1);
            color: #fff;
        }

        /* المطور */
        .developer {
            font-size: clamp(12px, 3.5vw, 14px);
            margin-top: 18px;
            color: rgba(255,255,255,0.8);
            border-top: 1px dashed rgba(255,215,0,0.5);
            padding-top: 18px;
            display: flex;
            justify-content: center;
            gap: 5px;
            flex-wrap: wrap;
        }

        /* تحسينات للشاشات الأفقية */
        @media (min-width: 768px) {
            .card {
                max-width: 500px;
            }
        }

        @media (min-width: 1024px) {
            .card {
                max-width: 550px;
            }
        }

        /* منع تجاوز المحتوى */
        img {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <!-- هلال متحرك - يتناسب مع جميع الشاشات -->
    <div class="moving-crescent">
        <i class="fas fa-moon"></i>
    </div>

    <div class="card">
        <div id="home-view">
            <div class="ramadan-greeting">🌙 رمضان كريم 🌙</div>
            <h1>
                <i class="fas fa-moon"></i>
                MIDO_AD
                <i class="fas fa-star"></i>
            </h1>
            
            <div class="btn-label"><i class="fas fa-mobile-alt"></i> ORANGE 500M</div>
            <button class="btn" onclick="showForm('orange500')"><i class="fas fa-gift"></i> تفعيل</button>
            
            <div class="btn-label"><i class="fas fa-cog"></i> عجلة ORANGE</div>
            <button class="btn" onclick="showForm('orangeWheel')"><i class="fas fa-sync-alt"></i> لف العجلة</button>
            
            <div class="btn-label"><i class="fas fa-balance-scale"></i> معرفة رصيد ORANGE</div>
            <button class="btn" onclick="showForm('orangeBalance')"><i class="fas fa-search"></i> استعلام</button>
            
            <div class="btn-label"><i class="fas fa-sun"></i> VODAFONE 1000M</div>
            <button class="btn" onclick="showForm('vodafoneSummer')"><i class="fas fa-umbrella-beach"></i> هدية الصيف</button>
            
            <div class="btn-label"><i class="fas fa-percent"></i> خصم 50% VODAFONE</div>
            <button class="btn" onclick="showForm('vodafoneDiscount')"><i class="fas fa-tags"></i> تفعيل خصم</button>
            
            <div class="btn-label"><i class="fas fa-users"></i> ETISALAT 500M سوشيال</div>
            <button class="btn" onclick="showForm('etisalat500')"><i class="fas fa-thumbs-up"></i> تفعيل</button>
            
            <div class="btn-label"><i class="fas fa-video"></i> ETISALAT 500M ستريمنج</div>
            <button class="btn" onclick="showForm('etisalatStreaming')"><i class="fas fa-play"></i> تفعيل</button>
            
            <div class="btn-label"><i class="fas fa-chart-line"></i> معرفة استهلاك WE</div>
            <button class="btn" onclick="showForm('weUsage')"><i class="fas fa-file-alt"></i> استعلام</button>
            
            <a href="${TG_CHANNEL}" target="_blank" class="telegram-link">
                <i class="fab fa-telegram"></i>
            </a>
            <div class="developer">
                <i class="fas fa-code"></i> المطور: ${DEVELOPER_USER} 
                <span style="color:#ffd700;">🌙 رمضان 2026</span>
            </div>
        </div>
        
        <!-- نماذج الإدخال - بدون أي تغيير في الوظائف -->
        <div id="orange500-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-gift"></i> أورانج 500 ميجا</h2>
            <input type="tel" id="orange500-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="password" id="orange500-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="orange500-loading">جاري التفعيل...</div>
            <button class="btn" onclick="submitReq('orange500')"><i class="fas fa-check-circle"></i> تفعيل</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="orangeWheel-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-sync-alt"></i> عجلة أورانج</h2>
            <input type="tel" id="orangeWheel-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="password" id="orangeWheel-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="orangeWheel-loading">جاري التشغيل...</div>
            <button class="btn" onclick="submitReq('orangeWheel')"><i class="fas fa-spinner"></i> لف العجلة</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="orangeBalance-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-balance-scale"></i> معرفة رصيد أورانج</h2>
            <input type="tel" id="orangeBalance-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <div class="loading" id="orangeBalance-loading">جاري الاستعلام...</div>
            <button class="btn" onclick="submitReq('orangeBalance')"><i class="fas fa-search"></i> استعلام</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="vodafoneSummer-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-umbrella-beach"></i> فودافون هدية الصيف</h2>
            <input type="tel" id="vodafoneSummer-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="password" id="vodafoneSummer-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="vodafoneSummer-loading">جاري التفعيل...</div>
            <button class="btn" onclick="submitReq('vodafoneSummer')"><i class="fas fa-check"></i> تفعيل</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="vodafoneDiscount-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-percent"></i> خصم 50% فودافون</h2>
            <input type="tel" id="vodafoneDiscount-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="password" id="vodafoneDiscount-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="vodafoneDiscount-loading">جاري التفعيل...</div>
            <button class="btn" onclick="submitReq('vodafoneDiscount')"><i class="fas fa-tag"></i> تفعيل</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="etisalat500-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-users"></i> اتصالات 500 ميجا سوشيال</h2>
            <input type="tel" id="etisalat500-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="email" id="etisalat500-email" placeholder="البريد الإلكتروني" required>
            <input type="password" id="etisalat500-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="etisalat500-loading">جاري التفعيل...</div>
            <button class="btn" onclick="submitReq('etisalat500')"><i class="fas fa-check"></i> تفعيل</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="etisalatStreaming-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-video"></i> اتصالات 500 ميجا ستريمنج</h2>
            <input type="tel" id="etisalatStreaming-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="email" id="etisalatStreaming-email" placeholder="البريد الإلكتروني" required>
            <input type="password" id="etisalatStreaming-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="etisalatStreaming-loading">جاري التفعيل...</div>
            <button class="btn" onclick="submitReq('etisalatStreaming')"><i class="fas fa-play"></i> تفعيل</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
        
        <div id="weUsage-view" class="form-container" style="display:none;">
            <h2 style="color:#ffd700; font-size:clamp(20px,6vw,28px); margin-bottom:15px;"><i class="fas fa-chart-line"></i> معرفة استهلاك WE</h2>
            <input type="tel" id="weUsage-phone" placeholder="رقم الهاتف (01XXXXXXXXX)" pattern="^01[0-9]{9}$" required>
            <input type="password" id="weUsage-pass" placeholder="كلمة المرور" required>
            <div class="loading" id="weUsage-loading">جاري الاستعلام...</div>
            <button class="btn" onclick="submitReq('weUsage')"><i class="fas fa-file-signature"></i> استعلام</button>
            <a class="back-link" onclick="location.reload()"><i class="fas fa-arrow-right"></i> رجوع</a>
        </div>
    </div>

    <script>
        // ========== نفس دوال التحكم الأصلية بدون تغيير ==========
        function showForm(formName) {
            const allForms = ['home', 'orange500', 'orangeWheel', 'orangeBalance', 'vodafoneSummer', 
                            'vodafoneDiscount', 'etisalat500', 'etisalatStreaming', 'weUsage'];
            
            allForms.forEach(form => {
                const el = document.getElementById(form + '-view');
                if (el) el.style.display = 'none';
            });
            
            document.getElementById(formName + '-view').style.display = 'block';
        }
        
        async function submitReq(type) {
            let data = { type };
            const phoneInput = document.getElementById(type + '-phone');
            const passInput = document.getElementById(type + '-pass');
            const emailInput = document.getElementById(type + '-email');
            
            if (!phoneInput) {
                showError('عنصر إدخال الهاتف غير موجود');
                return;
            }
            
            data.phone = phoneInput.value.trim();
            
            if (type !== 'orangeBalance') {
                if (!passInput) {
                    showError('عنصر إدخال كلمة المرور غير موجود');
                    return;
                }
                data.pass = passInput.value.trim();
            }
            
            if (type === 'etisalat500' || type === 'etisalatStreaming') {
                if (!emailInput) {
                    showError('عنصر إدخال البريد الإلكتروني غير موجود');
                    return;
                }
                data.email = emailInput.value.trim();
            }
            
            if (!/^01[0-9]{9}$/.test(data.phone)) {
                Swal.fire('خطأ', 'رقم الهاتف يجب أن يبدأ بـ 01 ويتكون من 11 رقماً', 'error');
                return;
            }
            
            if (type !== 'orangeBalance' && !data.pass) {
                Swal.fire('خطأ', 'أدخل كلمة المرور', 'error');
                return;
            }
            
            if ((type === 'etisalat500' || type === 'etisalatStreaming') && !isValidEmail(data.email)) {
                Swal.fire('خطأ', 'أدخل بريد إلكتروني صحيح', 'error');
                return;
            }
            
            const loadingEl = document.getElementById(type + '-loading');
            if (loadingEl) loadingEl.style.display = 'block';
            
            const btn = document.querySelector('#' + type + '-view .btn');
            if (btn) btn.disabled = true;
            
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (loadingEl) loadingEl.style.display = 'none';
                if (btn) btn.disabled = false;
                
                if (result.success) {
                    Swal.fire({
                        title: 'نجاح',
                        text: result.msg,
                        icon: 'success',
                        confirmButtonText: 'حسناً',
                        background: '#1a2a1a',
                        color: '#fff',
                        confirmButtonColor: '#ffd700',
                        width: '90%',
                        padding: '20px'
                    });
                } else {
                    Swal.fire({
                        title: 'خطأ',
                        text: result.msg,
                        icon: 'error',
                        confirmButtonText: 'حسناً',
                        background: '#1a2a1a',
                        color: '#fff',
                        confirmButtonColor: '#ffd700',
                        width: '90%',
                        padding: '20px'
                    });
                }
            } catch (error) {
                console.error('خطأ في الاتصال:', error);
                
                if (loadingEl) loadingEl.style.display = 'none';
                if (btn) btn.disabled = false;
                
                Swal.fire({
                    title: 'خطأ في الاتصال',
                    text: 'تعذر الاتصال بالخادم. يرجى المحاولة مرة أخرى.',
                    icon: 'error',
                    confirmButtonText: 'حسناً',
                    background: '#1a2a1a',
                    color: '#fff',
                    confirmButtonColor: '#ffd700',
                    width: '90%',
                    padding: '20px'
                });
            }
        }
        
        function isValidEmail(email) {
            const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            return re.test(email);
        }
        
        function showError(message) {
            Swal.fire({
                title: 'خطأ',
                text: message,
                icon: 'error',
                confirmButtonText: 'حسناً',
                background: '#1a2a1a',
                color: '#fff',
                confirmButtonColor: '#ffd700',
                width: '90%',
                padding: '20px'
            });
        }
        
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const activeView = document.querySelector('.form-container[style="display:block;"]');
                if (activeView) {
                    const formId = activeView.id.replace('-view', '');
                    if (formId !== 'home') {
                        submitReq(formId);
                    }
                }
            }
        });
    </script>
</body>
</html>
    `);
});

// ========== معالجة الطلبات ==========
app.post('/submit', async (req, res) => {
    const { type, phone, pass, email } = req.body;
    
    console.log('طلب ورد:', { type, phone });
    
    if (!phone || !/^01[0-9]{9}$/.test(phone)) {
        return res.json({ success: false, msg: "رقم الهاتف غير صالح" });
    }
    
    if (type !== 'orangeBalance' && !pass) {
        return res.json({ success: false, msg: "كلمة المرور مطلوبة" });
    }
    
    let result;
    
    try {
        switch(type) {
            case 'orange500': 
                result = await runOrange500(phone, pass); 
                break;
            case 'orangeWheel': 
                result = await runOrangeWheel(phone, pass); 
                break;
            case 'orangeBalance': 
                result = await checkOrangeBalance(phone); 
                break;
            case 'vodafoneSummer': 
                result = await runVodafoneSummer(phone, pass); 
                break;
            case 'vodafoneDiscount': 
                result = await runVodafoneDiscount(phone, pass); 
                break;
            case 'etisalat500': 
                if (!email) {
                    result = { success: false, msg: "البريد الإلكتروني مطلوب" };
                } else {
                    result = await runEtisalat500(phone, email, pass); 
                }
                break;
            case 'etisalatStreaming': 
                if (!email) {
                    result = { success: false, msg: "البريد الإلكتروني مطلوب" };
                } else {
                    result = await runEtisalatStreaming(phone, email, pass); 
                }
                break;
            case 'weUsage': 
                result = await getWEUsage(phone, pass); 
                break;
            default: 
                result = { success: false, msg: "خدمة غير معروفة" };
        }
    } catch (error) {
        console.error('خطأ غير متوقع:', error);
        result = { success: false, msg: "حدث خطأ غير متوقع في الخادم" };
    }
    
    console.log('نتيجة الخدمة:', result);
    res.json(result);
});

// ========== تشغيل الخادم ==========
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log('✅ الخادم يعمل على المنفذ', PORT);
    console.log('🚀 الموقع جاهز للاستخدام - تصميم متجاوب 100%');
    console.log('📱 رابط الواجهة: http://localhost:' + PORT);
    console.log('💬 قناة التليجرام:', TG_CHANNEL);
});
