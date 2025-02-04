document.addEventListener('DOMContentLoaded', () => {


    // Initialize Markdown parser
    marked.setOptions({ breaks: true });

    // Message creation function
    function createMessageElement(message) {
        const isUser = message.role === 'user';
        const div = document.createElement('div');
        div.className = `flex ${isUser ? 'justify-end' : 'justify-start'} gap-3`;
        
        div.innerHTML = `
            <div class="${isUser ? 'bg-blue-600' : 'bg-gray-800'} text-white p-4 rounded-2xl max-w-[80%] ${
                isUser ? 'rounded-br-none' : 'rounded-bl-none'
            } shadow-lg">
                <div class="prose prose-invert">${marked.parse(message.content)}</div>
            </div>
        `;
        return div;
    }

    // Message submission handler
    async function sendMessage(event) {
        event.preventDefault();
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        const container = document.getElementById('chat-container');
        const loading = document.getElementById('loading');
        const chatWindow = document.querySelector('.overflow-y-auto');

        if (!message) return;

        // Add user message
        const userMessage = createMessageElement({ role: 'user', content: message });
        userMessage.classList.add('message-enter');
        container.appendChild(userMessage);
        
        input.value = '';
        loading.classList.remove('hidden');
        
        chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Add bot response
            const botMessage = createMessageElement({ role: 'assistant', content: data.response });
            botMessage.classList.add('message-enter');
            container.appendChild(botMessage);

        } catch (error) {
            console.error('Error:', error);
            const errorMessage = createMessageElement({
                role: 'assistant',
                content: '**Error:** Could not get response'
            });
            errorMessage.classList.add('message-enter');
            container.appendChild(errorMessage);
        } finally {
            loading.classList.add('hidden');
            setTimeout(() => {
                chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
            }, 50);
        }
    }

    // Event listeners
    document.getElementById('chat-form').addEventListener('submit', sendMessage);
}); 