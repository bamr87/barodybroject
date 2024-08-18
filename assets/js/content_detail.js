// Assistant Selection change event
document.addEventListener("DOMContentLoaded", function() {
    const roleSelect = document.querySelector("#id_name_list");
    const instructionsBox = document.querySelector("#id_assist_instructions");
    const assistantField = document.querySelector("#id_assistant");

    roleSelect.addEventListener("change", function() {
        const selectedAssistantId = this.value;
        fetch(`/get_assistant_details/?assistant_id=${selectedAssistantId}`)
            .then(response => response.json())
            .then(data => {
                instructionsBox.value = data.instructions;
                assistantField.value = selectedAssistantId; // Update the assistant field with the selected ID
            })
            .catch(error => console.error('Error fetching assistants:', error));
    });
});

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