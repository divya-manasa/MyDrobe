// Chart rendering utilities using Canvas API

class ChartRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width;
    this.height = this.canvas.height;
  }
  
  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
  }
  
  drawBarChart(data, options = {}) {
    this.clear();
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    const maxValue = Math.max(...values);
    const barWidth = this.width / labels.length;
    const colors = options.colors || [
      '#2C5F7C', '#4A90A4', '#3B5F4E', '#64748B', '#2D5A4A'
    ];
    
    labels.forEach((label, index) => {
      const value = values[index];
      const barHeight = (value / maxValue) * (this.height - 60);
      const x = index * barWidth + 20;
      const y = this.height - barHeight - 40;
      
      // Draw bar with gradient
      const gradient = this.ctx.createLinearGradient(x, y, x, y + barHeight);
      gradient.addColorStop(0, colors[index % colors.length]);
      gradient.addColorStop(1, this.adjustColor(colors[index % colors.length], -20));
      
      this.ctx.fillStyle = gradient;
      this.ctx.fillRect(x, y, barWidth - 30, barHeight);
      
      // Draw label
      this.ctx.fillStyle = '#1E3A5F';
      this.ctx.font = '12px Inter';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(label, x + (barWidth - 30) / 2, this.height - 20);
      
      // Draw value
      this.ctx.fillStyle = '#2C5F7C';
      this.ctx.font = 'bold 14px Inter';
      this.ctx.fillText(value.toString(), x + (barWidth - 30) / 2, y - 10);
    });
  }
  
  drawPieChart(data, options = {}) {
    this.clear();
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    const total = values.reduce((a, b) => a + b, 0);
    
    let currentAngle = -Math.PI / 2; // Start from top
    const centerX = this.width / 2;
    const centerY = this.height / 2;
    const radius = Math.min(centerX, centerY) - 40;
    
    const colorMap = {
      'blue': '#2C5F7C',
      'black': '#1E3A5F',
      'white': '#F8F9FA',
      'gray': '#64748B',
      'green': '#3B5F4E',
      'red': '#C13838',
      'brown': '#8B4513',
      'pink': '#E91E63',
      'yellow': '#FFC107',
      'purple': '#9C27B0'
    };
    
    const colors = options.colors || Object.values(colorMap);
    
    labels.forEach((label, index) => {
      const value = values[index];
      const sliceAngle = (value / total) * 2 * Math.PI;
      
      // Draw slice
      this.ctx.beginPath();
      this.ctx.moveTo(centerX, centerY);
      this.ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      this.ctx.closePath();
      
      this.ctx.fillStyle = colorMap[label.toLowerCase()] || colors[index % colors.length];
      this.ctx.fill();
      this.ctx.strokeStyle = '#fff';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
      
      // Draw label
      const labelAngle = currentAngle + sliceAngle / 2;
      const labelX = centerX + Math.cos(labelAngle) * (radius + 30);
      const labelY = centerY + Math.sin(labelAngle) * (radius + 30);
      
      this.ctx.fillStyle = '#1E3A5F';
      this.ctx.font = '12px Inter';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(label, labelX, labelY);
      
      currentAngle += sliceAngle;
    });
  }
  
  drawLineChart(data, options = {}) {
    this.clear();
    
    const labels = Object.keys(data);
    const values = Object.values(data);
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const range = maxValue - minValue;
    
    const padding = 50;
    const chartWidth = this.width - padding * 2;
    const chartHeight = this.height - padding * 2;
    const pointSpacing = chartWidth / (labels.length - 1);
    
    // Draw axes
    this.ctx.strokeStyle = '#64748B';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(padding, padding);
    this.ctx.lineTo(padding, this.height - padding);
    this.ctx.lineTo(this.width - padding, this.height - padding);
    this.ctx.stroke();
    
    // Draw line
    this.ctx.strokeStyle = '#2C5F7C';
    this.ctx.lineWidth = 3;
    this.ctx.beginPath();
    
    values.forEach((value, index) => {
      const x = padding + index * pointSpacing;
      const y = this.height - padding - ((value - minValue) / range) * chartHeight;
      
      if (index === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    });
    
    this.ctx.stroke();
    
    // Draw points
    values.forEach((value, index) => {
      const x = padding + index * pointSpacing;
      const y = this.height - padding - ((value - minValue) / range) * chartHeight;
      
      this.ctx.fillStyle = '#4A90A4';
      this.ctx.beginPath();
      this.ctx.arc(x, y, 5, 0, 2 * Math.PI);
      this.ctx.fill();
      
      // Draw labels
      this.ctx.fillStyle = '#1E3A5F';
      this.ctx.font = '10px Inter';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(labels[index], x, this.height - padding + 20);
    });
  }
  
  adjustColor(color, amount) {
    return '#' + color.replace(/^#/, '').replace(/../g, color => 
      ('0' + Math.min(255, Math.max(0, parseInt(color, 16) + amount)).toString(16)).substr(-2)
    );
  }
}

// Export for use
window.ChartRenderer = ChartRenderer;
