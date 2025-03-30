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

$(document).ready(function() {
    $('#id_assistant').change(function() {
        var assistantId = $(this).val();
        if (assistantId) {
            $.ajax({
                url: '/get_assistant_details/' + assistantId + '/',
                method: 'GET',
                success: function(data) {
                    if (data.instructions) {
                        $('#id_instructions').val(data.instructions);
                    }
                },
                error: function() {
                    alert('Error fetching instructions');
                }
            });
        }
    });

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
