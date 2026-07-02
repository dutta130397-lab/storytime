import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StoryTime AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --font-family: 'Inter', sans-serif;
            --text-dark: #1e293b;
            --text-light: #64748b;
            --accent: #3b82f6;
            --glass-bg: rgba(255, 255, 255, 0.45);
            --glass-border: rgba(255, 255, 255, 0.6);
            --glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-family);
            color: var(--text-dark);
            min-height: 100vh;
            /* Vibrant pastel gradient background */
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%), linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
            background-blend-mode: overlay;
            display: flex;
            overflow-x: hidden;
        }

        /* Glassmorphism Utility Class */
        .glass {
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            box-shadow: var(--glass-shadow);
        }

        /* Sidebar Navigation */
        .sidebar {
            width: 250px;
            height: calc(100vh - 2rem);
            margin: 1rem;
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            position: fixed;
            left: 0;
            top: 0;
            z-index: 100;
        }

        .sidebar h2 {
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .sidebar h2 span {
            color: var(--accent);
        }

        .nav-menu {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .nav-item {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            color: var(--text-light);
            transition: all 0.2s ease;
        }

        .nav-item:hover, .nav-item.active {
            background: rgba(255, 255, 255, 0.7);
            color: var(--text-dark);
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        /* Main Content Area */
        .main-content {
            margin-left: 270px; /* Leave space for sidebar */
            padding: 1rem 2rem 1rem 1rem;
            width: calc(100% - 270px);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            transition: margin 0.3s ease;
        }
        
        .main-content.no-sidebar {
            margin-left: 0;
            width: 100%;
            align-items: center;
            justify-content: center;
        }

        /* Pages */
        .page-section {
            display: none;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            animation: fadeIn 0.3s ease-in-out;
        }
        
        .page-section.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Forms & Inputs (Glass) */
        .glass-input, .glass-select {
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.8);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-family: var(--font-family);
            font-size: 0.95rem;
            color: var(--text-dark);
            width: 100%;
            outline: none;
            transition: all 0.2s;
        }

        .glass-input:focus, .glass-select:focus {
            background: rgba(255, 255, 255, 0.8);
            border-color: var(--accent);
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-light);
            margin-bottom: 0.25rem;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input-group {
            margin-bottom: 1.25rem;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        /* Buttons */
        .primary-btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        .primary-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }

        .primary-btn:disabled {
            background: #94a3b8;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .preview-btn {
            background: white;
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 0.75rem;
            cursor: pointer;
            margin-left: 0.5rem;
            color: var(--accent);
        }

        .voice-row {
            display: flex;
        }

        /* Layout Panels */
        .panel {
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .studio-layout {
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 2rem;
            align-items: start;
        }
        
        .studio-header {
            margin-bottom: 2rem;
        }

        /* Login Page */
        .login-card {
            max-width: 400px;
            padding: 3rem;
            text-align: center;
        }

        .login-card h2 {
            margin-bottom: 2rem;
        }

        /* Video Output & Progress */
        .videos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
        }

        .video-item {
            display: flex;
            flex-direction: column;
            background: rgba(255, 255, 255, 0.5);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid var(--glass-border);
        }

        .video-item h4 {
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        video {
            width: 100%;
            aspect-ratio: 9/16;
            background: #000;
            border-radius: 8px;
        }
        
        .download-btn {
            background: var(--text-dark);
            color: white;
            text-align: center;
            padding: 0.5rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.85rem;
            margin-top: 0.75rem;
        }

        .metadata-box {
            background: rgba(255, 255, 255, 0.6);
            padding: 0.75rem;
            border-radius: 6px;
            margin-top: 0.75rem;
            font-size: 0.8rem;
        }
        
        .metadata-box p {
            margin-bottom: 0.5rem;
        }
        .metadata-box p:last-child { margin-bottom: 0; }

        /* Progress Tracker */
        .progress-tracker {
            display: none;
            margin-bottom: 2rem;
        }

        .step {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: var(--text-light);
            font-weight: 500;
        }
        .step.active { color: var(--accent); font-weight: 600; }
        .step.done { color: var(--text-dark); }
        .step-icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-size: 0.85rem;
            border: 1px solid var(--glass-border);
        }
        .step.active .step-icon { background: var(--accent); color: white; border-color: var(--accent); }
        .step.done .step-icon { background: var(--text-dark); color: white; border-color: var(--text-dark); }
        
        #error-message {
            display: none;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            color: #ef4444;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
    </style>
</head>
<body>

    <!-- Sidebar Navigation -->
    <nav class="sidebar glass" id="sidebar" style="display: none;">
        <h2>StoryTime <span>▷</span></h2>
        <ul class="nav-menu">
            <li class="nav-item active" data-target="page-studio">🎥 Studio</li>
            <li class="nav-item" data-target="page-library">📚 Library</li>
            <li class="nav-item" data-target="page-chat">💬 Assistant</li>
            <li class="nav-item" data-target="page-campaigns">📅 Campaigns</li>
            <li class="nav-item" data-target="page-login" style="margin-top: auto; color: #ef4444;">🚪 Sign Out</li>
        </ul>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content no-sidebar" id="mainContent">
        
        <!-- PAGE 1: LOGIN -->
        <section id="page-login" class="page-section active">
            <div class="login-card glass">
                <h2>Welcome to StoryTime</h2>
                <div class="input-group">
                    <input type="email" placeholder="Email Address" class="glass-input" value="creator@storytime.ai">
                </div>
                <div class="input-group">
                    <input type="password" placeholder="Password" class="glass-input" value="password123">
                </div>
                <button id="loginBtn" class="primary-btn">Sign In</button>
            </div>
        </section>

        <!-- PAGE 4: STUDIO (Base Generation Screen) -->
        <section id="page-studio" class="page-section">
            <div class="studio-header">
                <h2>Generate New Series</h2>
                <p style="color: var(--text-light); margin-top: 0.5rem;">Configure your AI engine and parameters to generate a short-form video series.</p>
            </div>
            
            <div class="studio-layout">
                <!-- Left: Controls -->
                <div class="panel glass">
                    <div class="input-group">
                        <label for="topicInput">Premise / Topic</label>
                        <input type="text" id="topicInput" class="glass-input" placeholder="e.g. A printer that prints emails from tomorrow">
                    </div>
                    
                    <div class="input-group">
                        <label for="nicheInput">Niche / Theme</label>
                        <select id="nicheInput" class="glass-select">
                            <option value="Corporate Nightmare">Corporate Nightmare</option>
                            <option value="Sci-Fi Horror">Sci-Fi Horror</option>
                            <option value="Historical Comedy">Historical Comedy</option>
                            <option value="True Crime">True Crime Parody</option>
                            <option value="Fantasy Lore">Fantasy Lore</option>
                            <option value="Custom">Other (Type your own)</option>
                        </select>
                        <input type="text" id="customNicheInput" class="glass-input" placeholder="Enter custom niche..." style="display:none; margin-top:0.5rem;">
                    </div>
                    
                    <div class="input-group">
                        <label for="styleInput">Storytelling Style</label>
                        <select id="styleInput" class="glass-select">
                            <option value="Sarcastic & Dry">Sarcastic & Dry</option>
                            <option value="Cinematic & Epic">Cinematic & Epic</option>
                            <option value="First-Person Journal">First-Person Journal</option>
                            <option value="Documentary">Documentary</option>
                            <option value="Custom">Other (Type your own)</option>
                        </select>
                        <input type="text" id="customStyleInput" class="glass-input" placeholder="Enter custom style..." style="display:none; margin-top:0.5rem;">
                    </div>

                    <div class="input-group">
                        <label for="voiceInput">Narration Voice</label>
                        <div class="voice-row">
                            <select id="voiceInput" class="glass-select">
                                <optgroup label="American - Male">
                                    <option value="am_adam">Adam (Clear, Deep)</option>
                                    <option value="am_fenrir">Fenrir (Intense, Gruff)</option>
                                    <option value="am_michael">Michael (Warm Narrator)</option>
                                    <option value="am_onyx">Onyx (Deep)</option>
                                </optgroup>
                                <optgroup label="American - Female">
                                    <option value="af_bella">Bella (Dynamic)</option>
                                    <option value="af_sarah">Sarah (Standard)</option>
                                    <option value="af_nicole">Nicole (Suspenseful)</option>
                                </optgroup>
                                <optgroup label="British - Male">
                                    <option value="bm_george">George (Documentary)</option>
                                    <option value="bm_lewis">Lewis (Standard UK)</option>
                                </optgroup>
                            </select>
                            <button class="preview-btn" id="previewBtn" title="Play Preview">▶</button>
                        </div>
                    </div>
                    
                    <div class="form-grid">
                        <div class="input-group">
                            <label for="episodesInput">Episodes</label>
                            <input type="number" id="episodesInput" class="glass-input" value="3" min="1" max="5">
                        </div>
                        <div class="input-group">
                            <label for="llmProviderInput">AI Engine</label>
                            <select id="llmProviderInput" class="glass-select">
                                <option value="llama">Llama 3 (Groq)</option>
                                <option value="gemini">Gemini 2.5</option>
                            </select>
                        </div>
                    </div>
                    
                    <button id="generateBtn" class="primary-btn" style="margin-top: 1rem;">Generate Video Series 🚀</button>
                    <div id="error-message"></div>
                </div>
                
                <!-- Right: Output & Preview -->
                <div class="panel glass" id="outputContainer">
                    <h3 style="margin-bottom: 1.5rem;">Preview & Generation</h3>
                    
                    <div class="progress-tracker" id="progressTracker">
                        <div class="step" id="step0">
                            <div class="step-icon">0</div>
                            <div class="step-text">Series Scribe: Awaiting...</div>
                        </div>
                        <div class="step" id="step1">
                            <div class="step-icon">1</div>
                            <div class="step-text">Generation Engine: Awaiting...</div>
                        </div>
                    </div>
                    
                    <div id="outputSection" style="display: none;">
                        <div class="videos-grid" id="videosGrid"></div>
                    </div>
                    
                    <div id="emptyState" style="text-align: center; color: var(--text-light); padding: 4rem 0;">
                        <p>Fill out the form on the left to start generating.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- PAGE 2: LIBRARY -->
        <section id="page-library" class="page-section">
            <div class="panel glass">
                <h2 style="margin-bottom: 1rem;">Your Library</h2>
                <p style="color: var(--text-light); margin-bottom: 2rem;">Browse and manage your previously generated series.</p>
                
                <div style="text-align: center; padding: 4rem; border: 1px dashed var(--glass-border); border-radius: 12px;">
                    <h3 style="color: var(--text-light);">No videos found</h3>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem; color: #94a3b8;">(Phase 2 Backend Integration Pending)</p>
                </div>
            </div>
        </section>

        <!-- PAGE 3: CHAT ASSISTANT -->
        <section id="page-chat" class="page-section">
            <div class="panel glass" style="height: 80vh; display: flex; flex-direction: column;">
                <h2 style="margin-bottom: 1rem;">AI Script Assistant</h2>
                <p style="color: var(--text-light); margin-bottom: 2rem;">Brainstorm viral ideas and storylines before generating.</p>
                
                <div style="flex-grow: 1; border: 1px solid var(--glass-border); border-radius: 12px; background: rgba(255,255,255,0.3); margin-bottom: 1rem; padding: 1rem; display: flex; align-items: center; justify-content: center;">
                    <p style="color: #94a3b8;">(Phase 3 WebSocket Chat UI Pending)</p>
                </div>
                
                <div style="display: flex; gap: 1rem;">
                    <input type="text" class="glass-input" placeholder="Type your idea here...">
                    <button class="primary-btn" style="width: auto;">Send</button>
                </div>
            </div>
        </section>

        <!-- PAGE 5: CAMPAIGNS -->
        <section id="page-campaigns" class="page-section">
            <div class="panel glass">
                <h2 style="margin-bottom: 1rem;">Campaigns & Scheduling</h2>
                <p style="color: var(--text-light); margin-bottom: 2rem;">Connect your social accounts to automate uploads.</p>
                
                <div class="form-grid">
                    <div style="background: rgba(255,255,255,0.5); padding: 2rem; border-radius: 12px; text-align: center;">
                        <h3 style="margin-bottom: 1rem;">YouTube Shorts</h3>
                        <button class="primary-btn" style="background: #ef4444;">Connect YouTube Account</button>
                    </div>
                    <div style="background: rgba(255,255,255,0.5); padding: 2rem; border-radius: 12px; text-align: center;">
                        <h3 style="margin-bottom: 1rem;">Instagram Reels</h3>
                        <button class="primary-btn" style="background: #e1306c;">Connect Instagram Account</button>
                    </div>
                </div>
                
                <div style="margin-top: 2rem; text-align: center; padding: 2rem; border: 1px dashed var(--glass-border); border-radius: 12px;">
                    <h3 style="color: var(--text-light);">Schedule Calendar</h3>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem; color: #94a3b8;">(Phase 4 Backend Scheduler Pending)</p>
                </div>
            </div>
        </section>

    </main>

    <!-- Hidden audio for previews -->
    <audio id="previewAudio"></audio>

    <!-- SPA Logic & Generation API Logic -->
    <script>
        // --- SPA Router Logic ---
        const navItems = document.querySelectorAll('.nav-item');
        const sections = document.querySelectorAll('.page-section');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        const loginBtn = document.getElementById('loginBtn');

        // Mock Login Flow
        loginBtn.addEventListener('click', () => {
            document.getElementById('page-login').classList.remove('active');
            sidebar.style.display = 'flex';
            mainContent.classList.remove('no-sidebar');
            document.getElementById('page-studio').classList.add('active');
        });

        // Sidebar Navigation
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetId = item.getAttribute('data-target');
                
                if (targetId === 'page-login') {
                    // Mock Logout
                    sidebar.style.display = 'none';
                    mainContent.classList.add('no-sidebar');
                }

                // Update active state in nav
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');

                // Toggle sections
                sections.forEach(sec => sec.classList.remove('active'));
                document.getElementById(targetId).classList.add('active');
            });
        });


        // --- Original API Logic (Studio) ---
        const generateBtn = document.getElementById('generateBtn');
        const nicheInput = document.getElementById('nicheInput');
        const styleInput = document.getElementById('styleInput');
        const topicInput = document.getElementById('topicInput');
        const episodesInput = document.getElementById('episodesInput');
        const llmProviderInput = document.getElementById('llmProviderInput');
        const voiceInput = document.getElementById('voiceInput');
        const previewBtn = document.getElementById('previewBtn');
        const previewAudio = document.getElementById('previewAudio');
        const customNicheInput = document.getElementById('customNicheInput');
        const customStyleInput = document.getElementById('customStyleInput');
        
        const progressTracker = document.getElementById('progressTracker');
        const outputSection = document.getElementById('outputSection');
        const videosGrid = document.getElementById('videosGrid');
        const emptyState = document.getElementById('emptyState');
        const errorMessage = document.getElementById('error-message');
        
        let seriesData = null;

        // Custom dropdown toggles
        nicheInput.addEventListener('change', () => {
            customNicheInput.style.display = nicheInput.value === 'Custom' ? 'block' : 'none';
        });
        styleInput.addEventListener('change', () => {
            customStyleInput.style.display = styleInput.value === 'Custom' ? 'block' : 'none';
        });

        // Audio preview
        previewBtn.addEventListener('click', () => {
            const selectedVoice = voiceInput.value;
            previewAudio.src = `/output/previews/${selectedVoice}.wav`;
            previewAudio.play().catch(err => {
                alert("Preview audio not found. Run python generate_previews.py first.");
            });
        });

        function updateStep(stepNum, status, message) {
            const stepEl = document.getElementById(`step${stepNum}`);
            if (!stepEl) return;
            const textEl = stepEl.querySelector('.step-text');
            
            if (status === 'processing') {
                stepEl.className = 'step active';
                textEl.textContent = message || 'Processing...';
            } else if (status === 'done') {
                stepEl.className = 'step done';
                textEl.textContent = message || `Node ${stepNum}: Completed`;
            } else if (status === 'completed') {
                stepEl.className = 'step done';
                textEl.textContent = message || `Node ${stepNum}: Ready`;
            }
        }
        
        function resetUI() {
            emptyState.style.display = 'none';
            progressTracker.style.display = 'block';
            outputSection.style.display = 'none';
            errorMessage.style.display = 'none';
            videosGrid.innerHTML = '';
            seriesData = null;
            
            document.getElementById('step0').className = 'step';
            document.getElementById('step0').querySelector('.step-text').textContent = 'Series Scribe: Awaiting...';
            
            document.getElementById('step1').className = 'step';
            document.getElementById('step1').querySelector('.step-text').textContent = 'Generation Engine: Awaiting...';
        }

        generateBtn.addEventListener('click', async () => {
            const topic = topicInput.value.trim();
            let niche = nicheInput.value === 'Custom' ? (customNicheInput.value.trim() || 'General') : nicheInput.value;
            let style = styleInput.value === 'Custom' ? (customStyleInput.value.trim() || 'General') : styleInput.value;
            const voiceId = voiceInput.value;
            const llmProvider = llmProviderInput.value;
            const episodes = parseInt(episodesInput.value) || 3;
            
            if (!topic) {
                alert("Please enter a premise.");
                return;
            }

            generateBtn.disabled = true;
            generateBtn.textContent = "Generating...";
            resetUI();
            
            const clientId = 'client_' + Math.random().toString(36).substring(2, 15);

            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, niche, style, episodes, voice_id: voiceId, llm_provider: llmProvider, client_id: clientId })
                });

                if (!res.ok) throw new Error('Failed to start generation');

                const evtSource = new EventSource(`/api/progress/${clientId}`);

                evtSource.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.status === 'error') {
                        errorMessage.textContent = 'Error: ' + data.message;
                        errorMessage.style.display = 'block';
                        generateBtn.disabled = false;
                        generateBtn.textContent = "Generate Video Series 🚀";
                        evtSource.close();
                        return;
                    }
                    
                    if (data.step !== undefined) {
                        updateStep(data.step, data.status, data.message);
                        if (data.data) seriesData = data.data; 
                    }

                    if (data.status === 'completed' && data.video_urls) {
                        evtSource.close();
                        outputSection.style.display = 'block';
                        
                        data.video_urls.forEach((url, i) => {
                            const episodeData = seriesData && seriesData.episodes ? seriesData.episodes[i] : null;
                            const title = episodeData ? episodeData.episode_title : `Part ${i+1}`;
                            const desc = episodeData && episodeData.description ? episodeData.description : "No description generated.";
                            const tags = episodeData && episodeData.hashtags ? episodeData.hashtags : "";

                            const wrapper = document.createElement('div');
                            wrapper.className = 'video-item';
                            wrapper.innerHTML = `
                                <h4>${title}</h4>
                                <video src="${url}?t=${new Date().getTime()}" controls></video>
                                <a href="${url}" download class="download-btn">Download MP4</a>
                                <div class="metadata-box">
                                    <p><strong>Description:</strong><br>${desc}</p>
                                    <p><strong>Hashtags:</strong><br>${tags}</p>
                                </div>
                            `;
                            videosGrid.appendChild(wrapper);
                        });
                        
                        generateBtn.disabled = false;
                        generateBtn.textContent = "Generate Video Series 🚀";
                        updateStep(1, 'completed', 'All episodes generated!');
                    }
                };
            } catch (err) {
                errorMessage.textContent = 'Error: ' + err.message;
                errorMessage.style.display = 'block';
                generateBtn.disabled = false;
                generateBtn.textContent = "Generate Video Series 🚀";
            }
        });
    </script>
</body>
</html>
"""

with open('/Users/sagnikdutta/Desktop/YT_EXP_2/index.html', 'w') as f:
    f.write(HTML_CONTENT)
