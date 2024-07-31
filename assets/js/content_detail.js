// Assistant Selection change event
document.addEventListener("DOMContentLoaded", function() {
    const roleSelect = document.querySelector("#id_name");
    const instructionsBox = document.querySelector("#id_instructions");
    const assistantField = document.querySelector("#id_assistant");

    roleSelect.addEventListener("change", function() {
        const selectedAssistantId = this.value;
        fetch(`/content/get-assistants/?assistant_id=${selectedAssistantId}`)
            .then(response => response.json())
            .then(data => {
                instructionsBox.value = data.instructions;
                assistantField.value = selectedAssistantId; // Update the assistant field with the selected ID
            })
            .catch(error => console.error('Error fetching assistants:', error));
    });
});

// Edit content functionality
document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', function() {
        const contentId = this.getAttribute('data-content-id');
        const formType = this.getAttribute('data-form-type'); // Get the form type (content or content-detail)
        const form = document.getElementById(`${formType}-form-${contentId}`);
        if (form) {
            // Enable form fields for editing
            form.querySelectorAll('input, textarea').forEach(input => {
                if (input.id !== 'content-textarea' && input.id !== 'prompt-textarea') {
                    input.removeAttribute('readonly');
                }
            });

            // Adjust button visibility
            this.style.display = 'none'; // Hide edit button
            form.querySelector('.save-btn').style.display = 'inline'; // Show save button
            form.querySelector('.cancel-btn').style.display = 'inline'; // Show cancel button
        } else {
            console.error('Form not found for contentId:', contentId);
        }
    });
});

// Cancel edit functionality
document.querySelectorAll('.cancel-btn').forEach(button => {
    button.addEventListener('click', function() {
        const contentId = this.previousElementSibling.getAttribute('data-content-id');
        const formType = this.previousElementSibling.getAttribute('data-form-type'); // Get the form type (content or content-detail)
        const form = document.getElementById(`${formType}-form-${contentId}`);
        if (form) {
            // Disable form fields to prevent editing
            form.querySelectorAll('input, textarea').forEach(input => {
                input.setAttribute('readonly', 'readonly');
            });

            // Adjust button visibility
            this.style.display = 'none'; // Hide cancel button
            form.querySelector('.save-btn').style.display = 'none'; // Hide save button
            form.querySelector('.edit-btn').style.display = 'inline'; // Show edit button
        } else {
            console.error('Form not found for contentId:', contentId);
        }
    });
});

// Save content functionality
document.querySelectorAll('.save-btn').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default form submission
        const contentId = this.getAttribute('data-content-id');
        const formType = this.getAttribute('data-form-type'); // Get the form type (content or content-detail)
        const form = document.getElementById(`${formType}-form-${contentId}`);
        if (form) {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            data['formType'] = formType; // Add formType to the data

            // Send Data to Server
            fetch(`/content/update/${contentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') // Function to get CSRF token from cookies
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Assuming the server responds with JSON
            })
            .then(data => {
                // Handle Server Response
                console.log('Success:', data);
                alert('Content saved successfully!');
                location.reload(); // Optionally reload the page to show the updated content
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error saving content. Please try again.');
            });
        } else {
            console.error('Form not found for contentId:', contentId);
        }
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