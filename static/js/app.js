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
        console.log('ImageGenerator initialized');
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
        
        // Advanced panel toggle
        this.initAdvancedPanel();
        
        this.updateCharCount();
    }

    initAdvancedPanel() {
        const toggle = document.getElementById('advancedToggle');
        const content = document.getElementById('advancedContent');
        
        console.log('Advanced panel elements:', { toggle, content });
        
        if (toggle && content) {
            toggle.addEventListener('click', () => {
                console.log('Advanced panel clicked');
                toggle.classList.toggle('expanded');
                content.classList.toggle('expanded');
                console.log('Classes after toggle:', {
                    toggleClasses: toggle.className,
                    contentClasses: content.className
                });
            });
        } else {
            console.error('Advanced panel elements not found:', { toggle, content });
        }
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
            
            // Get advanced parameters (only if specified by user)
            const seedInput = document.getElementById('seedInput');
            const seed = seedInput && seedInput.value.trim() !== '' ? parseInt(seedInput.value) : null;
            
            console.log('Starting generation:', { size, quality, seed: seed || 'random' });
            
            // Build request payload - only include advanced params if user specified them
            const payload = { 
                prompt: prompt,
                size: size,
                quality: quality
            };
            
            if (seed !== null) {
                payload.seed = seed;
            }
            
            // Start generation job
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Generation failed');
            }
            
            if (!data.job_id) {
                throw new Error('No job ID received from server');
            }
            
            // Start polling for job status
            this.pollJobStatus(data.job_id, prompt);
            
        } catch (error) {
            this.showError(error.message);
            this.setLoading(false);
        }
    }
    
    async pollJobStatus(jobId, originalPrompt) {
        console.log(`Starting polling for job: ${jobId}`);
        const startTime = Date.now();
        let retryCount = 0;
        
        const poll = async () => {
            const elapsed = Date.now() - startTime;
            
            try {
                if (elapsed > window.APP_CONFIG.polling.maxTimeMs) {
                    throw new Error(`Generation timeout after ${Math.round(elapsed/1000)} seconds`);
                }
                
                const response = await fetch(`/generate/status/${jobId}`);
                const status = await response.json();
                
                if (!response.ok) {
                    throw new Error(status.error || 'Failed to check status');
                }
                
                retryCount = 0;
                this.updateProgress(status.progress, status.message);
                
                if (status.status === 'completed') {
                    this.displayImage(status.result);
                    this.setLoading(false);
                } else if (status.status === 'failed') {
                    throw new Error(status.error || 'Generation failed');
                } else {
                    setTimeout(poll, window.APP_CONFIG.polling.intervalMs);
                }
                
            } catch (error) {
                retryCount++;
                if (retryCount <= window.APP_CONFIG.polling.maxRetries) {
                    setTimeout(poll, window.APP_CONFIG.polling.intervalMs);
                } else {
                    this.showError(error.message);
                    this.setLoading(false);
                }
            }
        };
        
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
        
        const seedInfo = data.user_seed !== null 
            ? `${data.seed} (user specified)` 
            : `${data.seed} (random)`;
        
        info.innerHTML = `
            <strong>Prompt:</strong> ${data.prompt}<br>
            <strong>Size:</strong> ${data.size} • <strong>Quality:</strong> ${data.quality}<br>
            <strong>Seed:</strong> ${seedInfo}<br>
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