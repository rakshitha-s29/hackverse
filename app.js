document.addEventListener('DOMContentLoaded', () => {

    const onboarding = document.getElementById('onboarding');
    const startBtn = document.getElementById('start-btn');
    const usernameInput = document.getElementById('username-input');
    const greetingText = document.getElementById('greeting');
    const heroSection = document.getElementById('hero');
    const festivalInfoText = document.getElementById('festival-info');
    const monthTitle = document.getElementById('month-special-title');
    const globalTravelerSelect = document.getElementById('global-traveler-select');

    let appData = null;
    let userName = localStorage.getItem('travelUserName');

    if(onboarding) {
        if(userName) {
            onboarding.style.display = 'none';
            fetchBackendData(userName);
        }

        startBtn.addEventListener('click', () => {
            const inputName = usernameInput.value.trim();
            if(inputName) {
                userName = inputName;
                localStorage.setItem('travelUserName', userName);
                onboarding.style.opacity = '0';
                setTimeout(() => {
                    onboarding.style.display = 'none';
                    fetchBackendData(userName);
                }, 500);
            }
        });
    } else {
        fetchBackendData(userName || "Traveler");
    }

    async function fetchBackendData(name) {
        try {
            const res = await fetch('/api/data');
            if(!res.ok) throw new Error("Failed to fetch");
            appData = await res.json();
            
            if(greetingText) {
                initializeHomePage(name);
            }
        } catch(err) {
            console.error(err);
        }
        initChatStateMachine(name || "Traveler");
    }

    function initializeHomePage(name) {
        greetingText.textContent = `Welcome back, ${name}`;
        
        const date = new Date();
        const currentMonthIndex = String(date.getMonth());
        
        const festivalInfo = appData.festivalsData && appData.festivalsData[currentMonthIndex] ? appData.festivalsData[currentMonthIndex] : {
            month: 'this month', event: 'Exciting festivals and celebrations', bg: 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&q=80&w=2000'
        };

        if(monthTitle) monthTitle.textContent = `Special in ${festivalInfo.month}`;
        festivalInfoText.textContent = `Discover incredible places hosting ${festivalInfo.event}`;
        // heroSection.style.backgroundImage = `url('${festivalInfo.bg}')`; // PRESERVE ELEGANT BACKGROUND

        // Render Carousels using the mapping to cities database
        renderCarousel('special-carousel', appData.topDestinationsThisMonth);
        renderCarousel('trending-carousel', appData.trendingDestinations);
        
        // Render photo-based Mood Folders
        renderMoodFolders();

        // Traveler logic altering recommendations locally
        if(globalTravelerSelect) {
            globalTravelerSelect.addEventListener('change', () => {
                // To simulate UI feeling "alive", we re-render carousels 
                // in reality we might sort or filter the list based on family vs solo etc
                renderCarousel('trending-carousel', appData.trendingDestinations.reverse());
            });
        }
    }

    function renderCarousel(containerId, dataList) {
        const container = document.getElementById(containerId);
        if(!container || !dataList || !appData.cities) return;
        container.innerHTML = '';
        
        dataList.forEach(item => {
            const cityInfo = appData.cities[item.id];
            if(!cityInfo) return; // safeguard
            
            const cardAnchor = document.createElement('a');
            cardAnchor.href = `/city/${item.id}`;
            cardAnchor.className = 'card';
            cardAnchor.style.textDecoration = 'none';
            cardAnchor.style.color = 'inherit';
            
            let tagHTML = item.tag ? `<div class="card-tag">${item.tag}</div>` : '';
            cardAnchor.innerHTML = `${tagHTML}<img src="${cityInfo.img}" alt="${cityInfo.title}">
                                  <div class="card-title">${cityInfo.title}</div>`;
            container.appendChild(cardAnchor);
        });
    }

    function renderMoodFolders() {
        const grid = document.getElementById('mood-folders-grid');
        if(!grid) return;
        grid.innerHTML = '';
        
        const moods = Object.keys(appData.moodDestinations);
        moods.forEach(mood => {
            const imgUrl = appData.moodImages[mood] || "https://images.unsplash.com/photo-1477587458883-47145ed94245";
            const a = document.createElement('a');
            a.href = `/mood/${mood}`;
            a.className = 'folder-card-photo';
            a.innerHTML = `
                <img src="${imgUrl}" alt="${mood} vibe">
                <div class="folder-overlay">
                    <span style="font-size:24px; font-weight:800; text-transform:capitalize;">${mood}</span>
                </div>
            `;
            grid.appendChild(a);
        });
    }

    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if(window.scrollY > 50 && navbar) {
            navbar.classList.add('scrolled');
        } else if(navbar) {
            navbar.classList.remove('scrolled');
        }
    });

    // ==========================================
    // NAMASTE NAVIGATOR AI STATE MACHINE
    // ==========================================
    const aiGuideBtn = document.getElementById('ai-guide');
    const chatbox = document.getElementById('chatbox');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatInputContainer = document.getElementById('chat-input-container');

    let chatOpen = false;
    let chatState = 0; 
    let finalItineraryMarkup = "";
    
    let tripData = {
        origin: '',
        mood: '',
        days: '',
        people: '',
        budget: '',
        destination: '',
        editStr: '',
        saveContent: ''
    };

    function initChatStateMachine(name) {
        if(chatMessages && chatState === 0) {
            const sel = document.getElementById('global-traveler-select');
            if(sel) tripData.people = sel.value;
            addMessage(`Namaste ${name}! I'm Namaste Navigator. Let's build your perfect, hyper-customized trip! First, <b>Where are you traveling from?</b> (e.g., Bangalore, Delhi, New York)`, 'ai');
        }
    }

    if(aiGuideBtn) {
        aiGuideBtn.addEventListener('click', () => {
            chatOpen = !chatOpen;
            if(chatOpen) {
                chatbox.classList.add('active');
                userInput.focus();
            } else {
                chatbox.classList.remove('active');
            }
        });
    }

    function addMessage(text, sender) {
        if(!chatMessages) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${sender}`;
        msgDiv.innerHTML = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function handleUserInput() {
        const text = userInput.value.trim();
        if(!text) return;
        
        addMessage(text, 'user');
        userInput.value = '';

        if(chatState === 0) {
            tripData.origin = text;
            chatState = 1;
            setTimeout(() => addMessage(`Got it, starting from ${tripData.origin}. Now, <b>what is your mood?</b> (e.g., Happy, Peaceful, Romantic, Historic)`, 'ai'), 400);
        }
        else if(chatState === 1) {
            tripData.mood = text;
            chatState = 2;
            setTimeout(() => addMessage("Excellent! How many days do you plan to stay?", 'ai'), 400);
        } 
        else if(chatState === 2) {
            tripData.days = text;
            chatState = 3;
            const sel = document.getElementById('global-traveler-select');
            if(sel && sel.value !== "") tripData.people = sel.value;
            setTimeout(() => addMessage(`Great. How many people are traveling? (Currently set to ${tripData.people || 'unknown'}, type a number to override or 'keep')`, 'ai'), 400);
        }
        else if(chatState === 3) {
            if(text.toLowerCase() !== "keep" && text !== "") tripData.people = text;
            chatState = 4;
            setTimeout(() => addMessage("Almost done! What is your exact numerical budget capacity? (e.g., 3500, 50000)", 'ai'), 400);
        }
        else if(chatState === 4) {
            tripData.budget = text;
            chatState = 5;
            callBackendGenerator('suggest_places');
        }
        else if(chatState === 5) {
             tripData.destination = text;
             chatState = 6;
             callBackendGenerator('generate_itinerary');
        }
        else if(chatState === 6) {
            // Confirm or Edit
            if(text.toLowerCase().includes('confirm') || text.toLowerCase().includes('yes') || text.toLowerCase().includes('save') || text.toLowerCase().includes('fine') || text.toLowerCase().includes('looks good')) {
                
                let list = JSON.parse(localStorage.getItem('indiaExpItineraryList')) || [];
                list.push({
                    id: Date.now(),
                    destination: tripData.destination || "Custom Trip",
                    content: tripData.saveContent || finalItineraryMarkup, // Uses the rigidly pure save string
                    date: new Date().toLocaleDateString()
                });
                localStorage.setItem('indiaExpItineraryList', JSON.stringify(list));
                
                addMessage("<b>Itinerary Confirmed & Saved cleanly to your Dashboard!</b> Redirecting...", 'ai');
                chatInputContainer.style.display = 'none';
                setTimeout(() => window.location.href = '/itinerary', 2000);
            } else {
                tripData.editStr = text;
                callBackendGenerator('edit_itinerary');
            }
        }
    }

    function callBackendGenerator(reqType) {
         const typingId = 'typing-' + Date.now();
         const typingMsg = document.createElement('div');
         typingMsg.className = 'msg ai';
         typingMsg.id = typingId;
         typingMsg.innerHTML = '<i>Processing your rigorous parameters...</i>';
         chatMessages.appendChild(typingMsg);
         chatMessages.scrollTop = chatMessages.scrollHeight;

         fetch('/api/chat', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ state: tripData, reqType: reqType })
         })
         .then(r => r.json())
         .then(data => {
             document.getElementById(typingId).remove();
             finalItineraryMarkup = data.displayMarkup;
             tripData.saveContent = data.saveMarkup; // Store the separated pure itinerary internally!
             addMessage(data.displayMarkup, 'ai');
         })
         .catch(e => {
             console.error(e);
             document.getElementById(typingId).remove();
             addMessage("Sorry, I'm having trouble connecting to the network.", 'ai');
         });
    }

    if(sendBtn) sendBtn.addEventListener('click', handleUserInput);
    if(userInput) {
        userInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') handleUserInput();
        });
    }

    // ==========================================
    // PARALLAX EFFECT FOR HERO
    // ==========================================
    const heroSliderContainer = document.getElementById('hero-slider-container');
    window.addEventListener('scroll', () => {
        if(heroSliderContainer && window.scrollY < window.innerHeight) {
            heroSliderContainer.style.transform = `translateY(${window.scrollY * 0.4}px)`;
        }
    });

});
