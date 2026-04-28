// table_utils.js
// Provides sorting and filtering functionality for tables

document.addEventListener('DOMContentLoaded', () => {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        table.querySelectorAll('th.sortable').forEach(header => {
            header.addEventListener('click', () => {
                const columnIndex = header.cellIndex;
                const newOrder = header.dataset.order === 'asc' ? 'desc' : 'asc';
                header.dataset.order = newOrder;
                sortTable(table, columnIndex, newOrder);
            });
        });

        table.querySelectorAll('input.filter').forEach(input => {
            input.addEventListener('input', () => {
                const header = input.closest('th');
                if (!header) {
                    return;
                }

                filterTable(table, header.cellIndex, input.value);
            });
        });
    });
});

function sortTable(table, columnIndex, order) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const type = table.querySelector(`thead th:nth-child(${columnIndex + 1})`)?.dataset.type;
    rows.sort((a, b) => {
        const aCell = a.querySelector(`td:nth-child(${columnIndex + 1})`);
        const bCell = b.querySelector(`td:nth-child(${columnIndex + 1})`);
        const aText = aCell?.textContent.trim() || '';
        const bText = bCell?.textContent.trim() || '';
        if (type === 'number') {
            return order === 'asc' ? aText - bText : bText - aText;
        } else if (type === 'date') {
            return order === 'asc'
                ? new Date(aText) - new Date(bText)
                : new Date(bText) - new Date(aText);
        }
        return order === 'asc'
            ? aText.localeCompare(bText)
            : bText.localeCompare(aText);
    });
    rows.forEach(row => table.querySelector('tbody').appendChild(row));
}


function filterTable(table, columnIndex, query) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    rows.forEach(row => {
        if (row.cells.length === 1 && row.cells[0].colSpan > 1) {
            row.style.display = '';
            return;
        }

        const cell = row.querySelector(`td:nth-child(${columnIndex + 1})`);
        if (!cell) {
            row.style.display = '';
            return;
        }

        const cellText = cell.textContent.trim();
        row.style.display = cellText.toLowerCase().includes(query.toLowerCase()) ? '' : 'none';
    });
}