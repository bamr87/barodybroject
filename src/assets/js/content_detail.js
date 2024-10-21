
// Function to get CSRF token from cookies (needed for Django)
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
});