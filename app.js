document.addEventListener('DOMContentLoaded', () => {

    const greetingText = document.getElementById('greeting');
    const heroSection = document.getElementById('hero');
    const festivalInfoText = document.getElementById('festival-info');
    const monthTitle = document.getElementById('month-special-title');
    const globalTravelerSelect = document.getElementById('global-traveler-select');

    // AUTHENTICATION LOGIC
    // AUTHENTICATION LOGIC
    let appData = null;
    let userProfile = null;
    try {
        const stored = localStorage.getItem('travelUserProfile');
        if (stored) {
            userProfile = JSON.parse(stored);
        } else {
            const legacyUser = localStorage.getItem('travelUserName');
            if (legacyUser) {
                userProfile = { username: legacyUser, email: legacyUser + "@gmail.com" };
                localStorage.setItem('travelUserProfile', JSON.stringify(userProfile));
                localStorage.removeItem('travelUserName');
            }
        }
    } catch(e) {}

    let userName = userProfile ? userProfile.username : null;

    const splashScreen = document.getElementById('splash-screen');
    const splashAudio = document.getElementById('splash-audio');
    const authLayer = document.getElementById('auth-layer');
    const authLogin = document.getElementById('auth-login');
    const authSignup = document.getElementById('auth-signup');
    const googleMockModal = document.getElementById('google-mock-modal');
    
    // Profile Dropdown Elements
    const profileMenuContainer = document.getElementById('profile-menu-container');
    const profileToggle = document.getElementById('profile-toggle');
    const profileDropdown = document.getElementById('profile-dropdown');
    const profileNameDisplay = document.getElementById('profile-name-display');
    const dropdownUsername = document.getElementById('dropdown-username');
    const dropdownEmail = document.getElementById('dropdown-email');
    const editProfileModal = document.getElementById('edit-profile-modal');

    function launchApp(profileInfo) {
        userProfile = profileInfo;
        userName = profileInfo.username;
        localStorage.setItem('travelUserProfile', JSON.stringify(userProfile));
        if(authLayer) authLayer.style.display = 'none';
        if(splashScreen) splashScreen.style.display = 'none';
        setupProfileUI();
        fetchBackendData(userName);
    }

    function setupProfileUI() {
        if(!profileMenuContainer || !userProfile) return;
        profileMenuContainer.style.display = 'inline-block';
        if(profileNameDisplay) profileNameDisplay.innerText = userProfile.username.split(' ')[0];
        if(dropdownUsername) dropdownUsername.innerText = userProfile.username;
        if(dropdownEmail) dropdownEmail.innerText = userProfile.email;
    }

    if (!userProfile) {
        if (splashAudio) {
            splashAudio.volume = 0.5;
            let playPromise = splashAudio.play();
            if (playPromise !== undefined) {
                playPromise.catch(error => { console.log("Audio autoplay prevented", error); });
            }
        }
        
        setTimeout(() => {
            if(splashScreen) {
                splashScreen.style.opacity = '0';
                setTimeout(() => {
                    splashScreen.style.display = 'none';
                    if(authLayer) authLayer.style.display = 'flex';
                }, 600);
            }
        }, 2500);

        const loginBtn = document.getElementById('login-btn');
        if(loginBtn) {
            loginBtn.addEventListener('click', () => {
                const loginIdentifier = document.getElementById('login-identifier');
                let id = loginIdentifier.value.trim() || 'Traveler';
                let username = id.includes('@') ? id.split('@')[0] : id;
                launchApp({ username: username, email: id.includes('@') ? id : username+'@gmail.com' });
            });
        }

        const signupBtn = document.getElementById('signup-btn');
        if(signupBtn) {
            signupBtn.addEventListener('click', () => {
                const signupUsername = document.getElementById('signup-username');
                const signupEmail = document.getElementById('signup-email');
                let id = signupUsername.value.trim() || 'NewTraveler';
                let email = signupEmail.value.trim() || id+'@gmail.com';
                launchApp({ username: id, email: email });
            });
        }

        document.getElementById('show-signup-btn')?.addEventListener('click', () => {
            authLogin.style.display = 'none';
            authSignup.style.display = 'block';
        });

        document.getElementById('back-to-login-btn')?.addEventListener('click', () => {
            authSignup.style.display = 'none';
            authLogin.style.display = 'block';
        });

        document.getElementById('show-forgot-btn')?.addEventListener('click', () => {
            alert("Password reset link sent to your email!");
        });

        document.getElementById('google-login-btn')?.addEventListener('click', () => {
            googleMockModal.style.display = 'flex';
        });

        document.getElementById('close-google-mock')?.addEventListener('click', () => {
            googleMockModal.style.display = 'none';
        });

        document.querySelectorAll('.google-account').forEach(acc => {
            acc.addEventListener('click', () => {
                const nameNode = acc.querySelector('strong');
                const emailNode = acc.querySelector('span');
                const pName = nameNode ? nameNode.innerText : 'GoogleUser';
                const pEmail = emailNode ? emailNode.innerText : 'user@gmail.com';
                googleMockModal.style.display = 'none';
                launchApp({ username: pName, email: pEmail });
            });
        });

    } else {
        if(splashScreen) splashScreen.style.display = 'none';
        if(authLayer) authLayer.style.display = 'none';
        setupProfileUI();
        fetchBackendData(userName);
    }

    if (profileToggle) {
        profileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('active');
        });
        
        document.addEventListener('click', (e) => {
            if(profileMenuContainer && !profileMenuContainer.contains(e.target) && profileDropdown) {
                profileDropdown.classList.remove('active');
            }
        });
    }

    const logoutBtn = document.getElementById('logout-btn');
    if(logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('travelUserProfile');
            localStorage.removeItem('travelUserName');
            window.location.reload();
        });
    }

    const switchAccountBtn = document.getElementById('switch-account-btn');
    if(switchAccountBtn) {
        switchAccountBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('travelUserProfile');
            localStorage.removeItem('travelUserName');
            window.location.reload();
        });
    }

    const editProfileBtn = document.getElementById('edit-profile-btn');
    if(editProfileBtn) {
        editProfileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if(profileDropdown) profileDropdown.classList.remove('active');
            document.getElementById('edit-username').value = userProfile.username;
            document.getElementById('edit-email').value = userProfile.email;
            if(editProfileModal) editProfileModal.style.display = 'flex';
        });
    }

    const closeEditProfile = document.getElementById('close-edit-profile');
    if(closeEditProfile) {
        closeEditProfile.addEventListener('click', () => {
            if(editProfileModal) editProfileModal.style.display = 'none';
        });
    }

    const saveProfileBtn = document.getElementById('save-profile-btn');
    if(saveProfileBtn) {
        saveProfileBtn.addEventListener('click', () => {
            const newUsername = document.getElementById('edit-username').value.trim();
            const newEmail = document.getElementById('edit-email').value.trim();
            if(newUsername) {
                userProfile.username = newUsername;
                userProfile.email = newEmail;
                launchApp(userProfile);
                if(editProfileModal) editProfileModal.style.display = 'none';
                alert("Profile successfully updated!");
            }
        });
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
