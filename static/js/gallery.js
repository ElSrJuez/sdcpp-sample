// Gallery JavaScript - Mobile-First with Touch Support

class Gallery {
    constructor() {
        this.currentPage = 1;
        this.loading = false;
        this.hasMore = true;
        this.images = [];
        this.currentImageIndex = 0;
        
        this.initElements();
        this.initEventListeners();
        this.loadGallery();
        this.loadStats();
    }
    
    initElements() {
        this.galleryGrid = document.getElementById('galleryGrid');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.loadMoreContainer = document.getElementById('loadMoreContainer');
        this.emptyState = document.getElementById('emptyState');
        this.galleryStats = document.getElementById('galleryStats');
        
        // Modal elements
        this.modal = document.getElementById('imageModal');
        this.modalImage = document.getElementById('modalImage');
        this.modalClose = document.getElementById('modalClose');
        this.modalBackdrop = document.getElementById('modalBackdrop');
        this.modalPrev = document.getElementById('modalPrev');
        this.modalNext = document.getElementById('modalNext');
        this.imageMeta = document.getElementById('imageMeta');
    }
    
    initEventListeners() {
        // Load more button
        this.loadMoreBtn.addEventListener('click', () => this.loadMore());
        
        // Modal controls
        this.modalClose.addEventListener('click', () => this.closeModal());
        this.modalBackdrop.addEventListener('click', () => this.closeModal());
        this.modalPrev.addEventListener('click', () => this.prevImage());
        this.modalNext.addEventListener('click', () => this.nextImage());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Touch gestures for modal
        this.initTouchGestures();
    }
    
    initTouchGestures() {
        let startX = 0;
        let startY = 0;
        
        this.modal.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        this.modal.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const diffX = endX - startX;
            const diffY = endY - startY;
            
            // Swipe threshold
            const threshold = 50;
            
            // Horizontal swipe (navigate images)
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > threshold) {
                if (diffX > 0) {
                    this.prevImage();
                } else {
                    this.nextImage();
                }
            }
            
            // Vertical swipe down (close modal)
            if (diffY > threshold * 2 && Math.abs(diffX) < threshold) {
                this.closeModal();
            }
        }, { passive: true });
    }
    
    async loadGallery() {
        if (this.loading) return;
        
        this.loading = true;
        this.showLoading();
        
        try {
            const response = await fetch(`/api/gallery?page=${this.currentPage}`);
            const data = await response.json();
            
            if (this.currentPage === 1) {
                this.images = data.images;
                this.renderGallery(data.images);
            } else {
                this.images = [...this.images, ...data.images];
                this.appendImages(data.images);
            }
            
            this.hasMore = data.has_next;
            this.updateLoadMoreButton();
            
            if (data.total === 0) {
                this.showEmptyState();
            }
            
        } catch (error) {
            console.error('Error loading gallery:', error);
            this.showError('Failed to load gallery');
        } finally {
            this.loading = false;
            this.hideLoading();
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/gallery/stats');
            const stats = await response.json();
            
            if (stats.total > 0) {
                this.galleryStats.textContent = `${stats.total} images • ${stats.total_size_mb}MB`;
            } else {
                this.galleryStats.textContent = 'No images yet';
            }
        } catch (error) {
            this.galleryStats.textContent = 'Gallery stats unavailable';
        }
    }
    
    renderGallery(images) {
        this.galleryGrid.innerHTML = '';
        this.appendImages(images);
    }
    
    appendImages(images) {
        const fragment = document.createDocumentFragment();
        
        images.forEach((image, index) => {
            const item = this.createGalleryItem(image, this.images.indexOf(image));
            fragment.appendChild(item);
        });
        
        this.galleryGrid.appendChild(fragment);
    }
    
    createGalleryItem(image, index) {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.dataset.index = index;
        
        // Format date from generation timestamp or file creation
        const dateStr = image.generation_timestamp || image.created_at || image.timestamp;
        const date = new Date(dateStr).toLocaleDateString();
        
        // Truncate prompt for display
        const shortPrompt = image.prompt.length > 60 
            ? image.prompt.substring(0, 60) + '...' 
            : image.prompt;
        
        item.innerHTML = `
            <img class="gallery-thumbnail" 
                 src="${image.thumbnail_url}" 
                 alt="${image.prompt}"
                 loading="lazy">
            <div class="gallery-info">
                <div class="gallery-prompt">${shortPrompt}</div>
                <div class="gallery-meta">
                    <span class="gallery-date">${date}</span>
                    <span class="gallery-size">${image.size}</span>
                </div>
            </div>
        `;
        
        // Add click handler
        item.addEventListener('click', () => this.openModal(index));
        
        // Touch feedback
        item.addEventListener('touchstart', () => {}, { passive: true });
        
        return item;
    }
    
    loadMore() {
        if (!this.hasMore || this.loading) return;
        
        this.currentPage++;
        this.loadGallery();
    }
    
    updateLoadMoreButton() {
        if (this.hasMore) {
            this.loadMoreContainer.style.display = 'block';
            this.loadMoreBtn.disabled = this.loading;
            this.loadMoreBtn.textContent = this.loading ? 'Loading...' : 'Load More Images';
        } else {
            this.loadMoreContainer.style.display = 'none';
        }
    }
    
    openModal(index) {
        this.currentImageIndex = index;
        const image = this.images[index];
        
        if (!image) return;
        
        this.modalImage.src = image.image_url;
        this.modalImage.alt = image.prompt;
        
        // Update metadata - show AI generation details
        const genDate = new Date(image.generation_timestamp || image.created_at || image.timestamp).toLocaleString();
        
        let metaHTML = `
            <div><strong>Prompt:</strong> ${image.prompt}</div>
            <div><strong>Model:</strong> ${image.model} • <strong>Size:</strong> ${image.size}</div>
            <div><strong>Generated:</strong> ${genDate}</div>
        `;
        
        // Add optional AI parameters if available
        if (image.seed) metaHTML += `<div><strong>Seed:</strong> ${image.seed}</div>`;
        if (image.steps) metaHTML += `<div><strong>Steps:</strong> ${image.steps}</div>`;
        if (image.cfg_scale) metaHTML += `<div><strong>CFG Scale:</strong> ${image.cfg_scale}</div>`;
        
        this.imageMeta.innerHTML = metaHTML;
        
        // Update navigation buttons
        this.modalPrev.disabled = index === 0;
        this.modalNext.disabled = index === this.images.length - 1;
        
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
    }
    
    closeModal() {
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
    }
    
    prevImage() {
        if (this.currentImageIndex > 0) {
            this.openModal(this.currentImageIndex - 1);
        }
    }
    
    nextImage() {
        if (this.currentImageIndex < this.images.length - 1) {
            this.openModal(this.currentImageIndex + 1);
        }
    }
    
    handleKeyboard(e) {
        if (!this.modal.classList.contains('visible')) return;
        
        switch (e.key) {
            case 'Escape':
                this.closeModal();
                break;
            case 'ArrowLeft':
                this.prevImage();
                break;
            case 'ArrowRight':
                this.nextImage();
                break;
        }
    }
    
    showLoading() {
        if (this.currentPage === 1) {
            this.galleryGrid.innerHTML = `
                <div class="loading-placeholder">
                    <div class="loader-large"></div>
                    <p>Loading gallery...</p>
                </div>
            `;
        }
    }
    
    hideLoading() {
        const placeholder = this.galleryGrid.querySelector('.loading-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
    }
    
    showEmptyState() {
        this.emptyState.style.display = 'block';
        this.loadMoreContainer.style.display = 'none';
    }
    
    showError(message) {
        this.galleryGrid.innerHTML = `
            <div class="loading-placeholder">
                <p style="color: #dc2626;">${message}</p>
            </div>
        `;
    }
}

// Initialize gallery when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new Gallery();
});

// Prevent zoom on double tap
document.addEventListener('touchstart', () => {}, { passive: true });