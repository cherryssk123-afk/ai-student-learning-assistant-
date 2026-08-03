/**
 * AI-Powered Student Learning Assistant - Interactive JS Engine
 * Coventry University MSc Dissertation Project
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('Learning Assistant UI Initialized.');

    // Initialize Bootstrap tooltips & popovers if present
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-scroll tutor chat container to bottom
    const chatBox = document.getElementById('chatContainer');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});

/**
 * Toggle Roadmap Week completion via AJAX
 */
function toggleWeekCompletion(roadmapId, weekId) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/roadmap/${roadmapId}/toggle-week/${weekId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update progress bar
            const progressBar = document.getElementById(`roadmapProgressBar`);
            const progressBadge = document.getElementById(`roadmapProgressBadge`);
            const weekCard = document.getElementById(`weekCard_${weekId}`);
            const weekStatusBadge = document.getElementById(`weekStatus_${weekId}`);

            if (progressBar) {
                progressBar.style.width = `${data.progress_percent}%`;
                progressBar.setAttribute('aria-valuenow', data.progress_percent);
            }
            if (progressBadge) {
                progressBadge.innerText = `${data.progress_percent}% Completed`;
            }
            if (weekStatusBadge) {
                if (data.week_completed) {
                    weekStatusBadge.className = 'badge bg-success';
                    weekStatusBadge.innerText = 'Completed';
                } else {
                    weekStatusBadge.className = 'badge bg-secondary';
                    weekStatusBadge.innerText = 'In Progress';
                }
            }

            // Toast feedback
            showToast(data.week_completed ? 'Milestone marked complete!' : 'Milestone status reset.');
        } else {
            alert('Error updating milestone status.');
        }
    })
    .catch(error => console.error('Error toggling week:', error));
}

/**
 * Send question to AI Tutor via AJAX
 */
function sendTutorQuestion(event) {
    event.preventDefault();
    const questionInput = document.getElementById('tutorQuestion');
    const contextInput = document.getElementById('tutorContext');
    const chatContainer = document.getElementById('chatContainer');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const question = questionInput.value.trim();
    const context = contextInput ? contextInput.value : 'General';

    if (!question) return;

    // Append User Message to UI
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsgHtml = `
        <div class="d-flex mb-3">
            <div class="chat-bubble-user">
                <div class="fw-semibold text-white mb-1"><i class="bi bi-person-fill"></i> You</div>
                <p class="mb-1">${escapeHtml(question)}</p>
                <small class="text-white-50 float-end" style="font-size: 0.7rem;">${timeNow}</small>
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', userMsgHtml);

    // Clear input
    questionInput.value = '';
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Append Typing Indicator
    const typingId = `typing_${Date.now()}`;
    const typingHtml = `
        <div class="d-flex mb-3" id="${typingId}">
            <div class="chat-bubble-ai">
                <div class="fw-semibold text-emerald mb-1"><i class="bi bi-robot"></i> AI Academic Tutor</div>
                <div class="py-2">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <small class="text-muted ms-2">Synthesizing academic explanation...</small>
                </div>
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', typingHtml);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // POST request to backend
    fetch('/tutor/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ question: question, context: context })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        if (data.success) {
            const formattedAnswer = renderMarkdownSimple(data.answer);
            const aiMsgHtml = `
                <div class="d-flex mb-3">
                    <div class="chat-bubble-ai">
                        <div class="fw-semibold text-success mb-2"><i class="bi bi-robot"></i> AI Academic Tutor</div>
                        <div class="markdown-body">${formattedAnswer}</div>
                        <small class="text-muted float-end" style="font-size: 0.7rem;">${data.timestamp}</small>
                    </div>
                </div>
            `;
            chatContainer.insertAdjacentHTML('beforeend', aiMsgHtml);
        } else {
            const errorHtml = `
                <div class="d-flex mb-3">
                    <div class="chat-bubble-ai border-danger">
                        <div class="text-danger mb-1"><i class="bi bi-exclamation-triangle"></i> Error</div>
                        <p class="mb-0 text-white-50">${data.error || 'Failed to communicate with tutor engine.'}</p>
                    </div>
                </div>
            `;
            chatContainer.insertAdjacentHTML('beforeend', errorHtml);
        }
        chatContainer.scrollTop = chatContainer.scrollHeight;
    })
    .catch(err => {
        console.error('Tutor Error:', err);
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        const catchHtml = `
            <div class="d-flex mb-3">
                <div class="chat-bubble-ai border-warning">
                    <div class="text-warning mb-1"><i class="bi bi-exclamation-circle"></i> Service Connection Notice</div>
                    <p class="mb-0 text-white-50">Tutor response synthesis issue. Please try submitting again or refreshing.</p>
                </div>
            </div>
        `;
        chatContainer.insertAdjacentHTML('beforeend', catchHtml);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    });
}

/**
 * Copy text element to clipboard
 */
function copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const text = el.innerText || el.value;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}

/**
 * Download text content as file
 */
function downloadSummaryAsFile(elementId, filename = 'study_summary.txt') {
    const el = document.getElementById(elementId);
    if (!el) return;

    const text = el.innerText;
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
}

/**
 * Toast Notification Utility
 */
function showToast(message) {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    const toastId = `toast_${Date.now()}`;
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-dark border-emerald show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-check-circle-fill text-success me-2"></i> ${escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    setTimeout(() => {
        const el = document.getElementById(toastId);
        if (el) el.remove();
    }, 3500);
}

/**
 * Simple Lightweight Markdown Renderer
 */
function renderMarkdownSimple(mdText) {
    if (!mdText) return '';
    let html = mdText;
    
    // Code blocks ```python ... ```
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
        return `<pre class="bg-dark p-3 rounded border border-secondary text-light"><code>${escapeHtml(code.trim())}</code></pre>`;
    });

    // Inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code class="bg-dark text-success px-1 rounded">$1</code>');

    // Headings ### ## #
    html = html.replace(/^### (.*$)/gim, '<h5 class="mt-3 mb-2 text-emerald">$1</h5>');
    html = html.replace(/^## (.*$)/gim, '<h4 class="mt-3 mb-2 text-emerald">$1</h4>');
    html = html.replace(/^# (.*$)/gim, '<h3 class="mt-3 mb-2 text-emerald">$1</h3>');

    // Bold **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italics *text*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Bullet lists - item
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li class="ms-3">$1</li>');

    // Paragraph breaks
    html = html.replace(/\n\n/g, '<br/><br/>');

    return html;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
