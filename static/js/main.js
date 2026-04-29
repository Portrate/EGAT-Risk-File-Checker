// selectedFile: the PDF the user chose.
// lastResult:   the last result from /analyze, saved so the export button can use it again.
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
                const score = !isNaN(parsedScore) ? Math.max(0, parsedScore) : 0;
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
                score: !isNaN(parsed) ? Math.max(0, parsed) : 0
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
        const score = !isNaN(parsedScore) ? Math.max(0, parsedScore) : 0;

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
        // Recompute from the DOM so presets loaded after init don't desync the counter
        rowCount = checklistBody.querySelectorAll('tr').length + 1;
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

// The AI sometimes returns text with simple markdown formatting.
// These helpers turn that text into safe HTML to show in the results panel.

// Replace special characters so the browser does not treat them as HTML tags.
function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// Turn **bold** and *italic* markers into real HTML tags.
function inlineMarkdown(text) {
    text = escapeHtml(text);
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    return text;
}

// Convert a multi-line text to HTML. Handles bullet lists and bold/italic only,
// since the AI rarely uses anything more complex.
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

// Grey out the verify button and lock the entire UI while waiting for a result.
function setLoading(on) {
    const btn = document.getElementById('verify-btn');
    if (!btn) return;
    btn.disabled = on;
    btn.style.opacity = on ? '0.6' : '1';
    const icon = btn.querySelector('.material-symbols-outlined');
    if (icon) {
        icon.textContent = on ? 'progress_activity' : 'verified';
        if (on) icon.classList.add('spinning');
        else icon.classList.remove('spinning');
    }

    // Lock every interactive element outside the verify button
    const selectors = [
        '#upload-card',
        '#pdf-input',
        '#model-select',
        '#api-key-input',
        '#add-row-btn',
        '#export-btn',
        '#add-model-btn',
        '#save-preset-btn',
        '#delete-preset-btn',
        '#preset-select',
        '#checklist-body input',
        '#checklist-body button',
        '#checklist-body .remove-sub-item',
    ];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            if (el === btn) return;
            if (on) {
                el.dataset._wasDisabled = el.disabled ? '1' : '0';
                el.disabled = true;
                el.style.pointerEvents = 'none';
                el.style.opacity = '0.5';
            } else {
                if (el.dataset._wasDisabled !== '1') el.disabled = false;
                el.style.pointerEvents = '';
                el.style.opacity = '';
                delete el.dataset._wasDisabled;
            }
        });
    });

    // Overlay on the upload card (not a form element, so needs pointer-events)
    const uploadCard = document.getElementById('upload-card');
    if (uploadCard) {
        uploadCard.style.pointerEvents = on ? 'none' : '';
        uploadCard.style.opacity = on ? '0.5' : '';
    }
}

// Show an error message inside the results area instead of a popup alert.
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

// Fill the results panel with pass/fail cards from the /analyze response.
// Passed items show the evidence quote; failed items show why they were missing.
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
    // Only show the export button after results are ready.
    if (exportBtn) exportBtn.style.display = 'inline-flex';
}

// Send the last result to /export/excel and start a file download in the browser.
// The filename comes from the server header so Thai characters are handled correctly.
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
        // Use a hidden <a> tag to start the download, then free the temporary URL.
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

let timerInterval = null;
let startTime = 0;

function startTimer() {
    const timerDisplay = document.getElementById('timer-display');
    const timeElapsed = document.getElementById('time-elapsed');
    if (timerDisplay) timerDisplay.style.display = 'flex';
    
    startTime = Date.now();
    
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const totalSeconds = Math.floor(elapsed / 1000);
        const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
        const seconds = String(totalSeconds % 60).padStart(2, '0');
        if (timeElapsed) timeElapsed.textContent = `${minutes}:${seconds}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// Check that a file and checklist exist, then send them to /analyze and show the results.
async function runVerification() {
    const checklist = getChecklist();
    if (checklist.length === 0) { showError('กรุณาเพิ่มหัวข้อหลักและรายการย่อยอย่างน้อย 1 รายการ'); return; }

    const noTitle = checklist.find(s => !s.title);
    if (noTitle) { showError('กรุณากรอกชื่อหัวข้อหลักให้ครบทุกแถว'); return; }

    const emptySection = checklist.find(s => s.items.length === 0);
    if (emptySection) {
        showError(`หัวข้อ "${emptySection.title}" ยังไม่มีรายการย่อย กรุณาเพิ่มรายการย่อยอย่างน้อย 1 รายการ`);
        return;
    }

    const file = getSelectedFile();
    if (!file) { showError('กรุณาอัปโหลดไฟล์ PDF ก่อน'); return; }

    setLoading(true);
    startTimer();
    lastResult = null;
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) exportBtn.style.display = 'none';
    try {
        const form = new FormData();
        form.append('file', file);
        form.append('checklist', JSON.stringify(checklist));

        const modelSelect = document.getElementById('model-select');
        const apiKeyInput = document.getElementById('api-key-input');
        const selectedModel = modelSelect ? modelSelect.value : '';
        if (selectedModel) form.append('model', selectedModel);

        const isCloud = selectedModel.startsWith('gemini') || selectedModel.startsWith('gpt');
        if (isCloud) {
            const apiKey = apiKeyInput ? apiKeyInput.value.trim() : '';
            if (!apiKey) { setLoading(false); stopTimer(); showError('กรุณากรอก API Key สำหรับโมเดลที่เลือก'); return; }
            form.append('api_key', apiKey);
        }

        const res = await fetch('/analyze', { method: 'POST', body: form });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            // Backend already returns Thai messages as a string; pydantic 422 returns an array — replace with a friendly Thai message
            let msg;
            if (typeof data.detail === 'string') {
                msg = data.detail;
            } else if (res.status === 422) {
                msg = 'ข้อมูลรายการตรวจสอบไม่ถูกต้อง กรุณาตรวจสอบหัวข้อหลักและรายการย่อยให้ครบถ้วน';
            } else if (res.status === 502) {
                msg = 'ไม่สามารถเชื่อมต่อกับโมเดล AI ได้ กรุณาตรวจสอบสถานะของ Ollama หรือ API Key';
            } else {
                msg = 'เกิดข้อผิดพลาดในการตรวจสอบเอกสาร กรุณาลองใหม่อีกครั้ง';
            }
            throw new Error(msg);
        }
        renderResults(await res.json());
    } catch (err) {
        // Network/parse failures fall through here — show a generic Thai message rather than raw exception text
        const msg = err.message && /[฀-๿]/.test(err.message)
            ? err.message
            : 'เกิดข้อผิดพลาดในการตรวจสอบเอกสาร กรุณาลองใหม่อีกครั้ง';
        showError(msg);
    } finally {
        setLoading(false);
        stopTimer();
    }
}

function initModelSelect() {
    const modelSelect = document.getElementById('model-select');
    const apiKeyRow = document.getElementById('api-key-row');
    const deleteBtn = document.getElementById('delete-model-btn');
    if (!modelSelect || !apiKeyRow) return;

    function updateApiKeyVisibility() {
        const val = modelSelect.value;
        const isCloud = val.startsWith('gemini') || val.startsWith('gpt');
        apiKeyRow.style.display = isCloud ? 'block' : 'none';
    }

    function updateDeleteButtonVisibility() {
        if (!deleteBtn) return;
        const opt = modelSelect.selectedOptions[0];
        const isCustom = opt && opt.dataset.custom === '1';
        deleteBtn.style.display = isCustom ? 'flex' : 'none';
    }

    modelSelect.addEventListener('change', () => {
        updateApiKeyVisibility();
        updateDeleteButtonVisibility();
    });

    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            const opt = modelSelect.selectedOptions[0];
            if (!opt || opt.dataset.custom !== '1') return;
            const value = opt.value;
            const label = opt.textContent.replace(' (เพิ่มเอง)', '');
            if (!window.confirm(`ลบโมเดล "${label}" หรือไม่?`)) return;

            const list = readCustomModels().filter(m => m.value !== value);
            writeCustomModels(list);
            loadCustomModels();
            // Reset selection to the first available option
            modelSelect.selectedIndex = 0;
            modelSelect.dispatchEvent(new Event('change'));
        });
    }

    loadCustomModels();
    updateApiKeyVisibility();
    updateDeleteButtonVisibility();
}

// Presets: a saved checklist under a user-chosen name. Persisted in localStorage.
const PRESETS_KEY = 'checklistPresets';

function readPresets() {
    try {
        const raw = localStorage.getItem(PRESETS_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch {
        return {};
    }
}

function writePresets(map) {
    localStorage.setItem(PRESETS_KEY, JSON.stringify(map));
}

function refreshPresetDropdown(selectedName = '') {
    const sel = document.getElementById('preset-select');
    const delBtn = document.getElementById('delete-preset-btn');
    if (!sel) return;
    const presets = readPresets();
    const names = Object.keys(presets).sort((a, b) => a.localeCompare(b, 'th'));
    sel.innerHTML = '<option value="">— เลือก Preset —</option>' +
        names.map(n => `<option value="${escapeHtml(n)}">${escapeHtml(n)}</option>`).join('');
    if (selectedName && presets[selectedName]) sel.value = selectedName;
    if (delBtn) delBtn.style.display = sel.value ? 'inline-flex' : 'none';
}

function renderChecklist(checklist) {
    const body = document.getElementById('checklist-body');
    if (!body) return;
    body.innerHTML = '';

    const sections = (checklist && checklist.length) ? checklist : [{ title: '', items: [] }];

    sections.forEach((section, idx) => {
        const tr = document.createElement('tr');
        const chipsHtml = (section.items || []).map(it => {
            const score = !isNaN(parseFloat(it.score)) ? Math.max(0, parseFloat(it.score)) : 0;
            return `<div class="sub-item-chip" data-score="${score}">
                <span class="sub-item-text">${escapeHtml(it.name || '')}</span>
                <span class="sub-item-score-badge" style="background:var(--color-surface-container-highest); border-radius:10px; padding:0 4px; font-size:0.6rem; font-weight:bold; margin-left:4px;">${score}</span>
                <span class="material-symbols-outlined remove-sub-item">close</span>
            </div>`;
        }).join('');

        tr.innerHTML = `
            <td class="excel-row-index">${idx + 1}</td>
            <td class="excel-cell"><input type="text" placeholder="หัวข้อหลัก" value="${escapeHtml(section.title || '')}" /></td>
            <td class="excel-cell sub-items-cell">
                <div class="sub-items-container">${chipsHtml}</div>
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
        body.appendChild(tr);
        bindSubItemEvents(tr);
        // Re-bind chip remove buttons for the chips we just rendered
        tr.querySelectorAll('.sub-item-chip .remove-sub-item').forEach(btn => {
            btn.addEventListener('click', () => btn.closest('.sub-item-chip').remove());
        });
        tr.querySelector('.delete-row-btn').addEventListener('click', () => {
            tr.remove();
            // Re-number remaining rows
            document.querySelectorAll('#checklist-body tr').forEach((row, i) => {
                const cell = row.querySelector('.excel-row-index');
                if (cell) cell.textContent = i + 1;
            });
        });
    });
}

function initPresets() {
    const sel = document.getElementById('preset-select');
    const saveBtn = document.getElementById('save-preset-btn');
    const delBtn = document.getElementById('delete-preset-btn');
    if (!sel || !saveBtn || !delBtn) return;

    refreshPresetDropdown();

    sel.addEventListener('change', () => {
        delBtn.style.display = sel.value ? 'inline-flex' : 'none';
        if (!sel.value) return;
        const presets = readPresets();
        const data = presets[sel.value];
        if (data) renderChecklist(data);
    });

    saveBtn.addEventListener('click', () => {
        const current = getChecklist();
        if (current.length === 0) {
            showError('ยังไม่มีรายการตรวจสอบให้บันทึก');
            return;
        }
        const presets = readPresets();
        const defaultName = sel.value || '';
        const name = window.prompt('ตั้งชื่อ Preset:', defaultName);
        if (!name) return;
        const trimmed = name.trim();
        if (!trimmed) return;
        if (presets[trimmed] && !window.confirm(`มี Preset "${trimmed}" อยู่แล้ว ต้องการเขียนทับหรือไม่?`)) return;
        presets[trimmed] = current;
        writePresets(presets);
        refreshPresetDropdown(trimmed);
    });

    delBtn.addEventListener('click', () => {
        if (!sel.value) return;
        if (!window.confirm(`ลบ Preset "${sel.value}" หรือไม่?`)) return;
        const presets = readPresets();
        delete presets[sel.value];
        writePresets(presets);
        refreshPresetDropdown();
    });
}

// Custom models stored as [{ provider: 'openai'|'gemini', value, label }]
const CUSTOM_MODELS_KEY = 'customModels';

function readCustomModels() {
    try {
        const raw = localStorage.getItem(CUSTOM_MODELS_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function writeCustomModels(list) {
    localStorage.setItem(CUSTOM_MODELS_KEY, JSON.stringify(list));
}

function loadCustomModels() {
    const modelSelect = document.getElementById('model-select');
    if (!modelSelect) return;

    // Clear any previously injected custom <option>s
    modelSelect.querySelectorAll('option[data-custom="1"]').forEach(o => o.remove());

    const openaiGroup = document.getElementById('openai-group');
    const geminiGroup = document.getElementById('gemini-group');
    const customs = readCustomModels();

    for (const m of customs) {
        const opt = document.createElement('option');
        opt.value = m.value;
        opt.textContent = `${m.label || m.value} (เพิ่มเอง)`;
        opt.dataset.custom = '1';
        const target = m.provider === 'gemini' ? geminiGroup : openaiGroup;
        if (target) target.appendChild(opt);
    }
}

function initAddModelDialog() {
    const btn = document.getElementById('add-model-btn');
    const dialog = document.getElementById('add-model-dialog');
    const provider = document.getElementById('add-model-provider');
    const nameInput = document.getElementById('add-model-name');
    const labelInput = document.getElementById('add-model-label');
    const errorEl = document.getElementById('add-model-error');
    const cancelBtn = document.getElementById('add-model-cancel');
    const saveBtn = document.getElementById('add-model-save');
    const modelSelect = document.getElementById('model-select');
    if (!btn || !dialog) return;

    function showError(msg) {
        if (!errorEl) return;
        errorEl.textContent = msg;
        errorEl.style.display = msg ? 'block' : 'none';
    }

    function open() {
        nameInput.value = '';
        labelInput.value = '';
        provider.value = 'openai';
        showError('');
        dialog.style.display = 'flex';
        nameInput.focus();
    }

    function close() {
        dialog.style.display = 'none';
    }

    btn.addEventListener('click', open);
    cancelBtn.addEventListener('click', close);
    dialog.addEventListener('click', (e) => { if (e.target === dialog) close(); });

    saveBtn.addEventListener('click', () => {
        const value = nameInput.value.trim();
        const label = labelInput.value.trim();
        const prov = provider.value;
        if (!value) { showError('กรุณากรอกชื่อโมเดล'); return; }

        // Backend routes by prefix: gpt-* → OpenAI, gemini* → Gemini.
        // Enforce a matching prefix so the request goes to the right provider.
        if (prov === 'openai' && !value.startsWith('gpt') && !value.startsWith('o1') && !value.startsWith('o3')) {
            showError('ชื่อโมเดล OpenAI ต้องขึ้นต้นด้วย gpt, o1 หรือ o3');
            return;
        }
        if (prov === 'gemini' && !value.startsWith('gemini')) {
            showError('ชื่อโมเดล Gemini ต้องขึ้นต้นด้วย gemini');
            return;
        }

        const list = readCustomModels();
        if (list.some(m => m.value === value) || modelSelect.querySelector(`option[value="${CSS.escape(value)}"]:not([data-custom="1"])`)) {
            showError('มีโมเดลนี้อยู่แล้ว');
            return;
        }

        list.push({ provider: prov, value, label });
        writeCustomModels(list);
        loadCustomModels();
        modelSelect.value = value;
        modelSelect.dispatchEvent(new Event('change'));
        close();
    });
}

// Start everything when the page loads
initUpload();
initChecklist();
initModelSelect();
initAddModelDialog();
initPresets();
document.getElementById('verify-btn').addEventListener('click', runVerification);
document.getElementById('export-btn').addEventListener('click', exportToExcel);
