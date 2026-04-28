document.addEventListener('DOMContentLoaded', () => {
    const taskTable = document.getElementById('task-table');
    const taskList = document.getElementById('task-list');
    const searchInput = document.getElementById('search-input');

    let allCollections = [];

    class CollectionManager {
        async fetchCollections() {
            UIUtils.showLoading();

            try {
                const response = await apiClient.get('/collection/');
                const data = await apiClient.handleResponse(response);

                allCollections = data.data || [];
                this.hideAllFeedback();
                this.renderCollections(allCollections);
            } catch (err) {
                this.showError('Error loading collections. Please try again later.');
                UIUtils.hideElement('task-table');
                UIUtils.hideElement('empty-state');
                console.error('Fetch collections error: ', err);
            } finally {
                UIUtils.hideLoading();
            }
        }

        renderCollections(collections) {
            taskList.innerHTML = '';

            if (!collections.length) {
                taskTable.classList.add('d-none');
                const emptyState = document.getElementById('empty-state');
                if (emptyState) emptyState.classList.remove('d-none');
                return;
            }

            UIUtils.showElement('task-table');
            UIUtils.hideElement('empty-state');

            collections.forEach(col => {
                taskList.appendChild(this.createRow(col));
            });

            this.attachDeleteHandlers();
        }

        createRow(col) {
            const row = document.createElement('tr');

            const titleTd = document.createElement('td');
            titleTd.textContent = col.title;
            row.appendChild(titleTd);

            const descTd = document.createElement('td');
            descTd.classList.add('d-none', 'd-md-table-cell');
            descTd.textContent = col.description || '-';
            row.appendChild(descTd);

            const createdTd = document.createElement('td');
            createdTd.classList.add('d-none', 'd-md-table-cell');
            createdTd.textContent = UIUtils.formatDateTime(col.created_at);
            row.appendChild(createdTd);

            const actionsTd = document.createElement('td');
            actionsTd.innerHTML = this.getActionButtons(col.id);
            row.appendChild(actionsTd);

            return row;
        }

        getActionButtons(id) {
            return `
                <div class="d-flex gap-2">
                    <a href="/${id}" class="btn btn-sm btn-outline-primary" title="View">
                        <i class="bi bi-eye"></i>
                    </a>
                    <a href="/edit/${id}" class="btn btn-sm btn-outline-warning" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger btn-delete-task"
                            data-id="${id}" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
        }

        attachDeleteHandlers() {
            document.querySelectorAll('.btn-delete-task').forEach(button => {
                button.addEventListener('click', async () => {
                    const id = button.getAttribute('data-id');
                    if (!id) return;

                    const confirmed = await UIUtils.confirmAction('Are you sure you want to delete this collection?');
                    if (!confirmed) return;

                    await this.deleteCollection(id, button);
                });
            });
        }

        async deleteCollection(id, button) {
            const originalHTML = button.innerHTML;

            try {
                button.disabled = true;
                button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';

                const response = await apiClient.delete(`/collection/${id}`);
                await apiClient.handleResponse(response);

                allCollections = allCollections.filter(col => col.id != id);
                this.applyFilters();
            } catch (error) {
                console.error('Delete error:', error);
                alert(error.message || 'Error deleting collection');
                button.disabled = false;
                button.innerHTML = originalHTML;
            }
        }

        applyFilters() {
            const searchText = searchInput.value.toLowerCase();

            const filtered = allCollections.filter(col => {
                return col.title.toLowerCase().includes(searchText) ||
                    (col.description && col.description.toLowerCase().includes(searchText));
            });

            this.renderCollections(filtered);
        }

        showError(message) {
            const errorText = document.getElementById('error-text');
            const errorMessage = document.getElementById('error-message');
            if (errorText) errorText.textContent = message;
            if (errorMessage) errorMessage.classList.remove('d-none');
        }

        hideAllFeedback() {
            UIUtils.hideElement('error-message');
            const errorText = document.getElementById('error-text');
            if (errorText) errorText.textContent = '';
            UIUtils.hideElement('empty-state');
        }
    }

    const manager = new CollectionManager();
    searchInput.addEventListener('input', () => manager.applyFilters());
    manager.fetchCollections();
});
