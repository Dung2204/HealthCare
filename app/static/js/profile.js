document.addEventListener("DOMContentLoaded", function () {
    // Load initial user settings (avatar, notifications)
    fetch('/get_user_settings', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update avatar
            const avatarImg = document.querySelector('.avatar-img');
            if (avatarImg && data.avatar_url) {
                avatarImg.src = `${data.avatar_url}?t=${new Date().getTime()}`;
                console.log('Avatar loaded:', data.avatar_url);
            } else {
                console.warn('No avatar URL returned or avatarImg not found');
            }

            // Update notifications
            const notificationsCheckbox = document.getElementById('notifications');
            if (notificationsCheckbox && data.notifications !== undefined) {
                notificationsCheckbox.checked = data.notifications;
                console.log('Notifications initialized:', data.notifications);
            } else {
                console.warn('Notifications setting not returned or checkbox not found');
            }
        } else {
            console.error('Lỗi tải cài đặt người dùng:', data.message);
        }
    })
    .catch(error => {
        console.error('Lỗi kết nối khi tải cài đặt:', error);
    });

    // Tải lại ảnh avatar để tránh cache
    const avatarImg = document.querySelector('.avatar-img');
    if (avatarImg) {
        const src = avatarImg.src;
        avatarImg.src = src.includes('?t=') ? src.replace(/(\?t=)\d+/, `?t=${new Date().getTime()}`) : `${src}?t=${new Date().getTime()}`;
    }

    // Xử lý tải ảnh avatar
    const avatarInput = document.getElementById('avatar');
    const avatarForm = document.querySelector('.profile-avatar-form');
    if (avatarInput && avatarForm) {
        avatarForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const file = avatarInput.files[0];
            if (!file) {
                showFeedback(avatarInput, 'Vui lòng chọn một file ảnh.');
                return;
            }
            const allowedExtensions = ['png', 'jpg', 'jpeg', 'gif'];
            const extension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(extension)) {
                showFeedback(avatarInput, 'Định dạng file không được hỗ trợ.');
                return;
            }
            const formData = new FormData(avatarForm);
            fetch('/upload_avatar', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    avatarImg.src = `${data.url}?t=${new Date().getTime()}`;
                    showAlert('Cập nhật ảnh đại diện thành công!', 'success');
                    updateProfileProgress();
                    console.log('Avatar updated:', data.url);
                } else {
                    showAlert(`Lỗi khi tải ảnh lên: ${data.message}`, 'error');
                    console.error('Avatar upload failed:', data.message);
                }
            })
            .catch(error => {
                console.error('Lỗi tải ảnh:', error);
                showAlert('Lỗi khi tải ảnh lên. Vui lòng thử lại.', 'error');
            });
        });
    }

    // Xử lý toggle thông báo
    const notificationsCheckbox = document.getElementById('notifications');
    if (notificationsCheckbox) {
        notificationsCheckbox.addEventListener('change', function (e) {
            fetch('/update_notifications', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ enabled: e.target.checked })
            })
            .then(response => response.json())
            .then(data => {
                showAlert(
                    data.success ? 'Cài đặt thông báo đã được cập nhật!' : `Lỗi: ${data.message}`,
                    data.success ? 'success' : 'error'
                );
                console.log('Notifications updated:', data.success);
            })
            .catch(error => {
                console.error('Lỗi cập nhật thông báo:', error);
                showAlert('Lỗi khi cập nhật thông báo. Vui lòng thử lại.', 'error');
            });
        });
    }

    // Xử lý validation form thông tin
    const profileForm = document.querySelector('.profile-form[action="/update_profile"]');
    if (profileForm) {
        profileForm.addEventListener('submit', function (e) {
            const inputs = profileForm.querySelectorAll('input[required]');
            const bio = profileForm.querySelector('#bio');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    showFeedback(input, 'Vui lòng điền trường này.');
                } else {
                    clearFeedback(input);
                }
            });
            if (bio && bio.value.trim().length > 200) {
                valid = false;
                showFeedback(bio, 'Mô tả không được vượt quá 200 ký tự.');
            } else if (bio) {
                clearFeedback(bio);
            }
            if (!valid) {
                e.preventDefault();
                console.warn('Validation failed: Một hoặc nhiều trường không hợp lệ.');
            } else {
                e.preventDefault();
                const formData = new FormData(profileForm);
                fetch('/update_profile', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('Cập nhật thông tin thành công!', 'success');
                        updateProfileProgress();
                    } else {
                        showAlert(`Lỗi: ${data.message}`, 'error');
                    }
                })
                .catch(error => {
                    console.error('Lỗi cập nhật thông tin:', error);
                    showAlert('Lỗi khi cập nhật thông tin. Vui lòng thử lại.', 'error');
                });
            }
        });
    }

    // Xử lý form đổi mật khẩu
    const passwordForm = document.querySelector('form[action="/change_password"]');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function (e) {
            const currentPassword = passwordForm.querySelector('#current_password');
            const newPassword = passwordForm.querySelector('#new_password');
            const confirmPassword = passwordForm.querySelector('#confirm_new_password');
            let valid = true;

            if (currentPassword && !currentPassword.value.trim()) {
                valid = false;
                showFeedback(currentPassword, 'Vui lòng nhập mật khẩu hiện tại.');
            } else if (currentPassword) {
                clearFeedback(currentPassword);
            }

            if (newPassword && (!newPassword.value.trim() || newPassword.value.length < 6)) {
                valid = false;
                showFeedback(newPassword, 'Mật khẩu mới phải có ít nhất 6 ký tự.');
            } else if (newPassword) {
                clearFeedback(newPassword);
            }

            if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
                valid = false;
                showFeedback(confirmPassword, 'Mật khẩu xác nhận không khớp.');
            } else if (confirmPassword) {
                clearFeedback(confirmPassword);
            }

            if (!valid) {
                e.preventDefault();
                console.warn('Password form validation failed.');
            }
        });
    }

    // Cập nhật thanh tiến độ hoàn thành hồ sơ
    function updateProfileProgress() {
        const username = document.querySelector('#username').value.trim();
        const email = document.querySelector('#email').value.trim();
        const bio = document.querySelector('#bio').value.trim();
        const hasAvatar = avatarImg.src.includes('default.jpg') ? false : true;
        let completedFields = 0;
        if (username) completedFields++;
        if (email) completedFields++;
        if (bio) completedFields++;
        if (hasAvatar) completedFields++;
        const progress = (completedFields / 4) * 100;
        const progressBar = document.querySelector('#profile-progress');
        const progressValue = document.querySelector('#profile-progress-value');
        if (progressBar && progressValue) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
            progressValue.textContent = `${Math.round(progress)}%`;
        }
    }

    // Khởi tạo thanh tiến độ khi tải trang
    updateProfileProgress();

    // Hàm hiển thị thông báo
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `<i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
        document.querySelector('.profile-container').prepend(alert);
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 2500);
    }

    // Hàm hiển thị feedback
    function showFeedback(input, message) {
        input.classList.add('is-invalid');
        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            input.parentNode.appendChild(feedback);
        }
        feedback.style.opacity = '0';
        setTimeout(() => {
            feedback.style.transition = 'opacity 0.3s ease';
            feedback.style.opacity = '1';
        }, 10);
    }

    // Hàm xóa feedback
    function clearFeedback(input) {
        input.classList.remove('is-invalid');
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.transition = 'opacity 0.3s ease';
            feedback.style.opacity = '0';
            setTimeout(() => feedback.remove(), 300);
        }
    }
});