document.addEventListener("DOMContentLoaded", function () {
    // === General UI Interactions (from index.js) ===

    // Smooth scroll for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Hamburger menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
            hamburger.setAttribute('aria-expanded', hamburger.classList.contains('active'));
        });
    }

    // Hide/show navbar on scroll
    let lastScrollTop = 0;
    const navBar = document.querySelector('.nav-bar');
    window.addEventListener('scroll', () => {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            navBar.classList.add('hidden');
        } else {
            navBar.classList.remove('hidden');
        }
        lastScrollTop = scrollTop;
    });

    // Animation on scroll for cards
    const cards = document.querySelectorAll('.feature-card, .testimonial-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                const skeleton = entry.target.querySelector('.skeleton');
                if (skeleton) skeleton.remove();
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Lazy load images
    const images = document.querySelectorAll('img[data-src]');
    const imgObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    }, { threshold: 0.1 });

    images.forEach(img => imgObserver.observe(img));

    // Dynamic CTA button animation
    const ctaButtons = document.querySelectorAll('.btn-primary');
    ctaButtons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            btn.style.setProperty('--x', `${x}px`);
            btn.style.setProperty('--y', `${y}px`);
        });
    });

    // Newsletter form submission with basic validation
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailInput = newsletterForm.querySelector('.newsletter-input');
            const email = emailInput.value.trim();
            if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                try {
                    // Simulate API call
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    showAlert('Cảm ơn bạn đã đăng ký nhận tin!', 'success');
                    emailInput.value = '';
                } catch {
                    showAlert('Đã có lỗi xảy ra. Vui lòng thử lại sau.', 'error');
                }
            } else {
                showAlert('Vui lòng nhập email hợp lệ.', 'error');
            }
        });
    }

    // Keyboard navigation support
    const focusableElements = document.querySelectorAll('a, button, input, [tabindex="0"]');
    focusableElements.forEach(el => {
        el.addEventListener('focus', () => {
            el.classList.add('focused');
        });
        el.addEventListener('blur', () => {
            el.classList.remove('focused');
        });
    });

    // Add styles for animations and accessibility (from index.js)
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        .btn-primary::before {
            content: '';
            position: absolute;
            width: 80px;
            height: 80px;
            background: radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(255, 255, 255, 0.25), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        .btn-primary:hover::before {
            opacity: 1;
        }
        img.loaded {
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .focused {
            outline: 3px solid #1a73e8 !important;
            outline-offset: 2px;
        }
    `;
    document.head.appendChild(style);

    // === User Profile Settings (from scripts.js) ===

    // Load initial user settings (avatar, dark mode, 2FA)
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

            // Update dark mode
            const darkModeCheckbox = document.getElementById('dark_mode');
            if (darkModeCheckbox && data.dark_mode !== undefined) {
                darkModeCheckbox.checked = data.dark_mode;
                document.body.classList.toggle('dark-mode', data.dark_mode);
                console.log('Dark mode initialized:', data.dark_mode);
            } else {
                console.warn('Dark mode setting not returned or checkbox not found');
            }

            // Update 2FA
            const twoFactorCheckbox = document.getElementById('two_factor');
            if (twoFactorCheckbox && data.two_factor !== undefined) {
                twoFactorCheckbox.checked = data.two_factor;
                console.log('2FA initialized:', data.two_factor);
            } else {
                console.warn('2FA setting not returned or checkbox not found');
            }
        } else {
            console.error('Lỗi tải cài đặt người dùng:', data.message || 'No data returned');
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

    // Xử lý toggle 2FA
    const twoFactorCheckbox = document.getElementById('two_factor');
    if (twoFactorCheckbox) {
        twoFactorCheckbox.addEventListener('change', function (e) {
            const isEnabled = e.target.checked;
            fetch('/update_2fa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ enabled: isEnabled })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Cài đặt xác thực hai yếu tố đã được cập nhật!', 'success');
                    console.log('2FA updated:', isEnabled);
                } else {
                    showAlert(`Lỗi: ${data.message}`, 'error');
                    e.target.checked = !isEnabled;
                    console.error('2FA update failed:', data.message);
                }
            })
            .catch(error => {
                console.error('Lỗi cập nhật 2FA:', error);
                showAlert('Lỗi khi cập nhật xác thực hai yếu tố. Vui lòng thử lại.', 'error');
                e.target.checked = !isEnabled;
            });
        });
    }

    // Xử lý toggle chế độ sáng/tối
    const darkModeCheckbox = document.getElementById('dark_mode');
    if (darkModeCheckbox) {
        darkModeCheckbox.addEventListener('change', function (e) {
            const isDarkMode = e.target.checked;
            document.body.classList.toggle('dark-mode', isDarkMode);
            console.log('Dark mode toggled to:', isDarkMode);
            fetch('/update_theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dark_mode: isDarkMode })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Cài đặt giao diện đã được cập nhật!', 'success');
                    console.log('Dark mode update successful');
                } else {
                    showAlert(`Lỗi: ${data.message}`, 'error');
                    e.target.checked = !isDarkMode;
                    document.body.classList.toggle('dark-mode', !isDarkMode);
                    console.error('Dark mode update failed:', data.message);
                }
            })
            .catch(error => {
                console.error('Lỗi cập nhật giao diện:', error);
                showAlert('Lỗi khi cập nhật giao diện. Vui lòng thử lại.', 'error');
                e.target.checked = !isDarkMode;
                document.body.classList.toggle('dark-mode', !isDarkMode);
            });
        });
    } else {
        console.error('Dark mode checkbox not found');
    }

    // Xử lý validation form thông tin
    const profileForm = document.querySelector('.profile-form');
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
            const confirmPassword = passwordForm.querySelector('#password');
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

    // Hàm hiển thị thông báo (from scripts.js)
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

    // Hàm hiển thị feedback (from scripts.js)
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

    // Hàm xóa feedback (from scripts.js)
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
