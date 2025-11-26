/**
 * File: content_detail.js
 * Description: Dynamic content loading and form handling with vanilla JavaScript
 * Author: Barodybroject Team <team@example.com>
 * Created: 2025-01-15
 * Last Modified: 2025-11-25
 * Version: 2.0.0
 * 
 * Dependencies:
 * - None (vanilla JavaScript, no jQuery)
 * 
 * Usage: Include in content detail template
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    // Assistant selection handler - migrated from jQuery to Fetch API
    const assistantSelect = document.getElementById('id_assistant');
    if (assistantSelect) {
        assistantSelect.addEventListener('change', function() {
            const assistantId = this.value;
            if (assistantId) {
                fetch(`/get_assistant_details/${assistantId}/`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const instructionsField = document.getElementById('id_instructions');
                    if (data.instructions && instructionsField) {
                        instructionsField.value = data.instructions;
                    }
                })
                .catch(error => {
                    console.error('Error fetching instructions:', error);
                    alert('Error fetching instructions');
                });
            }
        });
    }

    // Function to handle sorting
    function sortTable(table, column, order) {
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const type = table.querySelector(`thead th:nth-child(${column + 1})`).dataset.type;

        rows.sort((a, b) => {
            const aText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            const bText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();

            if (type === 'number') {
                return order === 'asc' ? aText - bText : bText - aText;
            } else if (type === 'date') {
                return order === 'asc' ? new Date(aText) - new Date(bText) : new Date(bText) - new Date(aText);
            } else {
                return order === 'asc' ? aText.localeCompare(bText) : bText.localeCompare(aText);
            }
        });

        rows.forEach(row => table.querySelector('tbody').appendChild(row));
    }

    // Function to handle filtering
    function filterTable(table, column, query) {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cellText = row.querySelector(`td:nth-child(${column + 1})`).textContent.trim().toLowerCase();
            row.style.display = cellText.includes(query.toLowerCase()) ? '' : 'none';
        });
    }

    // Attach event listeners to column headers for sorting
    document.querySelectorAll('th.sortable').forEach((header, index) => {
        header.addEventListener('click', () => {
            const table = header.closest('table');
            const order = header.dataset.order === 'asc' ? 'desc' : 'asc';
            header.dataset.order = order;
            sortTable(table, index, order);
        });
    });

    // Attach event listeners to filter input fields for filtering
    document.querySelectorAll('input.filter').forEach((input, index) => {
        input.addEventListener('input', () => {
            const table = input.closest('table');
            filterTable(table, index, input.value);
        });
    });
});
