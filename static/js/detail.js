document.addEventListener('DOMContentLoaded', async () => {
    const collectionId = COLLECTION_ID;

    class CollectionDetail {
        constructor(id) {
            this.id = id;
            this.files = [];
            this.init();
        }

        async init() {
            await Promise.all([this.loadCollection(), this.loadFiles()]);
            this.setupEventListeners();
        }

        async loadCollection() {
            UIUtils.showLoading();
            try {
                const response = await apiClient.get(`/collection/${this.id}`);
                const data = await apiClient.handleResponse(response);
                this.populateCollection(data.data);
                UIUtils.showElement('collection-container');
            } catch (error) {
                console.error('Failed to load collection:', error);
                this.showError(error.message || 'Failed to load collection.');
            } finally {
                UIUtils.hideLoading();
            }
        }

        populateCollection(col) {
            const set = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            };
            set('collection-title', col.title);
            set('collection-description', col.description || 'No description provided.');
            set('collection-created', UIUtils.formatDateTime(col.created_at));
            set('collection-updated', col.updated_at ? UIUtils.formatDateTime(col.updated_at) : '-');
        }

        async loadFiles() {
            try {
                const response = await apiClient.get(`/files/?document_id=${this.id}`);
                const data = await apiClient.handleResponse(response);
                this.files = data.data || [];
                this.renderFiles();
            } catch (error) {
                console.error('Failed to load files:', error);
            }
        }

        renderFiles() {
            const filesList = document.getElementById('files-list');
            const filesTable = document.getElementById('files-table');
            const emptyFiles = document.getElementById('empty-files');

            filesList.innerHTML = '';

            if (!this.files.length) {
                filesTable.classList.add('d-none');
                emptyFiles.classList.remove('d-none');
                return;
            }

            filesTable.classList.remove('d-none');
            emptyFiles.classList.add('d-none');

            this.files.forEach(file => filesList.appendChild(this.createFileRow(file)));
        }

        createFileRow(file) {
            const tr = document.createElement('tr');
            tr.dataset.id = file.id;
            tr.innerHTML = `
                <td>${FileUtils.escapeHtml(file.title)}</td>
                <td><span class="badge bg-secondary">${FileUtils.escapeHtml(file.extension)}</span></td>
                <td>${FileUtils.formatBytes(file.file_size)}</td>
                <td class="d-none d-md-table-cell">${UIUtils.formatDateTime(file.created_at)}</td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-info btn-preview"
                                data-id="${file.id}" data-title="${FileUtils.escapeHtml(file.title)}"
                                data-mime="${FileUtils.escapeHtml(file.mime_type)}" title="Preview">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success btn-download"
                                data-id="${file.id}" data-title="${FileUtils.escapeHtml(file.title)}" title="Download">
                            <i class="bi bi-download"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger btn-delete-file"
                                data-id="${file.id}" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            return tr;
        }

        setupEventListeners() {
            document.getElementById('delete-button')?.addEventListener('click', () => this.handleDeleteCollection());
            document.getElementById('upload-form')?.addEventListener('submit', (e) => this.handleUpload(e));

            document.getElementById('files-list')?.addEventListener('click', (e) => {
                const previewBtn = e.target.closest('.btn-preview');
                const downloadBtn = e.target.closest('.btn-download');
                const deleteBtn = e.target.closest('.btn-delete-file');
                if (previewBtn) FileUtils.handlePreview(previewBtn.dataset.id, previewBtn.dataset.title, previewBtn.dataset.mime);
                if (downloadBtn) FileUtils.handleDownload(downloadBtn.dataset.id, downloadBtn.dataset.title);
                if (deleteBtn) this.handleDeleteFile(deleteBtn.dataset.id, deleteBtn);
            });

            document.getElementById('previewModal')?.addEventListener('hidden.bs.modal', () => {
                const body = document.getElementById('preview-body');
                body.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
                document.getElementById('preview-download-btn').onclick = null;
                if (FileUtils._previewUrl) {
                    URL.revokeObjectURL(FileUtils._previewUrl);
                    FileUtils._previewUrl = null;
                }
            });
        }

        async handleDeleteCollection() {
            if (!confirm('Delete this collection? Uploaded files will not be deleted.')) return;

            UIUtils.showLoading();
            try {
                const response = await apiClient.delete(`/collection/${this.id}`);
                await apiClient.handleResponse(response);
                window.location.href = '/';
            } catch (error) {
                this.showError(error.message || 'Failed to delete collection.');
            } finally {
                UIUtils.hideLoading();
            }
        }

        async handleUpload(e) {
            e.preventDefault();
            const fileInput = document.getElementById('file-input');
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('document_id', this.id);

            const uploadBtn = document.getElementById('upload-btn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';

            try {
                const response = await apiClient.upload('/files/upload', formData);
                await apiClient.handleResponse(response);

                fileInput.value = '';
                const modalEl = document.getElementById('uploadModal');
                bootstrap.Modal.getInstance(modalEl)?.hide();

                await this.loadFiles();
                UIUtils.showAlert('alert-container', 'success', 'File uploaded successfully.');
            } catch (error) {
                UIUtils.showAlert('alert-container', 'danger', error.message || 'Upload failed.');
            } finally {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="bi bi-upload me-2"></i>Upload';
            }
        }

        async handleDeleteFile(fileId, btn) {
            if (!confirm('Delete this file?')) return;

            const originalHTML = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

            try {
                const response = await apiClient.delete(`/files/${fileId}`);
                await apiClient.handleResponse(response);
                this.files = this.files.filter(f => f.id != fileId);
                this.renderFiles();
            } catch (error) {
                alert(error.message || 'Failed to delete file.');
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            }
        }

        showError(message) {
            const errorBox = document.getElementById('error-message');
            const errorText = document.getElementById('error-text');
            if (errorBox && errorText) {
                errorText.textContent = message;
                errorBox.classList.remove('d-none');
            }
        }
    }

    new CollectionDetail(collectionId);
});
