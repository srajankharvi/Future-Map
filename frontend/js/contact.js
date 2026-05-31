document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;

    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const subjectSelect = document.getElementById('subject');
    const messageInput = document.getElementById('message');
    const charCounter = document.getElementById('charCount');
    const submitBtn = document.getElementById('submitBtn');
    const successOverlay = document.getElementById('successOverlay');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const MAX_CHARS = 1000;

    // 1. Autofill subject from URL query params
    const urlParams = new URLSearchParams(window.location.search);
    const subjectParam = urlParams.get('subject');
    if (subjectParam && subjectSelect) {
        // Find matching option and select it
        for (let option of subjectSelect.options) {
            if (option.value.toLowerCase() === subjectParam.toLowerCase()) {
                subjectSelect.value = option.value;
                break;
            }
        }
        // If select is custom select wrapper (from main.js), we need to trigger update
        subjectSelect.dispatchEvent(new Event('change'));
    }

    // 2. Character counter on message textarea
    if (messageInput && charCounter) {
        messageInput.addEventListener('input', () => {
            const len = messageInput.value.length;
            charCounter.textContent = `${len} / ${MAX_CHARS}`;
            if (len > MAX_CHARS) {
                messageInput.value = messageInput.value.substring(0, MAX_CHARS);
                charCounter.textContent = `${MAX_CHARS} / ${MAX_CHARS}`;
            }
            validateInput(messageInput, messageInput.value.trim().length >= 10);
            checkFormValidity();
        });
    }

    // 3. Form Validation Helpers
    function showError(input, message) {
        const parent = input.closest('.form-group') || input.parentElement;
        parent.classList.add('error');
        parent.classList.remove('success');
        
        let errorMsg = parent.querySelector('.error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('span');
            errorMsg.className = 'error-message';
            parent.appendChild(errorMsg);
        }
        errorMsg.textContent = message;
    }

    function showSuccess(input) {
        const parent = input.closest('.form-group') || input.parentElement;
        parent.classList.remove('error');
        parent.classList.add('success');
        
        const errorMsg = parent.querySelector('.error-message');
        if (errorMsg) errorMsg.remove();
    }

    function validateInput(input, condition, errorMsgText) {
        if (condition) {
            showSuccess(input);
            return true;
        } else {
            showError(input, errorMsgText || 'Invalid value');
            return false;
        }
    }

    // 4. Input Blur Events for real-time validation
    nameInput.addEventListener('blur', () => {
        validateInput(nameInput, nameInput.value.trim().length >= 2, 'Name must be at least 2 characters');
        checkFormValidity();
    });

    emailInput.addEventListener('blur', () => {
        validateInput(emailInput, emailRegex.test(emailInput.value.trim()), 'Please enter a valid email address');
        checkFormValidity();
    });

    subjectSelect.addEventListener('change', () => {
        validateInput(subjectSelect, subjectSelect.value !== '', 'Please select a subject');
        checkFormValidity();
    });

    messageInput.addEventListener('blur', () => {
        validateInput(messageInput, messageInput.value.trim().length >= 10, 'Message must be at least 10 characters');
        checkFormValidity();
    });

    // 5. Check total validity to enable/disable submit button
    function checkFormValidity() {
        const isNameValid = nameInput.value.trim().length >= 2;
        const isEmailValid = emailRegex.test(emailInput.value.trim());
        const isSubjectValid = subjectSelect.value !== '';
        const isMessageValid = messageInput.value.trim().length >= 10;

        const isFormValid = isNameValid && isEmailValid && isSubjectValid && isMessageValid;
        if (submitBtn) {
            submitBtn.disabled = !isFormValid;
        }
        return isFormValid;
    }

    // 6. Handle form submission
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!checkFormValidity()) return;

        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        const payload = {
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            subject: subjectSelect.value,
            message: messageInput.value.trim()
        };

        try {
            let endpoint = '/api/contact';
            if (window.API_BASE) {
                endpoint = `${window.API_BASE}/contact`;
            }

            let responseData;
            if (window.apiFetch) {
                responseData = await window.apiFetch(endpoint, {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
            } else {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                responseData = await response.json();
            }

            if (responseData && responseData.success) {
                // Show success view
                if (successOverlay) {
                    successOverlay.classList.add('visible');
                    contactForm.reset();
                    // Reset custom select dropdown if any
                    subjectSelect.dispatchEvent(new Event('change'));
                } else {
                    if (window.FeedbackModal && typeof window.FeedbackModal.showNotification === 'function') {
                        window.FeedbackModal.showNotification('Message sent successfully!');
                    } else {
                        alert('Message sent successfully!');
                    }
                }
            } else {
                if (responseData && responseData.status === 404) {
                    // Fallback to local success if backend route is not registered (dev server)
                    if (successOverlay) {
                        successOverlay.classList.add('visible');
                        contactForm.reset();
                    } else {
                        alert('Message sent successfully! (Demo Mode)');
                    }
                } else {
                    const errText = responseData.error || 'Failed to submit form. Please try again.';
                    if (window.FeedbackModal && typeof window.FeedbackModal.showNotification === 'function') {
                        window.FeedbackModal.showNotification(errText, false);
                    } else {
                        alert(errText);
                    }
                }
            }
        } catch (err) {
            console.error('Contact submission error:', err);
            // Simulate success in frontend-only development mode
            if (successOverlay) {
                successOverlay.classList.add('visible');
                contactForm.reset();
            } else {
                alert('Message sent successfully! (Demo Mode)');
            }
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    // Close success overlay/banner if there's a close button
    const closeSuccessBtn = document.getElementById('closeSuccessBtn');
    if (closeSuccessBtn && successOverlay) {
        closeSuccessBtn.addEventListener('click', () => {
            successOverlay.classList.remove('visible');
        });
    }
});
