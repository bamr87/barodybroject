/**
 * File: content_detail.js
 * Description: Dynamic content loading and form handling with vanilla JavaScript
 * Author: Barodybroject Team <team@example.com>
 * Created: 2025-01-15
 * Last Modified: 2026-08-29
 * Version: 2.1.0
 *
 * Dependencies:
 * - None (vanilla JavaScript, no jQuery, no client-side Markdown library)
 *
 * Usage: Include in content detail template
 *
 * Markdown fields render server-side. Rendering here in the browser would need a
 * second Markdown library and would bypass the bleach sanitizer that
 * `parodynews.utils.markdown.render_markdown` applies — a stored-XSS path in an
 * app whose content is AI-generated and user-editable. Every re-render is a POST
 * to `markdown_preview`, which returns already-sanitized HTML.
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

/**
 * POST Markdown source to the server and resolve with sanitized HTML.
 *
 * @param {string} url  the `markdown_preview` endpoint
 * @param {string} text raw Markdown
 * @returns {Promise<string>} rendered, already-sanitized HTML
 */
function fetchRenderedMarkdown(url, text) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ text: text }).toString()
    }).then(response => {
        if (!response.ok) {
            throw new Error(`Markdown preview failed: ${response.status}`);
        }
        return response.text();
    });
}

/**
 * Re-render one field's preview from its current source value.
 *
 * On failure the preview is left exactly as it was and the editor stays open,
 * so a dropped request can never destroy what the user typed or blank the
 * field — the raw text is still in the textarea, and it is still what submits.
 *
 * @param {HTMLElement} field a [data-markdown-field] wrapper
 * @param {string} url        the `markdown_preview` endpoint
 * @returns {Promise<void>}
 */
function refreshMarkdownPreview(field, url) {
    const rendered = field.querySelector('[data-markdown-rendered]');
    const input = field.querySelector('[data-markdown-source] textarea, [data-markdown-source] input, input[type="hidden"]');
    if (!rendered || !input) {
        return Promise.resolve();
    }
    return fetchRenderedMarkdown(url, input.value)
        .then(html => { rendered.innerHTML = html; })
        .catch(error => { console.error('Error rendering markdown preview:', error); });
}

/**
 * Wire up render-on-blur / raw-on-focus for every Markdown field under `root`.
 *
 * Read-only fields ([data-markdown-readonly]) have no editor in the DOM at all,
 * so they cannot reveal their source however they are clicked.
 *
 * @param {HTMLElement} root container carrying data-markdown-preview-url
 */
function initMarkdownFields(root) {
    const url = root.dataset.markdownPreviewUrl;
    if (!url) {
        return;
    }
    root.querySelectorAll('[data-markdown-field]').forEach(field => {
        const rendered = field.querySelector('[data-markdown-rendered]');
        const source = field.querySelector('[data-markdown-source]');
        // Read-only: rendered HTML only, nothing to swap to.
        if (!rendered || !source) {
            return;
        }
        const input = source.querySelector('textarea, input');
        if (!input) {
            return;
        }

        // Hidden HERE rather than in the template: with JavaScript disabled the
        // editor stays visible and usable instead of being unreachable.
        source.classList.add('d-none');

        const edit = () => {
            source.classList.remove('d-none');
            rendered.classList.add('d-none');
            input.focus();
        };
        rendered.addEventListener('click', edit);
        rendered.addEventListener('focus', edit);
        rendered.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                edit();
            }
        });

        input.addEventListener('blur', () => {
            refreshMarkdownPreview(field, url).finally(() => {
                source.classList.add('d-none');
                rendered.classList.remove('d-none');
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const contentForm = document.getElementById('content-form');
    if (contentForm) {
        initMarkdownFields(contentForm);
    }

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
                        // `instructions` is read-only, so it is displayed as
                        // rendered HTML — updating only the input would leave
                        // the user looking at the previous assistant's text.
                        const field = instructionsField.closest('[data-markdown-field]');
                        if (field && contentForm) {
                            refreshMarkdownPreview(field, contentForm.dataset.markdownPreviewUrl);
                        }
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
