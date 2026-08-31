// table_utils.js
// Provides sorting and filtering functionality for tables

document.addEventListener('DOMContentLoaded', () => {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th.sortable');
        headers.forEach(header => {
            header.addEventListener('click', event => {
                // The column's filter input lives inside this header. Clicking it
                // (or dragging to select its text) must focus/edit the input, not
                // re-sort the column.
                if (event.target.closest('input, textarea, select, label')) {
                    return;
                }

                const columnIndex = header.cellIndex;
                const newOrder = header.dataset.order === 'asc' ? 'desc' : 'asc';

                // Only one column is sorted at a time — clear the others so their
                // aria-sort doesn't lie and so returning to one starts from asc.
                headers.forEach(other => {
                    if (other !== header) {
                        delete other.dataset.order;
                        other.setAttribute('aria-sort', 'none');
                    }
                });

                header.dataset.order = newOrder;
                header.setAttribute('aria-sort', newOrder === 'asc' ? 'ascending' : 'descending');
                sortTable(table, columnIndex, newOrder);
            });
        });

        table.querySelectorAll('input.filter').forEach(input => {
            // filterTable re-reads every filter, so one handler per input is
            // enough and the column this input belongs to is worked out there.
            input.addEventListener('input', () => filterTable(table));
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


// Every active column filter, as {columnIndex, query}. Blank inputs are dropped
// so they impose no constraint.
function activeFilters(table) {
    return Array.from(table.querySelectorAll('input.filter'))
        .map(input => ({
            columnIndex: input.closest('th')?.cellIndex,
            query: input.value.trim().toLowerCase(),
        }))
        .filter(({ columnIndex, query }) => query !== '' && columnIndex !== undefined);
}

// Re-evaluate the whole table against ALL of its filters at once.
//
// Reading every filter on each keystroke — rather than only the one that just
// changed — is what makes several active filters combine (a row must match all
// of them) and what makes CLEARING one filter re-apply the rest instead of
// revealing rows the others still exclude.
function filterTable(table) {
    const body = table.querySelector('tbody');
    if (!body) {
        return;
    }

    const filters = activeFilters(table);
    const noMatchRow = body.querySelector('tr[data-filter-empty]');
    let dataRows = 0;
    let matches = 0;

    Array.from(body.rows).forEach(row => {
        // The filter-empty row is a message about the table, not a row of it.
        if (row === noMatchRow) {
            return;
        }

        // The server-side "No items found" row — a single cell spanning the
        // table. Not data, so it is never filtered away.
        if (row.cells.length === 1 && row.cells[0].colSpan > 1) {
            row.style.display = '';
            return;
        }

        dataRows += 1;
        const visible = filters.every(({ columnIndex, query }) => {
            const cell = row.cells[columnIndex];
            // A row with no cell in that column cannot contradict the filter.
            return !cell || cell.textContent.trim().toLowerCase().includes(query);
        });

        row.style.display = visible ? '' : 'none';
        if (visible) {
            matches += 1;
        }
    });

    if (noMatchRow) {
        // Only when the table HAS rows and the filters have hidden all of them.
        // With no rows at all the server's own empty state is already saying
        // so, and showing both would be two empty states stacked.
        const filteredToNothing = filters.length > 0 && dataRows > 0 && matches === 0;
        noMatchRow.style.display = filteredToNothing ? '' : 'none';
    }
}
