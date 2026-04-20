// Upload
let selectedFile = null;
let lastResult = null;

function getSelectedFile() {
    return selectedFile;
}

function initUpload() {
    const uploadCard = document.getElementById('upload-card');
    const fileInput  = document.getElementById('pdf-input');
    const uploadDesc = document.getElementById('upload-desc');

    if (!uploadCard || !fileInput) return;

    fileInput.addEventListener('click', e => e.stopPropagation());

    const browseLabel = uploadCard.querySelector('label[for="pdf-input"]');
    if (browseLabel) {
        browseLabel.addEventListener('click', e => e.stopPropagation());
    }

    uploadCard.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) setFile(fileInput.files[0]);
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
        uploadCard.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); });
    });

    uploadCard.addEventListener('dragenter', () => setHighlight(true));
    uploadCard.addEventListener('dragover',  () => setHighlight(true));
    uploadCard.addEventListener('dragleave', () => setHighlight(false));
    uploadCard.addEventListener('drop', e => {
        setHighlight(false);
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type === 'application/pdf') setFile(files[0]);
    });

    function setHighlight(on) {
        uploadCard.style.borderColor       = on ? 'var(--color-primary)' : 'var(--color-outline-variant)';
        uploadCard.style.backgroundColor   = on ? 'var(--color-surface-container)' : 'var(--color-surface-container-low)';
    }

    function setFile(file) {
        selectedFile = file;
        if (uploadDesc) {
            uploadDesc.innerHTML = `<span class="text-primary" style="font-weight:700;">${file.name}</span> พร้อมสำหรับการตรวจสอบ`;
        }
    }
}

// Checklist
function getChecklist() {
    const rows = document.querySelectorAll('#checklist-body tr');
    const checklist = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll('td.excel-cell');
        if (cells.length < 2) return;

        const titleEl = cells[0].querySelector('input, textarea');
        const title   = titleEl ? titleEl.value.trim() : '';

        // Auto-commit any text still sitting in the input field
        const pendingInput = cells[1].querySelector('.sub-item-input');
        if (pendingInput && pendingInput.value.trim()) {
            const container = cells[1].querySelector('.sub-items-container');
            if (container) {
                const val = pendingInput.value.trim();
                const scoreInput = cells[1].querySelector('.sub-item-score-input');
                const parsedScore = scoreInput ? parseFloat(scoreInput.value) : NaN;
                const score = !isNaN(parsedScore) ? parsedScore : 0;
                const chip = document.createElement('div');
                chip.className = 'sub-item-chip';
                chip.dataset.score = score;
                chip.innerHTML = `
                    <span class="sub-item-text">${val}</span>
                    <span class="sub-item-score-badge" style="background:var(--color-surface-container-highest); border-radius:10px; padding:0 4px; font-size:0.6rem; font-weight:bold; margin-left:4px;">${score}</span>
                    <span class="material-symbols-outlined remove-sub-item">close</span>
                `;
                chip.querySelector('.remove-sub-item').addEventListener('click', () => chip.remove());
                container.appendChild(chip);
                pendingInput.value = '';
                if (scoreInput) scoreInput.value = '0';
            }
        }

        const itemEls = cells[1].querySelectorAll('.sub-item-chip');
        const items   = Array.from(itemEls).map(el => {
            const parsed = parseFloat(el.dataset.score);
            return {
                name: el.querySelector('.sub-item-text').textContent.trim(),
                score: !isNaN(parsed) ? parsed : 0
            };
        }).filter(item => item.name);

        if (!title && items.length === 0) return;

        checklist.push({ title, items });
    });

    return checklist;
}

function bindSubItemEvents(row) {
    const input = row.querySelector('.sub-item-input');
    const scoreInput = row.querySelector('.sub-item-score-input');
    const btn = row.querySelector('.add-sub-item-btn');
    const container = row.querySelector('.sub-items-container');

    if (!input || !btn || !container) return;

    function addSubItem() {
        const val = input.value.trim();
        if (!val) return;
        const parsedScore = scoreInput ? parseFloat(scoreInput.value) : NaN;
        const score = !isNaN(parsedScore) ? parsedScore : 0;

        const chip = document.createElement('div');
        chip.className = 'sub-item-chip';
        chip.dataset.score = score;
        chip.innerHTML = `
            <span class="sub-item-text">${val}</span>
            <span class="sub-item-score-badge" style="background:var(--color-surface-container-highest); border-radius:10px; padding:0 4px; font-size:0.6rem; font-weight:bold; margin-left:4px;">${score}</span>
            <span class="material-symbols-outlined remove-sub-item">close</span>
        `;
        
        chip.querySelector('.remove-sub-item').addEventListener('click', () => {
            chip.remove();
        });

        container.appendChild(chip);
        input.value = '';
        if (scoreInput) scoreInput.value = '0';
    }

    btn.addEventListener('click', addSubItem);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addSubItem();
        }
    });
    if (scoreInput) {
        scoreInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSubItem();
                input.focus();
            }
        });
    }
}

function initChecklist() {
    const addRowBtn     = document.getElementById('add-row-btn');
    const checklistBody = document.getElementById('checklist-body');

    if (!addRowBtn || !checklistBody) return;

    let rowCount = checklistBody.querySelectorAll('tr').length;

    checklistBody.querySelectorAll('tr').forEach(bindSubItemEvents);

    addRowBtn.addEventListener('click', () => {
        rowCount++;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="excel-row-index">${rowCount}</td>
            <td class="excel-cell"><input type="text" placeholder="หัวข้อหลัก" value="" /></td>
            <td class="excel-cell sub-items-cell">
                <div class="sub-items-container"></div>
                <div class="add-sub-item-wrapper" style="display: flex; gap: 0.25rem; align-items: center; margin-top: 0.25rem;">
                    <input type="text" class="sub-item-input" placeholder="พิมพ์แล้วกด + หรือ Enter" style="flex: 1;" />
                    <input type="number" class="sub-item-score-input" value="0" min="0" style="width: 50px; text-align: center; border: 1px solid var(--color-outline-variant); border-radius: 4px; padding: 0.25rem;" title="คะแนน" />
                    <button type="button" class="btn-icon add-sub-item-btn" style="padding: 0.25rem; display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
                        <span class="material-symbols-outlined" style="font-size: 1.25rem;">add</span>
                    </button>
                </div>
            </td>
            <td class="excel-cell" style="text-align:center;">
                <button class="btn-icon delete-row-btn">
                    <span class="material-symbols-outlined">delete</span>
                </button>
            </td>`;
        checklistBody.appendChild(tr);
        bindSubItemEvents(tr);

        tr.querySelector('.delete-row-btn').addEventListener('click', () => {
            tr.remove();
            updateRowIndices();
        });
    });

    checklistBody.addEventListener('input', e => {
        if (e.target.tagName.toLowerCase() === 'textarea') {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        }
    });

    checklistBody.querySelectorAll('.delete-row-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            e.target.closest('tr').remove();
            updateRowIndices();
        });
    });

    function updateRowIndices() {
        rowCount = 0;
        checklistBody.querySelectorAll('tr').forEach(row => {
            rowCount++;
            const cell = row.querySelector('.excel-row-index');
            if (cell) cell.textContent = rowCount;
        });
    }
}

// Markdown renderer (for LLM reasoning output)
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function inlineMarkdown(text) {
    text = escapeHtml(text);
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    return text;
}

function parseMarkdown(text) {
    if (!text) return '';
    const lines = text.split('\n');
    let html = '';
    let inList = false;

    for (const line of lines) {
        const listMatch = line.match(/^[-•*]\s+(.+)$/);
        if (listMatch) {
            if (!inList) { html += '<ul style="margin:0.25rem 0 0 1rem;padding:0;">'; inList = true; }
            html += `<li>${inlineMarkdown(listMatch[1])}</li>`;
        } else {
            if (inList) { html += '</ul>'; inList = false; }
            if (line.trim()) html += inlineMarkdown(line);
        }
    }
    if (inList) html += '</ul>';
    return html;
}

// Verification
function setLoading(on) {
    const btn = document.getElementById('verify-btn');
    if (!btn) return;
    btn.disabled = on;
    btn.style.opacity = on ? '0.6' : '1';
    const icon = btn.querySelector('.material-symbols-outlined');
    if (icon) {
        icon.textContent = on ? 'progress_activity' : 'verified';
        if (on) {
            icon.classList.add('spinning');
        } else {
            icon.classList.remove('spinning');
        }
    }
}

function showError(msg) {
    const container = document.getElementById('result-items');
    if (container) {
        container.innerHTML = `<div class="result-item error" style="padding:1rem;">
            <div class="result-item-content">
                <span class="material-symbols-outlined text-error" style="font-variation-settings:'FILL' 1">error</span>
                <p style="font-size:0.875rem; color:var(--color-error);">${msg}</p>
            </div>
        </div>`;
    }
}

function renderResults(data) {
    const container = document.getElementById('result-items');
    const scoreEl   = document.getElementById('score-value');
    const totalScoreEl = document.getElementById('total-score-value');
    const exportBtn = document.getElementById('export-btn');

    if (scoreEl) scoreEl.textContent = `${data.similarity_score}%`;
    if (totalScoreEl && data.summary) {
        totalScoreEl.textContent = `${data.summary.passed_score} / ${data.summary.total_score}`;
    }
    if (!container) return;
    container.innerHTML = '';

    for (const section of data.results) {
        for (const item of section.items) {
            const isFail = item.status === 'fail';
            const score = item.score !== undefined ? item.score : 0;
            const div = document.createElement('div');
            div.className = `result-item${isFail ? ' error' : ''}`;
            div.innerHTML = `
                <div class="result-item-content">
                    <span class="material-symbols-outlined ${isFail ? 'text-error' : 'text-primary'}"
                        style="font-variation-settings:'FILL' 1">${isFail ? 'error' : 'check_circle'}</span>
                    <div>
                        <p class="result-item-title">${section.section} — ${item.requirement}</p>
                        <p class="result-item-sub">${parseMarkdown(isFail ? item.reasoning : (item.evidence || item.reasoning))}</p>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem;">
                    <span class="result-badge">${isFail ? 'MISSING' : 'FOUND'}</span>
                    <span class="result-score-text" style="font-size: 0.75rem; font-weight: 700; color: ${isFail ? 'var(--color-error)' : 'var(--color-primary)'};">${isFail ? `0` : `+${score}`} คะแนน</span>
                </div>`;
            container.appendChild(div);
        }
    }

    lastResult = data;
    if (exportBtn) exportBtn.style.display = 'inline-flex';
}

async function exportToExcel() {
    if (!lastResult) return;
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) exportBtn.disabled = true;
    try {
        const payload = {
            filename: getSelectedFile()?.name || 'document.pdf',
            ...lastResult,
        };
        const res = await fetch('/export/excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('ส่งออกไม่สำเร็จ');
        const blob = await res.blob();
        const disposition = res.headers.get('Content-Disposition') || '';
        let fname = 'ผลการตรวจสอบ.xlsx';
        const match = disposition.match(/filename\*=UTF-8''(.+)/i);
        if (match) fname = decodeURIComponent(match[1]);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fname;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert(err.message);
    } finally {
        if (exportBtn) exportBtn.disabled = false;
    }
}

async function runVerification() {
    const file = getSelectedFile();
    if (!file) { showError('Please upload a PDF document first.'); return; }

    const checklist = getChecklist();
    if (checklist.length === 0) { showError('Please add at least one checklist item.'); return; }

    setLoading(true);
    lastResult = null;
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) exportBtn.style.display = 'none';
    try {
        const form = new FormData();
        form.append('file', file);
        form.append('checklist', JSON.stringify(checklist));

        const res = await fetch('/analyze', { method: 'POST', body: form });
        if (!res.ok) {
            const detail = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(detail.detail || res.statusText);
        }
        renderResults(await res.json());
    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

// Init
initUpload();
initChecklist();
document.getElementById('verify-btn').addEventListener('click', runVerification);
document.getElementById('export-btn').addEventListener('click', exportToExcel);
