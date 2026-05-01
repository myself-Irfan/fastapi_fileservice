class FileUtils {

    static async handlePreview(fileId, filename, mimeType) {
        document.getElementById('previewModalLabel').textContent = filename;
        document.getElementById('preview-download-btn').onclick = () => FileUtils.handleDownload(fileId, filename);
        const modal = new bootstrap.Modal(document.getElementById('previewModal'));
        modal.show();

        try {
            const response = await apiClient.request(`/files/${fileId}/download`);
            if (!response.ok) throw new Error('Could not load file.');

            const body = document.getElementById('preview-body');

            if (mimeType.startsWith('text/')) {
                const text = await response.text();
                body.innerHTML = `<pre class="text-start text-white-50 m-0" style="max-height:70vh;overflow:auto;white-space:pre-wrap;word-break:break-word;">${FileUtils.escapeHtml(text)}</pre>`;
                return;
            }

            const blob = await response.blob();
            FileUtils._previewUrl = URL.createObjectURL(blob);

            if (mimeType.startsWith('image/')) {
                body.innerHTML = `<img src="${FileUtils._previewUrl}" class="img-fluid rounded" alt="${FileUtils.escapeHtml(filename)}" style="max-height:75vh;">`;
            } else if (mimeType === 'application/pdf') {
                body.innerHTML = `<iframe src="${FileUtils._previewUrl}" style="width:100%;height:75vh;border:none;" title="${FileUtils.escapeHtml(filename)}"></iframe>`;
            } else if (mimeType.startsWith('audio/')) {
                body.innerHTML = `<audio controls class="w-100 mt-2"><source src="${FileUtils._previewUrl}" type="${mimeType}">Your browser does not support audio playback.</audio>`;
            } else if (mimeType.startsWith('video/')) {
                body.innerHTML = `<video controls class="w-100" style="max-height:75vh;"><source src="${FileUtils._previewUrl}" type="${mimeType}">Your browser does not support video playback.</video>`;
            } else {
                URL.revokeObjectURL(FileUtils._previewUrl);
                FileUtils._previewUrl = null;
                body.innerHTML = `<div class="py-5 text-muted"><i class="bi bi-file-earmark display-4 d-block mb-3"></i>Preview not available for this file type.<br><small>${FileUtils.escapeHtml(mimeType)}</small></div>`;
            }
        } catch (error) {
            document.getElementById('preview-body').innerHTML = `<div class="py-4 text-danger"><i class="bi bi-exclamation-triangle me-2"></i>${error.message || 'Failed to load preview.'}</div>`;
        }
    }

    static async handleDownload(fileId, filename) {
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

    static formatBytes(bytes) {
            if (bytes < 1024) return `${bytes} B`;
            if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
            return `${(bytes / 1048576).toFixed(1)} MB`;
        }

    static escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}