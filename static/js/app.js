// Simple but functional JavaScript - Mobile-First

class ImageGenerator {
    constructor() {
        this.form = document.getElementById('promptForm');
        this.promptInput = document.getElementById('promptInput');
        this.generateBtn = document.getElementById('generateBtn');
        this.charCount = document.getElementById('charCount');
        this.resultArea = document.getElementById('resultArea');
        this.imageContainer = document.getElementById('imageContainer');
        this.errorMessage = document.getElementById('errorMessage');
        
        this.init();
    }
    
    init() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Character counter
        this.promptInput.addEventListener('input', () => this.updateCharCount());
        
        // Touch gestures for generated images
        this.imageContainer.addEventListener('touchstart', (e) => this.handleImageTouch(e));
        
        // Auto-resize textarea on mobile
        this.promptInput.addEventListener('input', () => this.autoResize());
        
        this.updateCharCount();
    }
    
    updateCharCount() {
        const count = this.promptInput.value.length;
        this.charCount.textContent = count;
        
        const maxLength = parseInt(this.promptInput.getAttribute('maxlength'));
        const warningThreshold = Math.floor(maxLength * 0.9);
        
        if (count > warningThreshold) {
            this.charCount.style.color = '#dc2626';
        } else {
            this.charCount.style.color = '#6b7280';
        }
    }
    
    autoResize() {
        const textarea = this.promptInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const prompt = this.promptInput.value.trim();
        if (!prompt) return;
        
        this.setLoading(true);
        this.hideError();
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Generation failed');
            }
            
            this.displayImage(data);
            
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    displayImage(data) {
        // Create image element
        const img = document.createElement('img');
        img.src = data.url;
        img.alt = data.prompt;
        img.className = 'generated-image';
        
        // Create info element
        const info = document.createElement('div');
        info.className = 'image-info';
        info.innerHTML = `
            <strong>Prompt:</strong> ${data.prompt}<br>
            <strong>Filename:</strong> ${data.filename}
        `;
        
        // Clear and populate container
        this.imageContainer.innerHTML = '';
        this.imageContainer.appendChild(img);
        this.imageContainer.appendChild(info);
        this.imageContainer.classList.add('visible');
        
        // Smooth scroll to image on mobile
        if (window.innerWidth < 768) {
            setTimeout(() => {
                this.imageContainer.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }, 100);
        }
    }
    
    handleImageTouch(e) {
        const img = e.target;
        if (img.classList.contains('generated-image')) {
            // Simple tap feedback
            img.style.transform = 'scale(0.95)';
            setTimeout(() => {
                img.style.transform = '';
            }, 150);
        }
    }
    
    setLoading(loading) {
        if (loading) {
            this.generateBtn.disabled = true;
            this.generateBtn.classList.add('loading');
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.classList.remove('loading');
        }
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.classList.add('visible');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }
    
    hideError() {
        this.errorMessage.classList.remove('visible');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ImageGenerator();
});

// Simple touch enhancement for better mobile experience
document.addEventListener('touchstart', () => {}, { passive: true });