// table_utils.js
// Provides sorting and filtering functionality for tables

document.addEventListener('DOMContentLoaded', () => {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        table.querySelectorAll('th.sortable').forEach((header, index) => {
            header.addEventListener('click', () => {
                const newOrder = header.dataset.order === 'asc' ? 'desc' : 'asc';
                header.dataset.order = newOrder;
                sortTable(table, index, newOrder);
            });
        });

        table.querySelectorAll('input.filter').forEach((input, index) => {
            input.addEventListener('input', () => {
                filterTable(table, index, input.value);
            });
        });
    });
});

function sortTable(table, columnIndex, order) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const type = table.querySelector(`thead th:nth-child(${columnIndex + 1})`).dataset.type;
    rows.sort((a, b) => {
        const aText = a.querySelector(`td:nth-child(${columnIndex + 1})`).textContent.trim();
        const bText = b.querySelector(`td:nth-child(${columnIndex + 1})`).textContent.trim();
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
        const cellText = row.querySelector(`td:nth-child(${columnIndex + 1})`).textContent.trim();
        row.style.display = cellText.toLowerCase().includes(query.toLowerCase()) ? '' : 'none';
    });
}