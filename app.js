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
            loginBtn.addEventListener('click', async () => {
                const identifierInput = document.getElementById('login-identifier');
                const passwordInput = document.getElementById('login-password');
                
                const id = identifierInput.value.trim();
                const pw = passwordInput.value.trim();

                if(!id || !pw) {
                    alert("Please enter both username/email and password.");
                    return;
                }

                try {
                    const res = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ identifier: id, password: pw })
                    });
                    const data = await res.json();
                    if(res.ok) {
                        launchApp(data.user);
                    } else {
                        alert(data.error || "Login failed.");
                    }
                } catch(e) {
                    console.error("Login Error:", e);
                    alert("System error during login.");
                }
            });
        }

        const signupBtn = document.getElementById('signup-btn');
        if(signupBtn) {
            signupBtn.addEventListener('click', async () => {
                const signupUsername = document.getElementById('signup-username');
                const signupEmail = document.getElementById('signup-email');
                const signupPassword = document.getElementById('signup-password');
                const signupAge = document.getElementById('signup-age');
                const signupMobile = document.getElementById('signup-mobile');

                const user = {
                    username: signupUsername.value.trim(),
                    email: signupEmail.value.trim(),
                    password: signupPassword.value.trim(),
                    age: signupAge.value.trim(),
                    mobile: signupMobile.value.trim()
                };

                if(!user.username || !user.email || !user.password || !user.mobile) {
                    alert("Please fill in all required fields (Username, Email, Password, Mobile).");
                    return;
                }

                try {
                    const res = await fetch('/api/signup', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(user)
                    });
                    const data = await res.json();
                    if(res.ok) {
                        alert("Signup successful! You can now log in.");
                        authSignup.style.display = 'none';
                        authLogin.style.display = 'block';
                    } else {
                        alert(data.error || "Signup failed.");
                    }
                } catch(e) {
                    console.error("Signup Error:", e);
                    alert("System error during signup.");
                }
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

        // Custom rendering for Special in April Section
        const specialCarousel = document.getElementById('special-carousel');
        if (specialCarousel) {
            specialCarousel.innerHTML = '';
            const aprilFestivals = [
                { id: 'amritsar', title: 'Amritsar, Punjab', tag: 'Vaisakhi', tagline: 'Harvest Festival Celebration', img: '/assets/festivals/vaisakhi.jpg' },
                { id: 'thrissur', title: 'Thrissur, Kerala', tag: 'Thrissur Pooram', tagline: 'Grand Temple Festival', img: '/assets/festivals/thrissur_pooram.jpg' },
                { id: 'varanasi', title: 'Varanasi, Uttar Pradesh', tag: 'Ganga Aarti', tagline: 'Sacred Evening Ritual', img: '/assets/festivals/ganga_aarti.jpg' },
                { id: 'ayodhya', title: 'Ayodhya, Uttar Pradesh', tag: 'Ram Navami', tagline: 'Birth of Lord Rama Celebration', img: '/assets/festivals/ram_navami.jpg' },
                { id: 'arunachal', title: 'Arunachal Pradesh', tag: 'Mopin Festival', tagline: 'Tribal Cultural Celebration', img: '/assets/festivals/mopin_festival.jpg' },
                { id: 'madurai', title: 'Madurai, Tamil Nadu', tag: 'Chithirai Festival', tagline: 'Meenakshi Temple Celebration', img: '/assets/festivals/chithirai_festival.jpg' }
            ];
            aprilFestivals.forEach(item => {
                const cardAnchor = document.createElement('a');
                cardAnchor.href = `/city/${item.id}`;
                cardAnchor.className = 'card';
                cardAnchor.style.textDecoration = 'none';
                cardAnchor.style.color = 'inherit';
                
                let tagHTML = `<div style="position: absolute; top: 10px; right: 10px; background: linear-gradient(135deg, rgba(0,0,0,0.85), rgba(20,20,20,0.75)); color: #FFD700; padding: 6px 12px; border-radius: 8px; font-size: 14px; font-weight: 700; letter-spacing: 0.5px; text-shadow: 0px 2px 6px rgba(0,0,0,0.9); border: 1px solid rgba(255, 215, 0, 0.8); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); box-shadow: 0 0 8px rgba(255, 215, 0, 0.4); z-index: 2; pointer-events: none;">${item.tag}</div>`;
                cardAnchor.innerHTML = `${tagHTML}<img src="${item.img}" alt="${item.tag}">
                                      <div class="card-title">${item.title}</div>
                                      <div style="font-size: 13px; color: var(--text-muted, gray); margin-top: 5px;">${item.tagline}</div>`;
                specialCarousel.appendChild(cardAnchor);
            });
        }
        
        const trendingCarousel = document.getElementById('trending-carousel');
        if (trendingCarousel) {
            trendingCarousel.innerHTML = '';
            const trendingItems = [
                { id: 'manali', title: 'Manali', tag: 'Snowy Mountain Escape', badge: 'Cool Escape', img: '/assets/trending/manali.jpg' },
                { id: 'munnar', title: 'Munnar', tag: 'Tea Hills Retreat', badge: 'Tea Retreat', img: '/assets/trending/munnar.jpg' },
                { id: 'coorg', title: 'Coorg', tag: 'Coffee Nature Vibes', badge: 'Coffee Hills', img: '/assets/trending/coorg.jpg' },
                { id: 'ooty', title: 'Ooty', tag: 'Cool Hill Getaway', badge: 'Hill Getaway', img: '/assets/trending/ooty.jpg' },
                { id: 'darjeeling', title: 'Darjeeling', tag: 'Himalayan Beauty', badge: 'Mountain Views', img: '/assets/trending/darjeeling.jpg' },
                { id: 'shimla', title: 'Shimla', tag: 'Summer Hill Charm', badge: 'Summer Chill', img: '/assets/trending/shimla.jpg' }
            ];
            trendingItems.forEach(item => {
                const cardAnchor = document.createElement('a');
                cardAnchor.href = `/city/${item.id}`;
                cardAnchor.className = 'card';
                cardAnchor.style.textDecoration = 'none';
                cardAnchor.style.color = 'inherit';
                cardAnchor.style.position = 'relative'; // Ensure absolute positioning bounds correctly
                cardAnchor.innerHTML = `<div style="position: absolute; top: 10px; right: 10px; background: rgba(0, 0, 0, 0.65); color: #FFFFFF; padding: 6px 10px; border-radius: 10px; font-weight: 600; font-size: 12px; z-index: 2; pointer-events: none;">${item.badge}</div>
                                      <img src="${item.img}" alt="${item.title}">
                                      <div class="card-title">${item.title}</div>
                                      <div style="font-size: 13px; color: var(--text-muted, gray); margin-top: 5px;">${item.tag}</div>`;
                trendingCarousel.appendChild(cardAnchor);
            });
        }
        
        // Render photo-based Mood Folders
        renderMoodFolders();

        // Personalized Recommendations
        fetchRecommendations(name);

        // Traveler logic altering recommendations locally
        if(globalTravelerSelect) {
            globalTravelerSelect.addEventListener('change', () => {
                // To simulate UI feeling "alive", we re-render carousels 
                // in reality we might sort or filter the list based on family vs solo etc
                const trendCar = document.getElementById('trending-carousel');
                if(trendCar) {
                    const cards = Array.from(trendCar.children);
                    trendCar.innerHTML = '';
                    cards.reverse().forEach(c => trendCar.appendChild(c));
                }
            });
        }
    }

    async function fetchRecommendations(name) {
        const section = document.getElementById('interests-section');
        const carousel = document.getElementById('interests-carousel');
        if(!section || !carousel) return;

        try {
            const res = await fetch(`/api/user/recommendations?username=${encodeURIComponent(name)}`);
            const data = await res.json();
            if(data.recommendations && data.recommendations.length > 0) {
                section.style.display = 'block';
                renderCarousel('interests-carousel', data.recommendations);
            } else {
                section.style.display = 'none';
            }
        } catch(err) {
            console.error("Error fetching recommendations:", err);
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
    const backToTopBtn = document.getElementById('back-to-top');
    const floatingHomeBtn = document.getElementById('floating-home');

    window.addEventListener('scroll', () => {
        // Navbar scrolled state
        if(window.scrollY > 50 && navbar) {
            navbar.classList.add('scrolled');
        } else if(navbar) {
            navbar.classList.remove('scrolled');
        }

        // Floating navigation visibility
        if (window.scrollY > 300) {
            if (backToTopBtn) backToTopBtn.classList.add('show');
            if (floatingHomeBtn) floatingHomeBtn.classList.add('show');
        } else {
            if (backToTopBtn) backToTopBtn.classList.remove('show');
            if (floatingHomeBtn) floatingHomeBtn.classList.remove('show');
        }
    });

    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    if (floatingHomeBtn) {
        floatingHomeBtn.addEventListener('click', () => {
            window.location.href = '/';
        });
    }



        // ==========================================
    // NAMASTE NAVIGATOR AI AGENT
    // ==========================================
    const aiGuideBtn = document.getElementById('ai-guide');
    const chatbox = document.getElementById('chatbox');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatInputContainer = document.getElementById('chat-input-container');

    let chatOpen = false;
    let finalItineraryMarkup = "";
    
    // Core session memory for the Python NLP Engine
    let agentState = {
        messages: [],
        budget: null,
        days: null,
        interest: null,
        destination: null,
        source_location: null,
        saveContent: null,
        ready_to_save: false
    };

    function initChatStateMachine(name) {
        if(chatMessages && chatMessages.children.length === 0) {
            const sel = document.getElementById('global-traveler-select');
            let travelerType = sel ? sel.value : "2";
            agentState.people = travelerType;
            addMessage(`Namaste ${name}! I am <b>VoyageVeda</b>, your personal Agentic AI Travel Expert.<br><br>I can now perform live research, check current weather, and reason through your trip goals. How can I help you today?`, 'ai');
            agentState.messages.push(`Namaste ${name}! I am VoyageVeda, your personal Agentic AI Travel Expert. How can I help you?`);
        }
    }

    const chatBackdrop = document.getElementById('chat-backdrop');

    if(aiGuideBtn) {
        aiGuideBtn.addEventListener('click', () => {
            chatOpen = !chatOpen;
            if(chatOpen) {
                chatbox.classList.add('active');
                if(chatBackdrop) chatBackdrop.classList.add('active');
                userInput.focus();
            } else {
                chatbox.classList.remove('active');
                if(chatBackdrop) chatBackdrop.classList.remove('active');
            }
        });
    }

    if(chatBackdrop) {
        chatBackdrop.addEventListener('click', () => {
            chatOpen = false;
            chatbox.classList.remove('active');
            chatBackdrop.classList.remove('active');
        });
    }

    function addMessage(text, sender) {
        if(!chatMessages) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${sender}`;
        msgDiv.innerHTML = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Make suggestion pills clickable if any
        msgDiv.querySelectorAll('.suggestion-pills span').forEach(pill => {
            pill.style.cursor = 'pointer';
            pill.addEventListener('click', () => {
                userInput.value = pill.innerText.replace(/,$/, ''); // Remove trailing comma if exists
                handleUserInput();
            });
        });
    }

    async function handleUserInput() {
        const text = userInput.value.trim();
        if(!text) return;
        
        addMessage(text, 'user');
        agentState.messages.push(text);
        userInput.value = '';

        if(agentState.ready_to_save && (text.toLowerCase().includes('confirm') || text.toLowerCase().includes('yes') || text.toLowerCase().includes('save'))) {
            let list = JSON.parse(localStorage.getItem('indiaExpItineraryList')) || [];
            list.push({
                id: Date.now(),
                destination: agentState.destination || "Custom Trip",
                content: agentState.saveContent || finalItineraryMarkup,
                date: new Date().toLocaleDateString()
            });
            localStorage.setItem('indiaExpItineraryList', JSON.stringify(list));
            
            // Sync interests to backend for personalization
            if(userName && agentState.interest) {
                fetch('/api/user/update_interests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: userName,
                        interests: [agentState.interest]
                    })
                }).catch(err => console.error("Failed to sync interests:", err));
            }
            
            addMessage("<b>Itinerary Confirmed & Saved seamlessly to your Dashboard!</b> Redirecting...", 'ai');
            chatInputContainer.style.display = 'none';
            setTimeout(() => window.location.href = '/itinerary', 2000);
            return;
        }

        callBackendAgent(text);
    }

    function callBackendAgent(userText) {
         const typingId = 'typing-' + Date.now();
         const typingMsg = document.createElement('div');
         typingMsg.className = 'msg ai';
         typingMsg.id = typingId;
         typingMsg.innerHTML = '<i>Analyzing your request...</i>';
         chatMessages.appendChild(typingMsg);
         chatMessages.scrollTop = chatMessages.scrollHeight;

         fetch('/api/chat', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ text: userText, state: agentState })
         })
         .then(r => r.json())
         .then(data => {
             const typingElement = document.getElementById(typingId);
             if (typingElement) typingElement.remove();
             
             // Update our continuous memory
             if(data.newState) {
                 agentState = data.newState;
             }
             
             // If the agent provided reasoning, show it
             if (data.agentData && data.agentData.reasoning) {
                 const thoughtDiv = document.createElement('div');
                 thoughtDiv.className = 'msg ai thought-process';
                 thoughtDiv.style.fontSize = '12px';
                 thoughtDiv.style.opacity = '0.8';
                 thoughtDiv.style.marginBottom = '5px';
                 thoughtDiv.style.padding = '8px';
                 thoughtDiv.style.borderLeft = '3px solid var(--primary-color)';
                 thoughtDiv.style.background = 'rgba(255, 215, 0, 0.05)';
                 thoughtDiv.innerHTML = `<b>Agent Reasoning:</b> ${data.agentData.reasoning}`;
                 chatMessages.appendChild(thoughtDiv);
             }

             // Show Task Execution Plan
             if (data.agentData && data.agentData.task_plan && data.agentData.task_plan.length > 0) {
                 const planDiv = document.createElement('div');
                 planDiv.className = 'msg ai task-console';
                 planDiv.style.fontSize = '11px';
                 planDiv.style.fontFamily = 'monospace';
                 planDiv.style.color = '#FFD700';
                 planDiv.style.background = '#1a1a1a';
                 planDiv.style.padding = '10px';
                 planDiv.style.borderRadius = '8px';
                 planDiv.style.border = '1px solid #333';
                 
                 let planHTML = "<b>AUTO-AGENT EXECUTION PLAN:</b><ul style='margin:5px 0; padding-left:15px;'>";
                 data.agentData.task_plan.forEach(task => {
                     planHTML += `<li>[RUNNING] ${task}</li>`;
                 });
                 planHTML += "</ul><span style='color:#0f0'>[SUCCESS] Task sequence complete.</span>";
                 planDiv.innerHTML = planHTML;
                 chatMessages.appendChild(planDiv);
             }

             finalItineraryMarkup = data.displayMarkup;
             if(data.saveMarkup) agentState.saveContent = data.saveMarkup;
             
             addMessage(data.displayMarkup, 'ai');
         })
         .catch(e => {
             console.error(e);
             document.getElementById(typingId).remove();
             addMessage("Sorry, the AI reasoning engine is currently unreachable.", 'ai');
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
