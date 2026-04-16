// checklist.js

/**
 * Read the current state of the checklist table and return it as the JSON
 * payload expected by POST /analyze.
 *
 * Each row maps to:  { title: string, items: string[] }
 * Sub-items are comma-separated inside the single "Required Sub-items" cell.
 */
function getChecklist() {
    const rows = document.querySelectorAll('#checklist-body tr');
    const checklist = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll('td.excel-cell');
        if (cells.length < 2) return;

        const titleEl = cells[0].querySelector('input, textarea');
        const itemsEl = cells[1].querySelector('input, textarea');

        const title = titleEl ? titleEl.value.trim() : '';
        const rawItems = itemsEl ? itemsEl.value.trim() : '';

        if (!title && !rawItems) return;

        const items = rawItems
            .split(',')
            .map(s => s.trim())
            .filter(Boolean);

        checklist.push({ title, items });
    });

    return checklist;
}

function initChecklist() {
    const addRowBtn = document.getElementById('add-row-btn');
    const checklistBody = document.getElementById('checklist-body');
    let rowCount = 3; // 3 rows are pre-filled in the HTML

    if (!addRowBtn || !checklistBody) return;

    addRowBtn.addEventListener('click', () => {
        rowCount++;
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td class="excel-row-index">${rowCount}</td>
            <td class="excel-cell">
                <textarea rows="1" placeholder="New Category"></textarea>
            </td>
            <td class="excel-cell">
                <textarea rows="1" placeholder="New Sub-items"></textarea>
            </td>
            <td class="excel-cell" style="text-align: center;">
                <button class="btn-icon delete-row-btn">
                    <span class="material-symbols-outlined" data-icon="delete">delete</span>
                </button>
            </td>
        `;
        checklistBody.appendChild(tr);

        // Attach event listener to new delete button
        const newDeleteBtn = tr.querySelector('.delete-row-btn');
        if (newDeleteBtn) {
            newDeleteBtn.addEventListener('click', () => {
                tr.remove();
                updateRowIndices();
            });
        }
    });

    // Auto-resize textareas within checklist body
    checklistBody.addEventListener('input', (e) => {
        if (e.target.tagName.toLowerCase() === 'textarea') {
            e.target.style.height = 'auto';
            e.target.style.height = (e.target.scrollHeight) + 'px';
        }
    });

    // Initial resize for pre-filled textareas
    setTimeout(() => {
        checklistBody.querySelectorAll('textarea').forEach(ta => {
            ta.style.height = 'auto';
            ta.style.height = (ta.scrollHeight) + 'px';
        });
    }, 0);

    // Attach to existing delete buttons
    const deleteBtns = checklistBody.querySelectorAll('.delete-row-btn');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const row = e.target.closest('tr');
            if (row) {
                row.remove();
                updateRowIndices();
            }
        });
    });

    function updateRowIndices() {
        const rows = checklistBody.querySelectorAll('tr');
        rowCount = 0;
        rows.forEach(row => {
            rowCount++;
            const indexCell = row.querySelector('.excel-row-index');
            if (indexCell) {
                indexCell.textContent = rowCount;
            }
        });
    }
}
