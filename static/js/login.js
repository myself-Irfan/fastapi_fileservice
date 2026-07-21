document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const alertContainer = 'alert-placeholder';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // clear previous alert and validation
        UIUtils.clearValidation(['email', 'password']);
        document.getElementById(alertContainer).innerHTML = '';

        const formData = {
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value.trim()
        };

        // client side validation
        if (!validateForm(formData)) return;

        UIUtils.setLoadingState('loginBtn', true, 'Signing in...')

        try {
            const response = await apiClient.post('/users/login', formData);
            const data = await apiClient.handleResponse(response);

            // store tokens ; data?
            const tokens = data.data || {};
            apiClient.setTokens(tokens.access_token, tokens.refresh_token);

            UIUtils.showAlert(
                alertContainer,
                'success',
                'Login successful. Redirecting...'
            )
            UIUtils.redirectAfterDelay('/');

        } catch (err) {
            // field-level validation errors come back as a list of formatted messages
            if (Array.isArray(err.data?.errors) && err.data.errors.length) {
                UIUtils.showAlert(alertContainer, 'danger', err.data.errors.join('<br>'));
            } else {
                UIUtils.showAlert(alertContainer, 'danger', err.message || 'Login failed.');
            }
        } finally {
            UIUtils.setLoadingState('loginBtn', false)
        }
    });

    function validateForm(data) {
        let isValid = true;

        // email validation
        if (!data.email) {
            UIUtils.showFieldError('email', 'Email is required');
            isValid = false;
        } else if (!UIUtils.isValidEmail(data.email)) {
            UIUtils.showFieldError('email', 'Please enter a valid email');
            isValid = false;
        }

        // password validation
        if (!data.password) {
            UIUtils.showFieldError('password', 'Password is required');
            isValid = false;
        } else if (data.password.length < 5) {
            UIUtils.showFieldError('password', 'Password must be at least 5 characters long');
            isValid = false
        }

        return isValid;
    }
})