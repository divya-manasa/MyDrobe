document.getElementById('search-btn').onclick = async () => {
    const intent = document.getElementById('intent').value.trim();
    
    if (!intent) {
        alert("Please describe what you're looking for!");
        return;
    }
    
    document.getElementById('output').innerHTML = '<div class="alert alert-info">🔍 Analyzing your wardrobe and finding matches...</div>';
    
    try {
        const res = await fetch('/api/smart-shopping/recommend', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${SmartStyle.getToken()}`
            },
            credentials: "include",
            body: JSON.stringify({
                intent: intent,
                budget_min: parseInt(document.getElementById('budget-min').value),
                budget_max: parseInt(document.getElementById('budget-max').value),
                style_preference: document.getElementById('style').value,
                color_preference: document.getElementById('color').value || null,
                sustainability: document.getElementById('sustainability').value
            })
        });
        
        if (!res.ok) throw new Error('Smart shopping API failed');
        const data = await res.json();
        renderResults(data);
    } catch (err) {
        console.error(err);
        document.getElementById('output').innerHTML = '<div class="alert alert-danger">❌ Failed to load recommendations</div>';
    }
};

function renderResults(data) {
    let html = '';
    
    // Wardrobe gaps
    if (data.gaps && data.gaps.length > 0) {
        html += '<div><h2>🔍 Wardrobe Gap Analysis</h2>';
        data.gaps.forEach(gap => {
            html += `<div class="gap-card">⚠️ ${gap}</div>`;
        });
        html += '</div>';
    }
    
    // User context
    html += `
        <div style="background: #f5f5f5; padding: 1em; border-radius: 8px; margin: 1.5em 0;">
            <strong>Your Profile:</strong> Size ${data.user_context.size} | ${data.user_context.body_shape} | 
            ${data.user_context.style} style | Budget: ${data.user_context.budget}
        </div>
    `;
    
    // Recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        html += '<div><h2>🎁 Smart Recommendations</h2><div style="display: flex; flex-wrap: wrap; gap: 1.5em;">';
        
        data.recommendations.forEach((prod, idx) => {
            html += `
                <div class="product-card">
                    <div class="match-badge">${prod.match_score}% Match</div>
                    <img src="${prod.image}" alt="${prod.name}">
                    ${prod.is_eco ? '<span class="eco-badge">♻️ Eco-Friendly</span>' : ''}
                    <div style="font-weight: 600; margin-top: 0.8em; font-size: 0.95em;">${prod.name}</div>
                    <div style="color: #666; font-size: 0.85em; margin-top: 0.3em;">${prod.brand}</div>
                    <div style="color: #19c97f; font-size: 1.2em; margin-top: 0.5em; font-weight: 600;">${prod.price}</div>
                    <div style="color: #666; font-size: 0.85em; margin-top: 0.25em;">⭐ ${prod.rating}</div>
                    
                    <ul class="match-reasons">
                        ${prod.match_reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                    
                    <a href="${prod.url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="margin-top: 1em; display: block; text-align: center; text-decoration: none;">
                        View on ${prod.store}
                    </a>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    document.getElementById('output').innerHTML = html;
}
