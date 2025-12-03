// ===== VOICE INPUT WITH REAL SPEECH RECOGNITION =====
let recognition = null;
let isListening = false;

// Initialize Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        isListening = true;
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        
        voiceBtn.classList.add('voice-active');
        voiceBtn.textContent = '🎙️ Listening...';
        voiceStatus.style.display = 'block';
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const promptInput = document.getElementById('prompt-input');
        
        // Replace or append based on whether textarea is empty
        if (promptInput.value.trim()) {
            promptInput.value += ' ' + transcript;
        } else {
            promptInput.value = transcript;
        }
        
        console.log('Voice input:', transcript);
    };
    
    recognition.onend = function() {
        isListening = false;
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        
        voiceBtn.classList.remove('voice-active');
        voiceBtn.textContent = '🎤 Voice Input';
        voiceStatus.style.display = 'none';
    };
    
    recognition.onerror = function(event) {
        isListening = false;
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        
        voiceBtn.classList.remove('voice-active');
        voiceBtn.textContent = '🎤 Voice Input';
        voiceStatus.style.display = 'none';
        
        if (event.error !== 'no-speech') {
            alert('Voice input error: ' + event.error);
        }
    };
}

// Voice button click handler
document.getElementById('voice-btn').onclick = function() {
    if (!recognition) {
        alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
    }
    
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
};

// ===== GENERATE OUTFIT =====
document.getElementById('generate-btn').onclick = async function() {
    const prompt = document.getElementById('prompt-input').value.trim();
    
    if (!prompt) {
        alert("Please describe your desired outfit!");
        return;
    }
    
    document.getElementById('output').innerHTML = '<div class="alert alert-info">🎨 AI is generating your outfit...</div>';
    
    try {
        const res = await fetch('/api/prompt-outfit/generate', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${SmartStyle.getToken ? SmartStyle.getToken() : ''}`
            },
            credentials: "include",
            body: JSON.stringify({
                prompt: prompt,
                occasion: null  // No occasion dropdown anymore
            })
        });
        
        if (!res.ok) throw new Error('AI outfit API failed');
        const data = await res.json();
        renderOutfitResults(data);
    } catch (err) {
        console.error(err);
        document.getElementById('output').innerHTML = '<div class="alert alert-danger">❌ AI is having trouble. Please try again!</div>';
    }
};

// ===== RENDER RESULTS =====
function renderOutfitResults(data) {
    let html = `
        <div style="margin-bottom:2em;">
            <h2>👗 AI-Generated Outfit</h2>
            <img src="${data.outfit_image}" class="img-preview" alt="AI Generated Outfit">
            <div style="font-size:1.1em;margin-top:1em;line-height:1.6;">${data.summary}</div>
        </div>
    `;
    
    html += '<div style="margin-bottom:2em;"><h2>💼 Wardrobe Match</h2><ul style="list-style:none;padding:0;">';
    data.matched_items.forEach(item => {
        html += `
            <li style="padding:0.5em 0;border-bottom:1px solid #eee;">
                <span style="font-weight:500;">${item.type}</span>, 
                <span style="color:#666;">${item.color}</span> - 
                ${item.name}
                <span class="${item.available ? 'badge-ok' : 'badge-missing'}" style="margin-left:1em;">
                    ${item.available ? '✓ Available' : '✗ Missing'}
                </span>
            </li>
        `;
    });
    html += '</ul></div>';
    
    if (data.shopping && data.shopping.length > 0) {
        html += '<div><h2>🛒 Shopping Suggestions</h2><div style="display:flex;flex-wrap:wrap;gap:1em;">';
        data.shopping.forEach(prod => {
            html += `
                <div style="border:1px solid #e0e0e0;border-radius:12px;padding:1em;width:220px;background:#fafafa;">
                    <img src="${prod.image}" alt="Product" style="width:100%;border-radius:8px;height:160px;object-fit:cover;">
                    <div style="font-weight:600;margin-top:0.5em;font-size:0.95em;">${prod.name}</div>
                    <div style="color:#19c97f;font-size:0.9em;margin-top:0.25em;">${prod.brand}</div>
                    <div style="color:#666;font-size:0.9em;margin-top:0.25em;">${prod.price}</div>
                    <a href="${prod.url}" target="_blank" class="btn btn-outline" style="margin-top:0.75em;display:inline-block;font-size:0.9em;">
                        View Product
                    </a>
                </div>
            `;
        });
        html += '</div></div>';
    }
    
    document.getElementById('output').innerHTML = html;
}
