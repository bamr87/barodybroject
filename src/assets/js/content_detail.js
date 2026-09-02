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

    // Quick-edit dialog for the selected assistant (issue #105). The assistants
    // are <option>s inside a <select>, which browsers render as native UI: there
    // is no per-assistant element to hover, position against, or attach a button
    // to. So the control is adjacent to the select and acts on the current
    // selection, and it is always visible rather than hover-revealed — :hover
    // does not exist on touch devices and a hover-only control is unreachable by
    // keyboard and unannounced to screen readers.
    const editAssistantBtn = document.getElementById('edit-assistant-btn');
    const modalEl = document.getElementById('assistantEditModal');
    const modalForm = document.getElementById('assistantEditForm');
    const modalBody = document.getElementById('assistantEditBody');
    const modalAlert = document.getElementById('assistantEditAlert');
    const modalSave = document.getElementById('assistantEditSave');

    function syncEditButtonState() {
        if (!editAssistantBtn || !assistantSelect) {
            return;
        }
        editAssistantBtn.disabled = !assistantSelect.value;
    }

    function showModalError(message) {
        if (!modalAlert) {
            return;
        }
        modalAlert.textContent = message;
        modalAlert.classList.remove('d-none');
    }

    function clearModalError() {
        if (!modalAlert) {
            return;
        }
        modalAlert.textContent = '';
        modalAlert.classList.add('d-none');
    }

    function focusFirstField() {
        if (!modalBody) {
            return;
        }
        const first = modalBody.querySelector(
            'input:not([type="hidden"]), select, textarea'
        );
        if (first) {
            first.focus();
        }
    }

    function loadAssistantForm(assistantId) {
        if (!modalBody) {
            return Promise.resolve();
        }
        modalBody.setAttribute('aria-busy', 'true');
        modalSave.disabled = true;
        clearModalError();
        // Reset to the spinner first, or reopening the dialog for a different
        // assistant briefly shows the previous one's values.
        modalBody.innerHTML =
            '<div class="text-center py-4"><div class="spinner-border" role="status">' +
            '<span class="visually-hidden">Loading assistant…</span></div></div>';

        return fetch(`/assistants/${assistantId}/quick-edit/`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Could not load assistant (${response.status})`);
            }
            return response.text();
        })
        .then(html => {
            modalBody.innerHTML = html;
            modalSave.disabled = false;
            focusFirstField();
        })
        .catch(error => {
            console.error('Error loading assistant form:', error);
            modalBody.innerHTML = '';
            showModalError(error.message);
        })
        .finally(() => {
            modalBody.setAttribute('aria-busy', 'false');
        });
    }

    if (assistantSelect) {
        assistantSelect.addEventListener('change', function() {
            const assistantId = this.value;
            syncEditButtonState();
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

    // Reflect the initial selection, so the button starts disabled on a blank
    // form and enabled on one that already has an assistant.
    syncEditButtonState();

    if (editAssistantBtn && modalEl && window.bootstrap) {
        const modal = window.bootstrap.Modal.getOrCreateInstance(modalEl);

        editAssistantBtn.addEventListener('click', function() {
            if (!assistantSelect || !assistantSelect.value) {
                return;
            }
            modal.show();
            loadAssistantForm(assistantSelect.value);
        });

        // Bootstrap restores focus to the opener itself, but only if the dialog
        // was opened via data-bs-toggle. It was opened from script here, so
        // return focus explicitly.
        modalEl.addEventListener('hidden.bs.modal', function() {
            editAssistantBtn.focus();
        });

        if (modalForm) {
            modalForm.addEventListener('submit', function(event) {
                event.preventDefault();
                if (!assistantSelect || !assistantSelect.value) {
                    return;
                }

                const assistantId = assistantSelect.value;
                const formData = new FormData(modalForm);
                clearModalError();
                modalSave.disabled = true;

                fetch(`/assistants/${assistantId}/quick-edit/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: formData
                })
                .then(response => {
                    // 422 re-renders the fields with validation errors; the
                    // dialog stays open so the user keeps their input.
                    if (response.status === 422) {
                        return response.text().then(html => {
                            modalBody.innerHTML = html;
                            modalSave.disabled = false;
                            focusFirstField();
                            return null;
                        });
                    }
                    if (!response.ok) {
                        return response.json()
                            .catch(() => ({ error: `Save failed (${response.status})` }))
                            .then(payload => {
                                throw new Error(payload.error || 'Save failed');
                            });
                    }
                    return response.json();
                })
                .then(data => {
                    if (!data) {
                        return;
                    }
                    // Mirror the instructions into the content form, matching
                    // what the select's own change handler does above.
                    const instructionsField = document.getElementById('id_instructions');
                    if (instructionsField) {
                        instructionsField.value = data.instructions || '';
                    }
                    // Keep the selector's label in step with a renamed assistant.
                    const option = assistantSelect.querySelector(
                        `option[value="${data.assistant_id}"]`
                    );
                    if (option && data.name) {
                        option.textContent = data.name;
                    }
                    modal.hide();
                })
                .catch(error => {
                    console.error('Error saving assistant:', error);
                    showModalError(error.message);
                    modalSave.disabled = false;
                });
            });
        }
    }
});
