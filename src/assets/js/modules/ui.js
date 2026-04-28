// Shared UI behavior for Bootstrap-powered pages.

document.addEventListener('DOMContentLoaded', () => {
    const confirmModal = document.getElementById('confirmModal');
    const confirmButton = document.getElementById('confirmButton');
    const confirmMessage = document.getElementById('confirmMessage');

    if (confirmModal && confirmButton && confirmMessage) {
        let confirmTarget = null;

        confirmModal.addEventListener('show.bs.modal', event => {
            confirmTarget = event.relatedTarget || null;
            const message = confirmTarget?.getAttribute('data-confirm-message');
            const buttonText = confirmTarget?.getAttribute('data-confirm-button-text');
            const buttonClass = confirmTarget?.getAttribute('data-confirm-button-class');

            confirmMessage.textContent = message || 'Are you sure you want to perform this action? This cannot be undone.';
            confirmButton.textContent = buttonText || 'Delete';
            confirmButton.className = `btn ${buttonClass || 'btn-danger'}`;
        });

        confirmButton.addEventListener('click', () => {
            const href = confirmTarget?.getAttribute('data-confirm-href') || confirmTarget?.getAttribute('href');
            const formSelector = confirmTarget?.getAttribute('data-confirm-form');
            const form = formSelector ? document.querySelector(formSelector) : confirmTarget?.closest('form');

            if (form) {
                form.submit();
                return;
            }

            if (href && href !== '#') {
                window.location.href = href;
            }
        });
    }

    document.querySelectorAll('form[data-loading]').forEach(form => {
        form.addEventListener('submit', event => {
            const submitter = event.submitter || form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitter instanceof HTMLButtonElement) {
                if (submitter.name) {
                    const hiddenSubmitter = document.createElement('input');
                    hiddenSubmitter.type = 'hidden';
                    hiddenSubmitter.name = submitter.name;
                    hiddenSubmitter.value = submitter.value;
                    form.appendChild(hiddenSubmitter);
                }

                submitter.disabled = true;
                submitter.dataset.originalText = submitter.textContent;
                submitter.textContent = submitter.dataset.loadingText || 'Working...';
            }
        });
    });
});