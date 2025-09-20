document.addEventListener('DOMContentLoaded', () => {

    // --- Login/Register Form Toggle ---
    const showRegister = document.getElementById('show-register');
    const showLogin = document.getElementById('show-login');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (showRegister && showLogin) {
        showRegister.addEventListener('click', (e) => {
            e.preventDefault();
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
        });

        showLogin.addEventListener('click', (e) => {
            e.preventDefault();
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
        });
    }

    // --- Consultation Selection Logic ---
    const consultationForm = document.getElementById('consultation-form');
    if (consultationForm) {
        const optionCards = consultationForm.querySelectorAll('.option-card');
        const paymentSummary = document.getElementById('payment-summary');
        const feeElement = document.getElementById('fee');
        const totalElement = document.getElementById('total');
        const proceedBtn = document.getElementById('proceed-btn');

        // Ensure the form submission method is GET for the URL parameters
        consultationForm.method = 'GET';

        optionCards.forEach(card => {
            card.addEventListener('click', () => {
                optionCards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                const type = card.dataset.type;
                // Corrected the typo in dataset access
                const price = card.dataset.price;

                // Get the doctor ID from the URL path
                const pathParts = window.location.pathname.split('/');
                const doctorId = pathParts[pathParts.length - 1];

                // Set the form action to the correct payment route
                consultationForm.action = `/payment/${doctorId}/${type}`;

                feeElement.textContent = `₹${price}`;
                totalElement.textContent = `₹${price}`;

                proceedBtn.textContent = 'Proceed to Payment';

                paymentSummary.classList.remove('hidden');
            });
        });
    }

    // --- Live Consultation Chat Toggle ---
    const toggleChatBtn = document.getElementById('toggle-chat-btn');
    const chatView = document.getElementById('chat-view');

    if (toggleChatBtn && chatView) {
        toggleChatBtn.addEventListener('click', () => {
            chatView.classList.toggle('is-open');
        });
    }

    // --- AI Chatbot Logic ---
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('chat-input');

    const addChatMessage = (message, senderClass) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('new-chat-message', senderClass);
        messageElement.innerHTML = message;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageText = userInput.value.trim();
            if (!messageText) return;
            addChatMessage(messageText, 'user');
            userInput.value = '';
            try {
                const res = await fetch('/api/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText })
                });
                const data = await res.json();
                addChatMessage(data.reply, 'bot');
            } catch (error) {
                console.error("Chatbot API error:", error);
                addChatMessage("Sorry, I'm having trouble connecting right now.", 'bot');
            }
        });
    }

    // --- Symptom Checker Logic ---
    const symptomForm = document.getElementById('symptom-form');
    const symptomMessages = document.getElementById('symptom-messages');
    const symptomInput = document.getElementById('symptom-input');

    const addSymptomMessage = (message, senderClass) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('new-chat-message', senderClass);
        messageElement.innerHTML = message;
        symptomMessages.appendChild(messageElement);
        symptomMessages.scrollTop = symptomMessages.scrollHeight;
    };

    if (symptomForm) {
        symptomForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const symptomText = symptomInput.value.trim();
            if (!symptomText) return;
            addSymptomMessage(symptomText, 'user');
            symptomInput.value = '';
            try {
                const res = await fetch('/api/symptom-checker', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symptoms: symptomText })
                });
                const data = await res.json();
                addSymptomMessage(data.reply, 'bot');
            } catch (error) {
                console.error("Symptom Checker API error:", error);
                addSymptomMessage("Sorry, I'm having trouble analyzing your symptoms right now.", 'bot');
            }
        });
    }

    // --- Doctor Search Logic ---
    const searchForm = document.getElementById('doctor-search-form');
    const searchInput = document.getElementById('doctor-search-input');
    const doctorGrid = document.getElementById('doctor-grid');
    const noResultsMessage = document.getElementById('no-results');

    const filterDoctors = () => {
        const searchTerm = searchInput.value.toLowerCase();
        const doctorCards = doctorGrid.querySelectorAll('.doctor-card');
        let resultsFound = false;

        doctorCards.forEach(card => {
            const name = card.dataset.name.toLowerCase();
            const specialty = card.dataset.specialty.toLowerCase();
            const hospital = card.dataset.hospital.toLowerCase();
            if (name.includes(searchTerm) || specialty.includes(searchTerm) || hospital.includes(searchTerm)) {
                card.style.display = 'block';
                resultsFound = true;
            } else {
                card.style.display = 'none';
            }
        });

        if (resultsFound) {
            noResultsMessage.classList.add('hidden');
        } else {
            noResultsMessage.classList.remove('hidden');
        }
    };

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            filterDoctors();
        });
        searchInput.addEventListener('keyup', filterDoctors);
    }

    // --- PWA Service Worker Registration ---
    // Consolidated duplicate service worker registration to a single, clean block
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registered with scope:', registration.scope);
                })
                .catch(error => {
                    console.error('Service Worker registration failed:', error);
                });
        });
    }

});