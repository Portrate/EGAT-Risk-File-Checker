function addSubItemChip(container, text) {
    const chip = document.createElement('div');
    chip.className = 'sub-item-chip';
    chip.innerHTML = `
        <span class="sub-item-text">${text}</span>
        <span class="material-symbols-outlined remove-sub-item" data-icon="close">close</span>
    `;
    chip.querySelector('.remove-sub-item').addEventListener('click', () => chip.remove());
    container.appendChild(chip);
}

function wireSubItemInput(row) {
    const container = row.querySelector('.sub-items-container');
    const input = row.querySelector('.sub-item-input');
    const addBtn = row.querySelector('.add-sub-item-btn');

    function commit() {
        const val = input.value.trim();
        if (val) {
            addSubItemChip(container, val);
            input.value = '';
        }
        input.focus();
    }

    addBtn.addEventListener('click', commit);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            commit();
        }
    });
}

function buildNewRow(rowNumber) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td class="excel-row-index">${rowNumber}</td>
        <td class="excel-cell">
            <input type="text" placeholder="หัวข้อหลัก" />
        </td>
        <td class="excel-cell sub-items-cell">
            <div class="sub-items-container"></div>
            <div class="add-sub-item-wrapper" style="display: flex; gap: 0.25rem; align-items: center; margin-top: 0.25rem;">
                <input type="text" class="sub-item-input" placeholder="พิมพ์แล้วกด + หรือ Enter" style="flex: 1;" />
                <button type="button" class="btn-icon add-sub-item-btn" style="padding: 0.25rem; display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
                    <span class="material-symbols-outlined" style="font-size: 1.25rem;" data-icon="add">add</span>
                </button>
            </div>
        </td>
        <td class="excel-cell" style="text-align: center; vertical-align: top; padding-top: 0.5rem;">
            <button class="btn-icon delete-row-btn">
                <span class="material-symbols-outlined" data-icon="delete">delete</span>
            </button>
        </td>
    `;
    return tr;
}

function getChecklist() {
    const rows = document.querySelectorAll('#checklist-body tr');
    const checklist = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll('td.excel-cell');
        if (cells.length < 2) return;

        const titleEl = cells[0].querySelector('input');
        const title = titleEl ? titleEl.value.trim() : '';

        const chips = cells[1].querySelectorAll('.sub-item-chip .sub-item-text');
        const items = Array.from(chips).map(c => c.textContent.trim()).filter(Boolean);

        if (!title && items.length === 0) return;

        checklist.push({ title, items });
    });

    return checklist;
}

function initChecklist() {
    const addRowBtn = document.getElementById('add-row-btn');
    const checklistBody = document.getElementById('checklist-body');

    if (!addRowBtn || !checklistBody) return;

    function updateRowIndices() {
        checklistBody.querySelectorAll('tr').forEach((row, i) => {
            const indexCell = row.querySelector('.excel-row-index');
            if (indexCell) indexCell.textContent = i + 1;
        });
    }

    // Wire the initial row (already in HTML)
    const initialRow = checklistBody.querySelector('tr');
    if (initialRow) {
        wireSubItemInput(initialRow);
        initialRow.querySelector('.delete-row-btn').addEventListener('click', () => {
            initialRow.remove();
            updateRowIndices();
        });
    }

    // Add new row
    addRowBtn.addEventListener('click', () => {
        const rowNumber = checklistBody.querySelectorAll('tr').length + 1;
        const tr = buildNewRow(rowNumber);

        wireSubItemInput(tr);
        tr.querySelector('.delete-row-btn').addEventListener('click', () => {
            tr.remove();
            updateRowIndices();
        });

        checklistBody.appendChild(tr);
    });
}
