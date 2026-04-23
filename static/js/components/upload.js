let selectedFile = null;

function getSelectedFile() {
    return selectedFile;
}

// Make the upload card work — user can click it or drag a file onto it.
function initUpload() {
    const uploadCard = document.getElementById('upload-card');
    const fileInput = document.getElementById('pdf-input');
    const uploadDesc = document.getElementById('upload-desc');

    if (!uploadCard || !fileInput) return;

    // Stop a click on the file input from also triggering the card's click handler
    fileInput.addEventListener('click', e => e.stopPropagation());

    // Same fix for the browse label so it doesn't double-fire
    const browseLabel = uploadCard.querySelector('label[for="pdf-input"]');
    if (browseLabel) {
        browseLabel.addEventListener('click', e => e.stopPropagation());
    }

    // Clicking the card opens the file picker
    uploadCard.addEventListener('click', () => fileInput.click());

    // User picked a file through the dialog
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            setFile(fileInput.files[0]);
        }
    });

    // Stop the browser from opening the file when something is dragged over the card.
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
        uploadCard.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
    });

    uploadCard.addEventListener('dragenter', () => setHighlight(true));
    uploadCard.addEventListener('dragover',  () => setHighlight(true));
    uploadCard.addEventListener('dragleave', () => setHighlight(false));
    uploadCard.addEventListener('drop', e => {
        setHighlight(false);
        const files = e.dataTransfer.files;
        // Only use the file if it is a PDF; ignore everything else.
        if (files.length > 0 && files[0].type === 'application/pdf') {
            setFile(files[0]);
        }
    });

    // Change the card border colour when a file is being dragged over it.
    function setHighlight(on) {
        uploadCard.style.borderColor = on
            ? 'var(--color-primary)'
            : 'var(--color-outline-variant)';
        uploadCard.style.backgroundColor = on
            ? 'var(--color-surface-container)'
            : 'var(--color-surface-container-low)';
    }

    // Save the chosen file and update the text shown inside the card.
    function setFile(file) {
        selectedFile = file;
        if (uploadDesc) {
            uploadDesc.innerHTML = `<span class="text-primary" style="font-weight:700;">${file.name}</span> ready for verification.`;
        }
    }
}
