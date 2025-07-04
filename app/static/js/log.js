document.addEventListener("DOMContentLoaded", function () {
    // Client-side form validation
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const inputs = form.querySelectorAll('.auth-input[required]');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.classList.add('is-invalid');
                    const feedback = input.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.style.opacity = '0';
                        setTimeout(() => {
                            feedback.style.transition = 'opacity 0.3s ease';
                            feedback.style.opacity = '1';
                        }, 10);
                    }
                } else {
                    input.classList.remove('is-invalid');
                    const feedback = input.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.style.transition = 'opacity 0.3s ease';
                        feedback.style.opacity = '0';
                        setTimeout(() => feedback.remove(), 300);
                    }
                }
            });
            // Additional validation for password confirmation
            const password = form.querySelector('#password');
            const confirmPassword = form.querySelector('#confirm_password');
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                valid = false;
                confirmPassword.classList.add('is-invalid');
                const feedback = confirmPassword.parentElement.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = 'Mật khẩu xác nhận không khớp.';
                    feedback.style.opacity = '0';
                    setTimeout(() => {
                        feedback.style.transition = 'opacity 0.3s ease';
                        feedback.style.opacity = '1';
                    }, 10);
                }
            }
            if (!valid) {
                e.preventDefault();
                console.warn('Form validation failed: Một hoặc nhiều trường không hợp lệ.');
            }
        });
    });
});

// Toggle password visibility
window.togglePassword = function (id) {
    const passwordInput = document.getElementById(id);
    const toggleIcon = passwordInput.parentElement.querySelector('.toggle-password i');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('bi-eye-slash-fill');
        toggleIcon.classList.add('bi-eye-fill');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('bi-eye-fill');
        toggleIcon.classList.add('bi-eye-slash-fill');
    }
};