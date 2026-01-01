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
            // Get selected size and quality
            const sizeElement = document.querySelector('input[name="size"]:checked');
            const qualityElement = document.querySelector('input[name="quality"]:checked');
            const size = sizeElement ? sizeElement.value : '512x512';
            const quality = qualityElement ? qualityElement.value : 'low';
            
            // Start generation job
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    prompt: prompt,
                    size: size,
                    quality: quality
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Generation failed');
            }
            
            // Start polling for job status
            this.pollJobStatus(data.job_id, prompt);
            
        } catch (error) {
            this.showError(error.message);
            this.setLoading(false);
        }
    }
    
    async pollJobStatus(jobId, originalPrompt) {
        const maxPollingTime = 120000; // 2 minutes max
        const startTime = Date.now();
        const pollInterval = 2000; // Poll every 2 seconds
        
        const poll = async () => {
            try {
                // Check if we've been polling too long
                if (Date.now() - startTime > maxPollingTime) {
                    throw new Error('Generation timeout - please try again');
                }
                
                const response = await fetch(`/generate/status/${jobId}`);
                const status = await response.json();
                
                if (!response.ok) {
                    throw new Error(status.error || 'Failed to check status');
                }
                
                // Update progress message
                this.updateProgress(status.progress, status.message);
                
                if (status.status === 'completed') {
                    this.displayImage(status.result);
                    this.setLoading(false);
                } else if (status.status === 'failed') {
                    throw new Error(status.error || 'Generation failed');
                } else {
                    // Still processing, continue polling
                    setTimeout(poll, pollInterval);
                }
                
            } catch (error) {
                this.showError(error.message);
                this.setLoading(false);
            }
        };
        
        // Start polling
        poll();
    }
    
    updateProgress(progress, message) {
        // Update button text with progress
        const btnText = this.generateBtn.querySelector('.btn-text');
        if (btnText) {
            btnText.textContent = `${message} (${progress}%)`;
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
        const btnText = this.generateBtn.querySelector('.btn-text');
        
        if (loading) {
            this.generateBtn.disabled = true;
            this.generateBtn.classList.add('loading');
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.classList.remove('loading');
            // Reset button text
            if (btnText) {
                btnText.textContent = 'Generate Image';
            }
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