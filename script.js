// التحقق من حالة تسجيل الدخول
if (!localStorage.getItem('isLoggedIn')) {
    // إعادة توجيه المستخدم إلى صفحة تسجيل الدخول إذا لم يكن مسجل الدخول
    window.location.href = 'login.html';
}

// Initialize the counter
let count = 0;

// Get references to the counter and button elements
const counterElement = document.getElementById('counter');
const clickButton = document.getElementById('clickButton');
const logoutButton = document.getElementById('logoutButton');

// Add click event listener to the button
clickButton.addEventListener('click', () => {
    // Increment the counter
    count++;
    
    // Update the counter display
    counterElement.textContent = count;
});

// إضافة حدث تسجيل الخروج
logoutButton.addEventListener('click', () => {
    // مسح حالة تسجيل الدخول
    localStorage.removeItem('isLoggedIn');
    
    // إعادة التوجيه إلى صفحة تسجيل الدخول
    window.location.href = 'login.html';
});
