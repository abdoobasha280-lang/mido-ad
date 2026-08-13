function checkSubscription() {
    // إخفاء قسم القنوات وإظهار نموذج الإدخال
    document.getElementById('sub-section').classList.add('hidden');
    document.getElementById('service-section').classList.remove('hidden');
}

function startProcess() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const statusMsg = document.getElementById('status-msg');

    if (!email || !password) {
        alert('من فضلك ادخل البريد وكلمة السر');
        return;
    }

    statusMsg.classList.remove('hidden');
    statusMsg.innerHTML = "🔄 جاري فحص الحساب وتشغيل العمليات... انتظر قليلاً.";

    // محاكاة الاتصال
    setTimeout(() => {
        statusMsg.innerHTML = "✅ <b>تم الانتهاء من جمع النقاط والوحدات بنجاح!</b><br>متنساش الاسكرين بقى 📸⚡";
    }, 4000);
}
