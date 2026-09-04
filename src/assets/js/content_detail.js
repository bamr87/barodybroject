/**
 * File: content_detail.js
 * Description: Dynamic content loading and form handling with vanilla JavaScript
 * Author: Barodybroject Team <team@example.com>
 * Created: 2025-01-15
 * Last Modified: 2026-09-04
 * Version: 2.1.0
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
                    // The hidden input carries the raw Markdown that the form
                    // submits; the sibling block shows it rendered. Both are
                    // updated together so the two never drift apart.
                    const instructionsField = document.getElementById('id_instructions');
                    if (data.instructions && instructionsField) {
                        instructionsField.value = data.instructions;
                    }
                    const instructionsRendered = document.getElementById('instructions-rendered');
                    if (instructionsRendered && data.instructions_html !== undefined) {
                        // Server-rendered by django-markdownify and already
                        // bleach-sanitised. Never assign raw Markdown here.
                        instructionsRendered.innerHTML = data.instructions_html;
                    }
                })
                .catch(error => {
                    console.error('Error fetching instructions:', error);
                    alert('Error fetching instructions');
                });
            }
        });
    }
});
