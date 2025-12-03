// Global state
let currentAnalysis = null;
let currentImagePreview = null;
let currentEditingItemId = null;

// SmartStyle Helper Object
const SmartStyle = {
    showAlert(message, type = 'success') {
        const alertEl = document.getElementById('alert');
        if (!alertEl) return;
        
        alertEl.textContent = message;
        alertEl.className = `alert ${type}`;
        alertEl.style.display = 'block';
        
        setTimeout(() => {
            alertEl.style.display = 'none';
        }, 4000);
    },

    showLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'block';
    },

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
    }
};

// ========================================
// INITIALIZE
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎉 SmartStyle AI Initialized');
    
    // Upload area click
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.background = '#f0f0f0';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.background = '#f9f9f9';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.background = '#f9f9f9';
            handleFileSelect({ target: { files: e.dataTransfer.files } });
        });
    }
    
    // File input change
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Form submit
    const form = document.getElementById('item-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            handleFormSubmit();
        });
    }
    
    // Modal close
    const closeBtn = document.getElementById('view-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeViewModal);
    }
    
    window.addEventListener('click', (event) => {
        const modal = document.getElementById('view-modal');
        if (event.target === modal) {
            closeViewModal();
        }
    });
    
    // Load initial wardrobe
    loadWardrobe();
});

// ========================================
// UPLOAD & ANALYZE
// ========================================

async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        SmartStyle.showAlert('Please upload an image file (JPEG/PNG/GIF)', 'error');
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        currentImagePreview = e.target.result;
        document.getElementById('image-preview').src = e.target.result;
        document.getElementById('preview-container').style.display = 'block';
        document.getElementById('analysis-status').textContent = '✨ AI Detected Clothing Details...';
    };
    reader.readAsDataURL(file);
    
    // Analyze with AI
    const formData = new FormData();
    formData.append('file', file);
    
    SmartStyle.showLoading();
    
    try {
        console.log('📸 Uploading image for analysis...');
        const response = await fetch('/api/wardrobe/analyze-image', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const analysis = await response.json();
        console.log('✅ AI Analysis Complete:', analysis);
        
        currentAnalysis = analysis;
        
        // Show analysis status
        document.getElementById('analysis-status').innerHTML = `
            <strong>✨ AI Detected Occasions:</strong><br>
            ${(analysis.occasions || []).join(', ') || 'casual'}
        `;
        
        // Auto-fill form
        fillFormWithAnalysis(analysis);
        
        SmartStyle.hideLoading();
        SmartStyle.showAlert('✅ Image analyzed! Review and save.', 'success');
        
    } catch (error) {
        console.error('❌ Analysis error:', error);
        SmartStyle.hideLoading();
        SmartStyle.showAlert('Failed to analyze image. Please try again.', 'error');
        document.getElementById('analysis-status').textContent = '❌ Analysis failed. Try uploading again.';
    }
}

// ========================================
// FORM HELPERS
// ========================================

function fillFormWithAnalysis(analysis) {
    console.log('📝 Filling form with:', analysis);
    
    document.getElementById('item-name').value = analysis.itemname || '';
    document.getElementById('category').value = analysis.category || '';
    document.getElementById('subcategory').value = analysis.subcategory || '';
    document.getElementById('color').value = analysis.color || '';
    document.getElementById('pattern').value = analysis.pattern || '';
    document.getElementById('fabric').value = analysis.fabric || '';
    document.getElementById('style').value = analysis.style || '';
    document.getElementById('season').value = analysis.season || '';
    document.getElementById('gender').value = (analysis.gender || 'unisex').toLowerCase();
    document.getElementById('occasions').value = (analysis.occasions || []).join(', ');
    
    // ✅ STORE IMAGE PATH FOR LATER USE
    document.getElementById('item-form').setAttribute('data-image-url', analysis.temp_image_path);
    
    // Show form section
    document.getElementById('form-section').style.display = 'block';
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}

function fillMainFormForEdit(item) {
    console.log('✏️ Editing item:', item);
    
    currentEditingItemId = item.id;
    
    document.getElementById('item-name').value = item.name || '';
    document.getElementById('category').value = item.category || '';
    document.getElementById('subcategory').value = item.subcategory || '';
    document.getElementById('color').value = item.color || '';
    document.getElementById('pattern').value = item.pattern || '';
    document.getElementById('fabric').value = item.fabric || '';
    document.getElementById('style').value = item.style || '';
    document.getElementById('season').value = item.season || '';
    document.getElementById('brand').value = item.brand || '';
    document.getElementById('gender').value = (item.gender || 'unisex').toLowerCase();
    document.getElementById('occasions').value = 
        Array.isArray(item.occasions) ? item.occasions.join(', ') : (item.occasions || '');
    
    // ✅ KEEP EXISTING IMAGE
    document.getElementById('item-form').setAttribute('data-image-url', item.image_url || '');
    
    // Show form section
    document.getElementById('form-section').style.display = 'block';
    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}

// ========================================
// FORM SUBMIT (CREATE / UPDATE)
// ========================================

async function handleFormSubmit() {
    console.log('💾 Saving item...');
    
    // Get image URL from form data attribute
    const imageUrl = document.getElementById('item-form').getAttribute('data-image-url') || '';
    
    const itemData = {
        name: document.getElementById('item-name').value || '',
        category: document.getElementById('category').value || '',
        subcategory: document.getElementById('subcategory').value || '',
        color: document.getElementById('color').value || '',
        pattern: document.getElementById('pattern').value || '',
        fabric: document.getElementById('fabric').value || '',
        style: document.getElementById('style').value || '',
        season: document.getElementById('season').value || '',
        brand: document.getElementById('brand').value || '',
        gender: document.getElementById('gender').value || 'unisex',
        occasions: document.getElementById('occasions').value
            .split(',')
            .map(s => s.trim())
            .filter(s => s),
        image_url: imageUrl  // ✅ INCLUDE IMAGE URL!
    };
    
    // Validation
    if (!itemData.name || !itemData.category) {
        SmartStyle.showAlert('Please fill in Name and Category', 'error');
        return;
    }
    
    try {
        if (currentEditingItemId) {
            // UPDATE existing item
            console.log('🔄 Updating item', currentEditingItemId);
            const response = await fetch(`/api/wardrobe/items/${currentEditingItemId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(itemData)
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Update failed: ${error}`);
            }
            
            SmartStyle.showAlert('✅ Outfit updated successfully!', 'success');
            currentEditingItemId = null;
            
        } else {
            // CREATE new item
            console.log('✨ Creating new item', itemData);
            const response = await fetch('/api/wardrobe/items', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(itemData)
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Create failed: ${error}`);
            }
            
            SmartStyle.showAlert('✅ Outfit saved to wardrobe!', 'success');
        }
        
        // Reset form and reload
        document.getElementById('item-form').reset();
        document.getElementById('form-section').style.display = 'none';
        document.getElementById('preview-container').style.display = 'none';
        document.getElementById('file-input').value = '';
        
        loadWardrobe();
        
    } catch (error) {
        console.error('❌ Save error:', error);
        SmartStyle.showAlert('Failed to save outfit. Please try again.', 'error');
    }
}

// ========================================
// WARDROBE DISPLAY & MANAGEMENT
// ========================================

async function loadWardrobe() {
    try {
        console.log('📦 Loading wardrobe items...');
        const response = await fetch('/api/wardrobe/items');
        
        if (!response.ok) throw new Error('Failed to fetch items');
        
        const items = await response.json();
        console.log(`✅ Loaded ${items.length} items`);
        
        const grid = document.getElementById('wardrobe-grid');
        if (!grid) return;
        
        if (!items || items.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #999;">
                    <p style="font-size: 48px; margin-bottom: 10px;">📦</p>
                    <p>No items yet. Upload your first item!</p>
                    <p style="font-size: 12px; margin-top: 10px;">Upload images and let AI auto-detect clothing details</p>
                </div>
            `;
            return;
        }
        
        // ✅ SHOW ACTUAL IMAGE OR DEFAULT ICON
        grid.innerHTML = items.map(item => {
            const imageUrl = item.image_url ? `background-image: url('${item.image_url}'); background-size: cover; background-position: center;` : '';
            const displayContent = item.image_url 
                ? '' 
                : '<div class="item-icon">👕</div>';
            
            return `
                <div class="wardrobe-card">
                    <div class="item-preview" style="${imageUrl}">
                        ${displayContent}
                    </div>
                    <h3>${item.name || 'Untitled'}</h3>
                    <p style="color: #999; font-size: 12px;">${item.color || 'N/A'}</p>
                    <p style="color: #999; font-size: 12px;">${item.category || 'N/A'}</p>
                    <div class="card-actions">
                        <button class="btn-secondary" onclick="viewItem(${item.id})">👁️ View</button>
                        <button class="btn-delete" onclick="deleteItem(${item.id})">🗑️ Delete</button>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('❌ Load wardrobe error:', error);
        const grid = document.getElementById('wardrobe-grid');
        if (grid) {
            grid.innerHTML = '<p style="color: red;">⚠️ Failed to load items. Please refresh.</p>';
        }
    }
}

// ========================================
// VIEW MODAL
// ========================================

async function viewItem(itemId) {
    try {
        console.log('👀 Viewing item', itemId);
        const response = await fetch(`/api/wardrobe/items/${itemId}`);
        
        if (!response.ok) throw new Error(`Item not found`);
        
        const item = await response.json();
        console.log('📄 Item details:', item);
        
        // ✅ SHOW ACTUAL IMAGE OR FALLBACK
        const imageElement = document.getElementById('view-image');
        if (item.image_url) {
            imageElement.src = item.image_url;
            imageElement.style.display = 'block';
        } else {
            // Fallback SVG if no image
            imageElement.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300"%3E%3Crect fill="%23f0f0f0" width="300" height="300"/%3E%3Ctext x="50%25" y="50%25" font-size="120" fill="%23999" text-anchor="middle" dy=".3em"%3E👕%3C/text%3E%3C/svg%3E';
            imageElement.style.display = 'block';
        }
        
        // ✅ POPULATE ALL DETAILS
        document.getElementById('view-name').textContent = item.name || 'No Name';
        document.getElementById('view-category').textContent = item.category || 'N/A';
        document.getElementById('view-subcategory').textContent = item.subcategory || 'N/A';
        document.getElementById('view-color').textContent = item.color || 'N/A';
        document.getElementById('view-pattern').textContent = item.pattern || 'N/A';
        document.getElementById('view-fabric').textContent = item.fabric || 'N/A';
        document.getElementById('view-style').textContent = item.style || 'N/A';
        document.getElementById('view-season').textContent = item.season || 'N/A';
        document.getElementById('view-brand').textContent = item.brand || 'N/A';
        document.getElementById('view-gender').textContent = item.gender || 'N/A';
        document.getElementById('view-occasions').textContent = 
            Array.isArray(item.occasions) && item.occasions.length > 0
                ? item.occasions.join(', ') 
                : 'N/A';
        
        // Edit button handler
        const editBtn = document.getElementById('edit-button');
        if (editBtn) {
            editBtn.onclick = () => {
                fillMainFormForEdit(item);
                closeViewModal();
            };
        }
        
        // Show modal
        document.getElementById('view-modal').style.display = 'block';
        
    } catch (error) {
        console.error('❌ View error:', error);
        SmartStyle.showAlert('Failed to load outfit details', 'error');
    }
}

function closeViewModal() {
    document.getElementById('view-modal').style.display = 'none';
}

// ========================================
// DELETE
// ========================================

async function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this outfit?')) return;
    
    try {
        console.log('🗑️ Deleting item', itemId);
        const response = await fetch(`/api/wardrobe/items/${itemId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Delete failed');
        
        SmartStyle.showAlert('✅ Outfit deleted!', 'success');
        loadWardrobe();
        
    } catch (error) {
        console.error('❌ Delete error:', error);
        SmartStyle.showAlert('Failed to delete outfit', 'error');
    }
}