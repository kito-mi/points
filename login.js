// حساب مستخدم افتراضي
const validUsername = 'admin';
const validPassword = '1234';

// الحصول على عناصر النموذج
const loginForm = document.getElementById('loginForm');
const errorMessage = document.getElementById('errorMessage');

// معالجة حدث إرسال النموذج
loginForm.addEventListener('submit', function(event) {
    // منع إعادة تحميل الصفحة
    event.preventDefault();

    // الحصول على قيم اسم المستخدم وكلمة المرور
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // التحقق من صحة بيانات تسجيل الدخول
    if (username === validUsername && password === validPassword) {
        // تخزين حالة تسجيل الدخول
        localStorage.setItem('isLoggedIn', 'true');
        
        // الانتقال إلى صفحة العداد
        window.location.href = 'index.html';
    } else {
        // عرض رسالة خطأ
        errorMessage.textContent = 'اسم المستخدم أو كلمة المرور غير صحيحة';
    }
});
