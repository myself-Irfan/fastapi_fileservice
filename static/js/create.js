document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('create-form');
    const titleInput = document.getElementById('title');

    class TaskCreator {
        constructor() {
            this.setupEventListener();
        }

        setupEventListener() {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
            titleInput.addEventListener('blur', () => this.validateOnBlur());
            titleInput.addEventListener('input', () => this.clearMessageOnInput());
        }

        async handleSubmit(event) {
            event.preventDefault();

            this.hideAllMessages();

            if (!this.validateForm()) return;

            UIUtils.setLoadingState('create-btn', true, 'Creating...');

            const payload = this.getFormData();

            try {
                const response = await apiClient.post('/collection/', payload);
                await apiClient.handleResponse(response);

                UIUtils.showFeedback(
                    'feedback-message',
                    'feedback-icon',
                    'feedback-text',
                    'success',
                    'Collection created successfully! Redirecting...'
                );

                form.reset();
                UIUtils.redirectAfterDelay('/');
            } catch (error) {
                console.error('Error creating collection:', error);
                UIUtils.showFeedback(
                    'feedback-message',
                    'feedback-icon',
                    'feedback-text',
                    'danger',
                    error.message || 'Error creating collection. Please try again.'
                );
            } finally {
                UIUtils.setLoadingState('create-btn', false);
            }
        }

        getFormData() {
            return {
                title: document.getElementById('title').value.trim(),
                description: document.getElementById('description').value.trim() || null,
            };
        }

        validateForm() {
            const title = document.getElementById('title').value.trim();

            if (!title) {
                UIUtils.showFeedback('feedback-message', 'feedback-icon', 'feedback-text', 'danger', 'Title is required');
                return false;
            }

            if (title.length < 3 || title.length > 100) {
                UIUtils.showFeedback('feedback-message', 'feedback-icon', 'feedback-text', 'danger', 'Title must be between 3 and 100 characters');
                return false;
            }

            return true;
        }

        validateOnBlur() {
            if (titleInput.value.trim()) this.validateForm();
        }

        clearMessageOnInput() {
            const feedbackDiv = document.getElementById('feedback-message');
            if (!feedbackDiv.classList.contains('d-none')) this.hideAllMessages();
        }

        hideAllMessages() {
            UIUtils.hideFeedback('feedback-message', 'feedback-icon', 'feedback-text');
        }
    }

    new TaskCreator();
});
