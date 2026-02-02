document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const messagesContainer = document.getElementById('messagesContainer');
    const sendBtn = document.querySelector('.send-btn');

    // History Elements
    const chatNav = document.getElementById('chatNav');
    const historyNav = document.getElementById('historyNav');
    const restartBtn = document.getElementById('restartBtn');
    const chatArea = document.getElementById('chatArea');
    const historyArea = document.getElementById('historyArea');
    const historyContainer = document.getElementById('historyContainer');

    // Auto-focus input
    userInput.focus();

    // --- Navigation Logic ---
    chatNav.addEventListener('click', (e) => {
        e.preventDefault();
        chatNav.classList.add('active');
        historyNav.classList.remove('active');
        chatArea.classList.remove('hidden');
        historyArea.classList.add('hidden');
    });

    historyNav.addEventListener('click', async (e) => {
        e.preventDefault();
        historyNav.classList.add('active');
        chatNav.classList.remove('active');
        historyArea.classList.remove('hidden');
        chatArea.classList.add('hidden');

        // Load history when tab is clicked
        await loadHistory();
    });

    restartBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to restart the chat? This will clear the current conversation window, but your history will remain.')) {
            try {
                const response = await fetch('/api/restart', { method: 'POST' });
                if (response.ok) {
                    // Clear UI
                    messagesContainer.innerHTML = '';

                    // Add Welcome Message back
                    addMessage("Hello! I'm your TechGear Assistant. How can I help you today?", 'output-message');

                    // Reset View to Chat
                    chatNav.click();
                }
            } catch (error) {
                console.error('Error restarting chat:', error);
            }
        }
    });

    async function loadHistory() {
        historyContainer.innerHTML = '<div class="message output-message"><p>Loading history...</p></div>';
        try {
            const response = await fetch('/api/history');
            const data = await response.json();

            if (data.length === 0) {
                historyContainer.innerHTML = '<div class="message output-message"><p>No chat history yet. Start a conversation!</p></div>';
                return;
            }

            historyContainer.innerHTML = ''; // Clear loader

            // Render history items
            data.forEach(item => {
                const historyEl = document.createElement('div');
                historyEl.className = 'history-item';
                historyEl.innerHTML = `
                    <div class="history-q">Q: ${item.question}</div>
                    <div class="history-a">${item.response.replace(/\n/g, '<br>')}</div>
                    <div class="history-meta">
                        <span class="history-tag">${item.category}</span>
                        <span>${item.timestamp}</span>
                    </div>
                `;
                historyContainer.appendChild(historyEl);
            });
        } catch (error) {
            console.error('Error fetching history:', error);
            historyContainer.innerHTML = '<p>Error loading history.</p>';
        }
    }

    // --- Chat Logic ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();

        if (message) {
            // Add user message
            addMessage(message, 'input-message');
            userInput.value = '';

            // Disable input while waiting
            setInputState(false);

            try {
                // Call API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();

                // Add bot message
                addMessage(data.response, 'output-message');

            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, something went wrong. Please try again.', 'output-message');
            } finally {
                setInputState(true);
                userInput.focus();
            }
        }
    });

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const formattedText = text.replace(/\n/g, '<br>');

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${formattedText}</p>
                <span class="timestamp">${timestamp}</span>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function setInputState(enabled) {
        userInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        if (!enabled) {
            sendBtn.style.opacity = '0.7';
            sendBtn.style.cursor = 'not-allowed';
        } else {
            sendBtn.style.opacity = '1';
            sendBtn.style.cursor = 'pointer';
        }
    }
});
