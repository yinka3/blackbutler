$.js = function (el) {
    return $('[data-js=' + el + ']')
};


function typeWriter(text, element, delay = 50) {
    let i = 0;
    element.textContent = "";
    const interval = setInterval(() => {
        element.textContent += text;
        clearInterval(interval);
    }, delay);
}

function appendFormattedMessage(text, sender) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message', sender, 'main-message');

    const markdownLinkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
    const urlOnlyRegex = /(https?:\/\/[^\s]+)/g;

    const linkCards = [];
    const lines = text.split('\n');

    const cleanLines = lines.map(line => {
        let updatedLine = line;


        let match;
        while ((match = markdownLinkRegex.exec(line)) !== null) {
            linkCards.push({ text: match[1], url: match[2] });
            updatedLine = updatedLine.replace(match[0], '');
        }

        const urlMatches = updatedLine.match(urlOnlyRegex);
        if (urlMatches) {
            urlMatches.forEach(url => {
                linkCards.push({ text: url, url: url });
                updatedLine = updatedLine.replace(url, '');
            });
        }

        return updatedLine.trim();
    });

    const textContent = cleanLines.filter(Boolean).join('\n').trim();
    if (textContent) {
        const paragraph = document.createElement('p');
        paragraph.textContent = textContent;
        messageContainer.appendChild(paragraph);
    }

    if (linkCards.length > 0) {
        const cardGroup = document.createElement('div');
        cardGroup.classList.add('link-card-group');

        linkCards.forEach(({ text, url }) => {
            const card = document.createElement('a');
            card.href = url;
            card.target = "_blank";
            card.rel = "noopener noreferrer";
            card.classList.add('link-card');
            card.textContent = text;
            cardGroup.appendChild(card);
        });

        messageContainer.appendChild(cardGroup);
    }

    const chatMessages = document.getElementById("chat-messages");
    chatMessages.appendChild(messageContainer);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageContainer;
}


// Handle Learn More button clicks
let socket = null;
let currentEngineer = "";

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("chat-modal");
    const closeModal = document.querySelector("#chat-modal .close-btn");
    const promptInput = document.getElementById("user-prompt");
    const chatMessages = document.getElementById("chat-messages");

    // Global variables for the WebSocket and engineer context
    let socket = null;
    let currentEngineer = "";
    let loadingBubble = null;

    // Function to open and setup WebSocket connection
    function openSocket() {
        if (!socket || socket.readyState === WebSocket.CLOSED) {
            socket = new WebSocket("wss://blackbutler.onrender.com/ws/blackbutler");
            
            socket.onopen = () => {
                console.log("WebSocket connected.");
            };

            socket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                if (loadingBubble && loadingBubble.parentNode) {
                    loadingBubble.parentNode.removeChild(loadingBubble);
                    loadingBubble = null;
                }
                appendFormattedMessage(data.response, "bot");
            };

            socket.onerror = (err) => {
                console.error("WebSocket error:", err);
                appendFormattedMessage("WebSocket error occurred.", "bot");
            };

            socket.onclose = () => {
                console.log("WebSocket closed.");
            };
        }
    }

    // When a "Talk to Butler" button is clicked, open modal and socket
    document.querySelectorAll(".read-more").forEach(button => {
        button.addEventListener("click", function () {
            currentEngineer = this.getAttribute("data-engineer");
            document.getElementById("chat-engineer").textContent = `Ask about ${currentEngineer}:`;
            promptInput.value = "";
            chatMessages.innerHTML = "";
            modal.classList.add("active");
            openSocket();
        });
    });

    // Send user prompt on clicking Ask button
    document.getElementById("submit-prompt").addEventListener("click", function () {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            appendFormattedMessage("Please enter a question.", "bot");
            return;
        }
        appendFormattedMessage(prompt, "user");
        promptInput.value = "";
        loadingBubble = appendFormattedMessage("Loading...", "bot");
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ engineer: currentEngineer, prompt }));
        } else {
            if (loadingBubble && loadingBubble.parentNode) {
                loadingBubble.parentNode.removeChild(loadingBubble);
                loadingBubble = null;
            }
            appendFormattedMessage("WebSocket is not connected.", "bot");
        }
    });

    const startingPrompts = document.querySelectorAll('.starting-prompt');
    startingPrompts.forEach(button => {
        button.addEventListener("click", function () {
            const prompt = this.textContent.trim();
            appendFormattedMessage(prompt, "user");
            loadingBubble = appendFormattedMessage("Loading...", "bot");
            openSocket();
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ engineer: currentEngineer, prompt }));
            } else {
                if (loadingBubble && loadingBubble.parentNode) {
                    loadingBubble.parentNode.removeChild(loadingBubble);
                    loadingBubble = null;
                }
                appendFormattedMessage("WebSocket is not connected.", "bot");
            }
        });
    });

    closeModal.addEventListener("click", function () {
        modal.classList.remove("active");
        if (socket) {
            socket.close();
            socket = null;
        }
    });

    document.getElementById("scroll-to-timeline").addEventListener("click", function () {
        document.querySelector(".timeline").scrollIntoView({ behavior: "smooth" });
    });

    const timelineItems = document.querySelectorAll('.timeline-item');

    const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
        });
    }, {
        threshold: 0.15 // how much of the element should be visible
    });

    timelineItems.forEach(item => {
        observer.observe(item);
    });
});
