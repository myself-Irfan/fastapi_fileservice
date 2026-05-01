document.addEventListener('DOMContentLoaded', async () => {

    class FileManager {
        constructor() {
            this.files = [];
            this.init();
        }

        async init() {
            await this.loadFiles();
            this.setupEventListeners();
        }

        async loadFiles() {
            UIUtils.showLoading();
            try {
                const response = await apiClient.get('/files/');
                const data = await apiClient.handleResponse(response);
                this.files = data.data || [];
                this.renderFiles(this.files);
            } catch (error) {
                this.showError(error.message || 'Failed to load files.');
            } finally {
                UIUtils.hideLoading();
            }
        }

        renderFiles(files) {
            const list = document.getElementById('files-list');
            const table = document.getElementById('files-table');
            const empty = document.getElementById('empty-state');

            list.innerHTML = '';

            if (!files.length) {
                table.classList.add('d-none');
                empty.classList.remove('d-none');
                return;
            }

            table.classList.remove('d-none');
            empty.classList.add('d-none');
            files.forEach(file => list.appendChild(this.createRow(file)));
        }

        createRow(file) {
            const tr = document.createElement('tr');
            tr.dataset.id = file.id;
            tr.innerHTML = `
                <td>${this.escapeHtml(file.title)}</td>
                <td><span class="badge bg-secondary">${this.escapeHtml(file.extension)}</span></td>
                <td>${this.formatBytes(file.file_size)}</td>
                <td class="d-none d-md-table-cell">${UIUtils.formatDateTime(file.created_at)}</td>
                <td>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-success btn-download"
                                data-id="${file.id}" data-title="${this.escapeHtml(file.title)}" title="Download">
                            <i class="bi bi-download"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger btn-delete"
                                data-id="${file.id}" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            return tr;
        }

        setupEventListeners() {
            document.getElementById('upload-form')?.addEventListener('submit', e => this.handleUpload(e));

            document.getElementById('files-list')?.addEventListener('click', e => {
                const downloadBtn = e.target.closest('.btn-download');
                const deleteBtn = e.target.closest('.btn-delete');
                if (downloadBtn) this.handleDownload(downloadBtn.dataset.id, downloadBtn.dataset.title);
                if (deleteBtn) this.handleDelete(deleteBtn.dataset.id, deleteBtn);
            });

            document.getElementById('search-input')?.addEventListener('input', e => {
                const q = e.target.value.toLowerCase();
                const filtered = this.files.filter(f =>
                    f.title.toLowerCase().includes(q) || f.extension.toLowerCase().includes(q)
                );
                this.renderFiles(filtered);
            });

            document.getElementById('uploadModal')?.addEventListener('hidden.bs.modal', () => {
                document.getElementById('file-input').value = '';
            });
        }

        async handleUpload(e) {
            e.preventDefault();
            const fileInput = document.getElementById('file-input');
            if (!fileInput.files.length) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const btn = document.getElementById('upload-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uploading...';

            try {
                const response = await apiClient.upload('/files/upload', formData);
                await apiClient.handleResponse(response);

                const modalEl = document.getElementById('uploadModal');
                bootstrap.Modal.getInstance(modalEl)?.hide();

                await this.loadFiles();
                UIUtils.showAlert('alert-container', 'success', 'File uploaded successfully.');
            } catch (error) {
                UIUtils.showAlert('alert-container', 'danger', error.message || 'Upload failed.');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-upload me-2"></i>Upload';
            }
        }

        async handleDownload(fileId, filename) {
            try {
                const response = await apiClient.request(`/files/${fileId}/download`);
                if (!response.ok) throw new Error('Download failed.');

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (error) {
                UIUtils.showAlert('alert-container', 'danger', error.message || 'Download failed.');
            }
        }

        async handleDelete(fileId, btn) {
            if (!confirm('Delete this file?')) return;

            const originalHTML = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

            try {
                const response = await apiClient.delete(`/files/${fileId}`);
                await apiClient.handleResponse(response);
                this.files = this.files.filter(f => f.id != fileId);
                this.renderFiles(this.files);
                UIUtils.showAlert('alert-container', 'success', 'File deleted.');
            } catch (error) {
                UIUtils.showAlert('alert-container', 'danger', error.message || 'Delete failed.');
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            }
        }

        formatBytes(bytes) {
            if (bytes < 1024) return `${bytes} B`;
            if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
            return `${(bytes / 1048576).toFixed(1)} MB`;
        }

        escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        showError(message) {
            const box = document.getElementById('error-message');
            const text = document.getElementById('error-text');
            if (box && text) {
                text.textContent = message;
                box.classList.remove('d-none');
            }
        }
    }

    new FileManager();
});