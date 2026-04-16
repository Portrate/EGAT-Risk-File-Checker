// upload.js
let selectedFile = null;

function getSelectedFile() {
    return selectedFile;
}

function initUpload() {
    const uploadCard = document.getElementById('upload-card');
    const fileInput = document.getElementById('pdf-input');
    const uploadDesc = document.getElementById('upload-desc');

    if (!uploadCard || !fileInput) return;

    // Prevent programmatic click from bubbling back to the card (avoids double-trigger)
    fileInput.addEventListener('click', e => e.stopPropagation());

    // Prevent the browse label's native click from also hitting the card handler
    const browseLabel = uploadCard.querySelector('label[for="pdf-input"]');
    if (browseLabel) {
        browseLabel.addEventListener('click', e => e.stopPropagation());
    }

    // Click anywhere else on the card → open file dialog
    uploadCard.addEventListener('click', () => fileInput.click());

    // File chosen via dialog
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            setFile(fileInput.files[0]);
        }
    });

    // Drag-and-drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
        uploadCard.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
    });

    uploadCard.addEventListener('dragenter', () => setHighlight(true));
    uploadCard.addEventListener('dragover',  () => setHighlight(true));
    uploadCard.addEventListener('dragleave', () => setHighlight(false));
    uploadCard.addEventListener('drop', e => {
        setHighlight(false);
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type === 'application/pdf') {
            setFile(files[0]);
        }
    });

    function setHighlight(on) {
        uploadCard.style.borderColor = on
            ? 'var(--color-primary)'
            : 'var(--color-outline-variant)';
        uploadCard.style.backgroundColor = on
            ? 'var(--color-surface-container)'
            : 'var(--color-surface-container-low)';
    }

    function setFile(file) {
        selectedFile = file;
        if (uploadDesc) {
            uploadDesc.innerHTML = `<span class="text-primary" style="font-weight:700;">${file.name}</span> ready for verification.`;
        }
    }
}
