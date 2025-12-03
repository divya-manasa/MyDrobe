// Analytics dashboard functionality

async function loadAnalyticsDashboard() {
  SmartStyle.showLoading();
  
  try {
    const data = await SmartStyle.apiRequest('/api/analytics/dashboard');
    displayAnalyticsDashboard(data);
    
    const insights = await SmartStyle.apiRequest('/api/analytics/insights');
    displayInsights(insights.insights);
  } catch (error) {
    SmartStyle.showAlert('Failed to load analytics', 'error');
  } finally {
    SmartStyle.hideLoading();
  }
}

function displayAnalyticsDashboard(data) {
  // Summary stats
  const summaryContainer = document.getElementById('analytics-summary');
  if (summaryContainer) {
    summaryContainer.innerHTML = `
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">${data.summary.total_items}</span>
          <span class="stat-label">Total Items</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">${data.summary.never_worn}</span>
          <span class="stat-label">Never Worn</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">$${data.summary.total_spent}</span>
          <span class="stat-label">Total Spent</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">$${data.summary.avg_cost_per_wear}</span>
          <span class="stat-label">Avg Cost/Wear</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">${data.summary.eco_score}</span>
          <span class="stat-label">Eco Score</span>
        </div>
      </div>
    `;
  }
  
  // Most worn items
  const mostWornContainer = document.getElementById('most-worn');
  if (mostWornContainer && data.most_worn) {
    mostWornContainer.innerHTML = `
      <h3>Most Worn Items</h3>
      <div class="grid grid-3">
        ${data.most_worn.map(item => `
          <div class="card">
            <h4>${item.name}</h4>
            <p>Worn ${item.wear_count} times</p>
            <span class="badge badge-color">${item.color}</span>
          </div>
        `).join('')}
      </div>
    `;
  }
  
  // Least worn items
  const leastWornContainer = document.getElementById('least-worn');
  if (leastWornContainer && data.least_worn) {
    leastWornContainer.innerHTML = `
      <h3>Least Worn Items</h3>
      <div class="grid grid-3">
        ${data.least_worn.map(item => `
          <div class="card">
            <h4>${item.name}</h4>
            <p>Worn ${item.wear_count} times</p>
            <p><small>${item.days_since_worn} days since last worn</small></p>
          </div>
        `).join('')}
      </div>
    `;
  }
  
  // Render charts
  if (data.category_distribution) {
    renderCategoryChart(data.category_distribution);
  }
  
  if (data.color_distribution) {
    renderColorChart(data.color_distribution);
  }
}

function displayInsights(insights) {
  const container = document.getElementById('ai-insights');
  if (!container || !insights) return;
  
  container.innerHTML = `
    <h3>AI-Powered Insights</h3>
    <div class="grid grid-2">
      ${insights.map(insight => `
        <div class="card">
          <h4>💡 ${insight.insight}</h4>
          <p><strong>Recommended Action:</strong> ${insight.action}</p>
        </div>
      `).join('')}
    </div>
  `;
}

function renderCategoryChart(data) {
  const canvas = document.getElementById('category-chart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const labels = Object.keys(data);
  const values = Object.values(data);
  
  // Simple bar chart
  const maxValue = Math.max(...values);
  const barWidth = canvas.width / labels.length;
  const colors = ['#2C5F7C', '#4A90A4', '#3B5F4E', '#64748B', '#2D5A4A'];
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  labels.forEach((label, index) => {
    const value = values[index];
    const barHeight = (value / maxValue) * (canvas.height - 50);
    const x = index * barWidth + 10;
    const y = canvas.height - barHeight - 30;
    
    // Draw bar
    ctx.fillStyle = colors[index % colors.length];
    ctx.fillRect(x, y, barWidth - 20, barHeight);
    
    // Draw label
    ctx.fillStyle = '#1E3A5F';
    ctx.font = '12px Inter';
    ctx.fillText(label, x, canvas.height - 10);
    
    // Draw value
    ctx.fillText(value.toString(), x, y - 5);
  });
}

function renderColorChart(data) {
  const canvas = document.getElementById('color-chart');
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const labels = Object.keys(data);
  const values = Object.values(data);
  const total = values.reduce((a, b) => a + b, 0);
  
  // Simple pie chart
  let currentAngle = 0;
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = Math.min(centerX, centerY) - 20;
  
  const colorMap = {
    'blue': '#2C5F7C',
    'black': '#1E3A5F',
    'white': '#F8F9FA',
    'gray': '#64748B',
    'green': '#3B5F4E',
    'red': '#C13838',
    'brown': '#8B4513'
  };
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  labels.forEach((label, index) => {
    const value = values[index];
    const sliceAngle = (value / total) * 2 * Math.PI;
    
    // Draw slice
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
    ctx.closePath();
    
    ctx.fillStyle = colorMap[label.toLowerCase()] || '#94A3B8';
    ctx.fill();
    
    currentAngle += sliceAngle;
  });
}
