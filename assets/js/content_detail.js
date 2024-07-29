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
        // Step 1: Fetch raw data from the server
        fetch(`/get-raw-content?id=${contentId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text(); // Assuming the server returns raw text
            })
            .then(rawData => {
                // Find the div that will hold the editable textarea
                const contentDiv = document.querySelector(`div[data-content-id="${contentId}"]`);
                if (contentDiv) {
                    // Step 2: Create and configure the textarea
                    const editableText = document.createElement('textarea');
                    editableText.classList.add('form-control');
                    editableText.id = `editable-content-${contentId}`;
                    editableText.style.resize = 'none'; // Prevent resizing
                    editableText.style.width = '100%'; // Full width
                    editableText.style.height = '200px'; // Fixed height, adjust as needed
                    editableText.value = rawData; // Populate with raw data from the server

                    // Clear the contentDiv and append the textarea
                    contentDiv.innerHTML = '';
                    contentDiv.appendChild(editableText);

                    // Step 3: Adjust button visibility
                    this.style.display = 'none'; // Hide edit button
                    this.nextElementSibling.style.display = 'inline'; // Show save button
                    this.nextElementSibling.nextElementSibling.style.display = 'inline'; // Show cancel button
                } else {
                    console.error('Content div not found for contentId:', contentId);
                }
            })
            .catch(error => {
                console.error('Error fetching raw content:', error);
                alert('There was an error fetching the content. Please try again.');
            });
    });
});

// Function to decode HTML entities
function decodeHTMLEntities(text) {
    var textArea = document.createElement('textarea');
    textArea.innerHTML = text;
    return textArea.value;
}

document.querySelectorAll('.cancel-btn').forEach(button => {
    button.addEventListener('click', function() {
        location.reload(); // Simple way to discard changes
    });
});

document.querySelectorAll('.save-btn').forEach(button => {
    button.addEventListener('click', function() {
        const contentId = this.getAttribute('data-content-id');
        const editedContentElement = document.getElementById(`editable-content-${contentId}`);
        if (editedContentElement) {
            const editedContent = editedContentElement.value;
            // Step 2: Send Data to Server
            fetch(`/content/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Include CSRF token header if needed for Django
                    'X-CSRFToken': getCookie('csrftoken') // Function to get CSRF token from cookies
                },
                body: JSON.stringify({ contentId: contentId, editedContent: editedContent })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json(); // Assuming the server responds with JSON
            })
            .then(data => {
                // Step 3: Handle Server Response
                console.log('Success:', data);
                alert('Content saved successfully!');
                location.reload(); // Optionally reload the page to show the updated content
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error saving content. Please try again.');
            });
        } else {
            console.error('Edited content element not found for contentId:', contentId);
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