// AGRI-JARVIS Multilingual AI Voice Assistant for Canopy
// Powered by Google Gemini 3.5 & Web Speech API

function initJarvis() {
    // 1. Google Translate integration with direct event listening
    const script = document.createElement("script");
    script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    script.async = true;
    document.head.appendChild(script);

    window.googleTranslateElementInit = function () {
        new window.google.translate.TranslateElement({
            pageLanguage: 'en',
            includedLanguages: 'en,hi,ta,te,kn,ml,mr,bn,gu,pa,es,fr,de,ar',
            layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE
        }, 'google_translate_element');
    };

    // UI Elements
    const orb = document.createElement("div");
    orb.id = "jarvis-orb";
    orb.title = "AGRI-JARVIS: Multilingual AI Assistant (Click to talk)";
    orb.innerHTML = "<div class='orb-inner'>🎙️</div>";

    const panel = document.createElement("div");
    panel.id = "jarvis-panel";
    panel.innerHTML = `
        <div class="jarvis-header">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:18px;">🌱</span>
                <div>
                    <strong style="letter-spacing:1px; color:#9fd07a;">AGRI-JARVIS</strong>
                    <div style="font-size:9px; color:#888; font-family:var(--mono);">Multilingual Gemini AI Voice</div>
                </div>
            </div>
            <button id="jarvis-close-btn" style="background:none; border:none; color:#aaa; font-size:18px; cursor:pointer;">✕</button>
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="font-size:10px; color:#aaa; margin-bottom:4px; text-transform:uppercase; font-family:var(--mono);">Language / மொழி / भाषा:</div>
            <div id="google_translate_element"></div>
        </div>

        <div class="jarvis-status-row">
            <span id="jarvis-indicator" class="idle">&#9679; Ready</span>
            <span id="jarvis-model-tag" style="font-size:9px; color:#7bbf4a; font-family:var(--mono);">Gemini 3.5 Online</span>
        </div>

        <div id="jarvis-transcript" aria-live="polite">Click the mic or speak: "What is this field's NDVI?" or "zoom in"</div>
        <div id="jarvis-response"></div>

        <div class="jarvis-input-bar">
            <input id="jarvis-text-input" type="text" placeholder="Or type in Tamil, Hindi, English..." autocomplete="off" />
            <button id="jarvis-send-btn">Send</button>
            <button id="jarvis-speak-btn" title="Speak Response" style="background:#2a2019; border:1px solid #5a4a3a; border-radius:4px; color:#9fd07a; cursor:pointer; padding:0 8px;">🔊</button>
        </div>
    `;

    document.body.appendChild(orb);
    document.body.appendChild(panel);

    const closeBtn = document.getElementById("jarvis-close-btn");
    if (closeBtn) closeBtn.onclick = () => panel.classList.remove('open');

    // 2. Speech Recognition Logic
    let recognition = null;
    let isListening = false;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
    } else {
        const transcriptEl = document.getElementById('jarvis-transcript');
        if (transcriptEl) transcriptEl.innerText = "Voice input unsupported in this browser. Type your query below!";
    }

    function getCurrentLanguage() {
        const langCombo = document.querySelector('.goog-te-combo');
        const lang = langCombo ? langCombo.value : 'en';
        return lang || 'en';
    }

    function getSpeechLang(langCode) {
        const langMap = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'mr': 'mr-IN',
            'bn': 'bn-IN',
            'gu': 'gu-IN',
            'pa': 'pa-IN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'ar': 'ar-SA'
        };
        return langMap[langCode] || 'en-IN';
    }

    function toggleListening() {
        if (!recognition) {
            panel.classList.add("open");
            return;
        }

        if (isListening) {
            recognition.stop();
            orb.classList.remove('listening');
            isListening = false;
            setIndicator("idle", "Ready");
        } else {
            panel.classList.add("open");
            const lang = getCurrentLanguage();
            recognition.lang = getSpeechLang(lang);

            try {
                recognition.start();
                orb.classList.add('listening');
                document.getElementById('jarvis-transcript').innerText = "Listening in " + (recognition.lang) + "...";
                setIndicator("listening", "Listening...");
                isListening = true;
            } catch (err) {
                console.warn("Speech recognition error:", err);
            }
        }
    }

    orb.addEventListener("click", toggleListening);

    function setIndicator(state, label) {
        const ind = document.getElementById('jarvis-indicator');
        if (!ind) return;
        ind.className = state;
        ind.innerHTML = `&#9679; ${label}`;
    }

    if (recognition) {
        recognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript;
            document.getElementById('jarvis-transcript').innerText = `"${transcript}"`;

            if (event.results[event.results.length - 1].isFinal) {
                isListening = false;
                orb.classList.remove('listening');
                setIndicator("thinking", "Gemini AI Thinking...");
                processCommand(transcript);
            }
        };

        recognition.onerror = (e) => {
            isListening = false;
            orb.classList.remove('listening');
            setIndicator("idle", "Ready");
            console.warn("Speech recognition error event:", e);
        };

        recognition.onend = () => {
            if (isListening) {
                isListening = false;
                orb.classList.remove('listening');
                setIndicator("idle", "Ready");
            }
        };
    }

    // 3. Command Processing & Telemetry Context Extraction
    function getActiveTelemetryContext() {
        try {
            const ndvi = document.getElementById('p-ndvi')?.textContent;
            const temp = document.getElementById('p-temp')?.textContent;
            const moisture = document.getElementById('p-humidity')?.textContent;
            const cropType = document.getElementById('p-crop-type')?.textContent;
            const coords = document.getElementById('p-coords')?.textContent;
            const badge = document.getElementById('p-badge-text')?.textContent;
            const csi = document.getElementById('p-ml-csi')?.textContent;

            if (ndvi && ndvi !== '—') {
                return {
                    status: badge,
                    ndvi: ndvi,
                    temperature: temp,
                    soilMoisture: moisture,
                    cropClassification: cropType,
                    coordinates: coords,
                    cropStressIndex: csi
                };
            }
        } catch (_) {}
        return null;
    }

    let lastSpokenText = "";

    function processCommand(text) {
        const lang = getCurrentLanguage();
        const telemetry = getActiveTelemetryContext();

        setIndicator("thinking", "Gemini AI Thinking...");

        fetch("/api/assistant", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, lang: lang, telemetry: telemetry })
        })
        .then(res => res.json())
        .then(data => {
            setIndicator("idle", "Online");
            const responseDiv = document.getElementById('jarvis-response');
            responseDiv.innerHTML = `<span style="color:#9fd07a;">🤖 </span>${data.text}`;
            lastSpokenText = data.text;

            if (data.model) {
                const modelTag = document.getElementById('jarvis-model-tag');
                if (modelTag) modelTag.innerText = data.model;
            }

            // Speak response in matching language
            speak(data.text, lang);

            // Execute UI actions if returned
            if (data.actions && Array.isArray(data.actions)) {
                data.actions.forEach(action => {
                    if (action.type === 'zoom_map' && window.map) {
                        window.map.zoomIn(action.level || 1);
                    } else if (action.type === 'reset_globe' && typeof window.resetToGlobe === 'function') {
                        window.resetToGlobe();
                    } else if (action.type === 'filter_by_risk') {
                        const searchInput = document.getElementById('pac-input');
                        if (searchInput) searchInput.value = 'Farmland High Risk Focus';
                    }
                });
            }
        })
        .catch(e => {
            console.error("Jarvis fetch error:", e);
            setIndicator("idle", "Offline");
            document.getElementById('jarvis-response').innerText = "Assistant connection offline. Please check network.";
        });
    }

    // 4. Multilingual Speech Synthesis (TTS)
    function speak(text, lang) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel(); // barge-in / clear prior speech

        // Clean out emojis or markdown asterisks before TTS
        const cleanText = text.replace(/[*#_~`]|[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F700}-\u{1F77F}]|[\u{1F780}-\u{1F7FF}]|[\u{1F800}-\u{1F8FF}]|[\u{1F900}-\u{1F9FF}]|[\u{1FA00}-\u{1FA6F}]|[\u{1FA70}-\u{1FAFF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '');
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = getSpeechLang(lang);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        // Try to select an accent voice if matching
        const voices = window.speechSynthesis.getVoices();
        const targetPrefix = utterance.lang.slice(0, 2);
        const matchVoice = voices.find(v => v.lang.startsWith(targetPrefix));
        if (matchVoice) utterance.voice = matchVoice;

        window.speechSynthesis.speak(utterance);
    }

    // 5. Text Input Submission
    const textInput = document.getElementById('jarvis-text-input');
    const sendBtn = document.getElementById('jarvis-send-btn');
    const speakBtn = document.getElementById('jarvis-speak-btn');

    function sendTextMessage() {
        const val = (textInput?.value || '').trim();
        if (!val) return;
        document.getElementById('jarvis-transcript').innerText = `"${val}"`;
        textInput.value = '';
        processCommand(val);
    }

    if (sendBtn) sendBtn.onclick = sendTextMessage;
    if (textInput) {
        textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendTextMessage();
        });
    }
    if (speakBtn) {
        speakBtn.onclick = () => {
            if (lastSpokenText) speak(lastSpokenText, getCurrentLanguage());
        };
    }
}

// Inject styling for Orb, Floating Assistant Panel and Language controls
const styles = document.createElement('style');
styles.innerHTML = `
    #jarvis-orb {
        position: fixed;
        bottom: 25px;
        left: 25px;
        width: 58px;
        height: 58px;
        background: radial-gradient(circle, #10b981, #047857);
        border: 2px solid rgba(159, 208, 122, 0.5);
        border-radius: 50%;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.6);
        cursor: pointer;
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s;
    }
    #jarvis-orb:hover {
        transform: scale(1.08);
        box-shadow: 0 0 35px rgba(16, 185, 129, 0.85);
    }
    #jarvis-orb.listening {
        animation: pulse-ring-jarvis 1.1s infinite;
        background: radial-gradient(circle, #ef4444, #b91c1c);
        border-color: #f87171;
    }
    @keyframes pulse-ring-jarvis {
        0% { transform: scale(0.96); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 14px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.96); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    #jarvis-panel {
        position: fixed;
        bottom: -600px;
        left: 25px;
        width: min(360px, calc(100vw - 40px));
        background: rgba(26, 20, 16, 0.94);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid #3e5a2c;
        border-radius: 12px;
        padding: 16px;
        z-index: 9999;
        transition: bottom 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        color: #f2ecdf;
        font-family: var(--sans, system-ui);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.75);
    }
    #jarvis-panel.open {
        bottom: 95px;
    }
    .jarvis-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
    }
    .jarvis-status-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        margin-bottom: 8px;
    }
    #jarvis-indicator.idle { color: #888; }
    #jarvis-indicator.listening { color: #ef4444; font-weight: bold; }
    #jarvis-indicator.thinking { color: #eab308; font-style: italic; }
    #jarvis-transcript {
        font-family: var(--mono, monospace);
        font-style: italic;
        color: #aaa;
        font-size: 12px;
        background: rgba(0, 0, 0, 0.3);
        padding: 8px 10px;
        border-radius: 6px;
        min-height: 28px;
        border: 1px dashed rgba(255, 255, 255, 0.1);
    }
    #jarvis-response {
        margin-top: 10px;
        font-size: 13px;
        line-height: 1.45;
        max-height: 130px;
        overflow-y: auto;
        padding: 4px 0;
    }
    .jarvis-input-bar {
        display: flex;
        gap: 6px;
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    #jarvis-text-input {
        flex: 1;
        background: #111;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 6px 10px;
        color: #fff;
        font-size: 12px;
        outline: none;
    }
    #jarvis-text-input:focus {
        border-color: #9fd07a;
    }
    #jarvis-send-btn {
        background: #2a2019;
        border: 1px solid #5a4a3a;
        color: #e9e2d4;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 12px;
        cursor: pointer;
    }
    #jarvis-send-btn:hover {
        border-color: #9fd07a;
        color: #9fd07a;
    }
    /* Google Translate Styling */
    .goog-te-banner-frame, .goog-logo-link { display: none !important; }
    body { top: 0 !important; }
    .goog-te-gadget { color: transparent !important; font-size: 0px !important; }
    .goog-te-combo {
        width: 100%;
        background: #181410 !important;
        color: #f2ecdf !important;
        border: 1px solid #3e5a2c !important;
        border-radius: 6px !important;
        padding: 6px 8px !important;
        font-size: 12px !important;
        cursor: pointer;
        outline: none;
    }
    .goog-te-combo:focus {
        border-color: #9fd07a !important;
    }
    .skiptranslate.goog-te-gadget > span { display: none !important; }
`;
document.head.appendChild(styles);

window.addEventListener('load', initJarvis);
