// Handle GitHub issue form submission
// This script reads title and body from the modal form and redirects to GitHub's new issue page

document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('submitIssueButton');
    const form = document.getElementById('issueForm');
    const templateSelect = document.getElementById('templateSelect');
    const modal = document.getElementById('issueModal');
    const modalBody = document.getElementById('modalBody');
    if (!submitBtn || !form || !templateSelect || !modal || !modalBody) return;

    templateSelect.addEventListener('change', async () => {
        const selectedTemplate = templateSelect.value;
        if (!selectedTemplate) return;

        try {
            const response = await fetch(`/templates/${selectedTemplate}.json`);
            if (!response.ok) {
                console.error('Failed to fetch template:', response.statusText);
                return;
            }
            const templateData = await response.json();
            modalBody.innerHTML = `
                <label for="title">Title:</label>
                <input type="text" id="title" name="title" value="${templateData.title || ''}" required>
                <label for="body">Body:</label>
                <textarea id="body" name="body" required>${templateData.body || ''}</textarea>
            `;
            modal.style.display = 'block';
        } catch (error) {
            console.error('Error fetching template:', error);
        }
    });

    submitBtn.addEventListener('click', () => {
        const formData = new FormData(form);
        const title = formData.get('title') || '';
        const body = formData.get('body') || '';
        const repo = form.dataset.repo;
        if (!repo) {
            console.error('GitHub repository not specified on form.');
            return;
        }
        const url = `https://github.com/${repo}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
        window.open(url, '_blank');
    });
});