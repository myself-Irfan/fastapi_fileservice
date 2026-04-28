document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('edit-form');
    const submitButton = form.querySelector('button[type=submit]');
    const originalButtonText = submitButton.textContent;

    const feedback = document.getElementById('feedback-message');
    const feedbackText = document.getElementById('feedback-text');
    const feedbackIcon = document.getElementById('feedback-icon');

    const collectionId = COLLECTION_ID;

    async function fetchCollection() {
        try {
            const res = await apiClient.get(`/collection/${collectionId}`);
            const data = await apiClient.handleResponse(res);
            populateForm(data.data);
        } catch (err) {
            showFeedback('danger', 'Error loading collection. Please try again.');
            console.error(err);
        }
    }

    function populateForm(collection) {
        document.getElementById('title').value = collection.title || '';
        document.getElementById('description').value = collection.description || '';
    }

    function showLoading() {
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Updating...
        `;
    }

    function hideLoading() {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }

    function showFeedback(type, message) {
        feedback.className = `alert alert-${type} mt-3`;
        feedback.classList.remove('d-none');
        feedbackText.textContent = message;
        feedbackIcon.className = type === 'success'
            ? 'bi bi-check-circle-fill me-2'
            : 'bi bi-exclamation-triangle-fill me-2';
    }

    function validateForm() {
        const title = document.getElementById('title').value.trim();

        if (!title) {
            showFeedback('danger', 'Title is required.');
            return false;
        }

        if (title.length < 3 || title.length > 100) {
            showFeedback('warning', 'Title must be between 3 and 100 characters.');
            return false;
        }

        return true;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        feedback.classList.add('d-none');

        if (!validateForm()) return;

        showLoading();

        const payload = {
            title: document.getElementById('title').value.trim(),
            description: document.getElementById('description').value.trim() || null,
        };

        try {
            const res = await apiClient.put(`/collection/${collectionId}`, payload);
            await apiClient.handleResponse(res);

            showFeedback('success', 'Collection updated successfully.');
            setTimeout(() => { window.location.href = '/'; }, 1500);
        } catch (err) {
            showFeedback('danger', err.message);
            console.error(err);
        } finally {
            hideLoading();
        }
    });

    fetchCollection();
});
