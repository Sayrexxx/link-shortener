document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('url-form');
    const urlInput = document.getElementById('url');
    const customCodeInput = document.getElementById('custom-code');
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const shortUrlLink = document.getElementById('short-url');
    const copyBtn = document.getElementById('copy-btn');
    const urlError = document.getElementById('url-error');
    const codeError = document.getElementById('code-error');

    // Real-time validation
    urlInput.addEventListener('input', validateUrl);
    customCodeInput.addEventListener('input', validateCustomCode);

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!validateUrl() || !validateCustomCode()) {
            return;
        }

        try {
            // Show loading state
            submitBtn.disabled = true;
            loading.classList.remove('hidden');

            // Get CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            // Submit data
            const response = await axios.post('/api/links', {
                url: urlInput.value,
                custom_code: customCodeInput.value || undefined
            }, {
                headers: {
                    'X-CSRF-Token': csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            // Show result
            const shortUrl = `${window.location.origin}/${response.data.short_code}`;
            shortUrlLink.textContent = shortUrl;
            shortUrlLink.href = shortUrl;
            resultDiv.classList.remove('hidden');

            // Reset form
            form.reset();
            
        } catch (error) {
            if (error.response) {
                const { data } = error.response;
                if (data.detail) {
                    alert(`Error: ${data.detail}`);
                }
            } else {
                alert('An error occurred. Please try again.');
            }
        } finally {
            submitBtn.disabled = false;
            loading.classList.add('hidden');
        }
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(shortUrlLink.href)
            .then(() => {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy to clipboard';
                }, 2000);
            });
    });

    // Validation functions
    function validateUrl() {
        if (!urlInput.checkValidity()) {
            urlError.textContent = 'Please enter a valid URL (e.g. https://example.com)';
            urlError.classList.remove('hidden');
            return false;
        }
        urlError.classList.add('hidden');
        return true;
    }

    function validateCustomCode() {
        if (customCodeInput.value && !customCodeInput.checkValidity()) {
            codeError.textContent = 'Custom code must be 4-20 alphanumeric characters or hyphens';
            codeError.classList.remove('hidden');
            return false;
        }
        codeError.classList.add('hidden');
        return true;
    }
});
