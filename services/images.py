"""
Image processing service for thumbnail generation and optimization
Mobile-first, performance-focused approach
"""
import os
from PIL import Image, ImageOps
from pathlib import Path

class ImageService:
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config['files']['output_dir'])
        self.thumbs_dir = Path(config['files']['thumbs_dir'])
        self.thumb_size = tuple(config['gallery']['thumbnail_size'])
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.thumbs_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_thumbnail(self, filename):
        """Generate thumbnail for image - mobile optimized"""
        try:
            source_path = self.output_dir / filename
            thumb_path = self.thumbs_dir / filename
            
            if thumb_path.exists():
                return str(thumb_path)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source image not found: {filename}")
            
            # Open and process image
            with Image.open(source_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Generate thumbnail with smart cropping
                thumbnail = ImageOps.fit(
                    img, 
                    self.thumb_size, 
                    Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5)
                )
                
                # Save optimized thumbnail
                thumbnail.save(
                    thumb_path,
                    'JPEG',
                    quality=85,
                    optimize=True,
                    progressive=True
                )
                
                return str(thumb_path)
                
        except Exception as e:
            print(f"Error generating thumbnail for {filename}: {e}")
            return None
    
    def get_thumbnail_url(self, filename):
        """Get URL for thumbnail, generate if needed"""
        thumb_path = self.thumbs_dir / filename
        
        if not thumb_path.exists():
            self.generate_thumbnail(filename)
        
        if thumb_path.exists():
            return f"/thumbs/{filename}"
        
        # Fallback to original image
        return f"/images/{filename}"
    
    def get_image_info(self, filename):
        """Get image dimensions and file size"""
        try:
            full_path = self.output_dir / filename
            if not full_path.exists():
                return None
                
            with Image.open(full_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'file_size': full_path.stat().st_size
                }
        except Exception as e:
            print(f"Error getting image info for {filename}: {e}")
            return None
    
    def cleanup_thumbnails(self):
        """Remove thumbnails for images that no longer exist"""
        removed = 0
        
        for thumb_file in self.thumbs_dir.glob('*.jpg'):
            # Check if original exists (look for .png version)
            original_name = thumb_file.stem + '.png'
            original_path = self.output_dir / original_name
            
            if not original_path.exists():
                thumb_file.unlink()
                removed += 1
        
        return removed
    
    def get_directory_size(self, directory):
        """Get total size of directory in bytes"""
        total_size = 0
        directory_path = Path(directory)
        
        if directory_path.exists():
            for file_path in directory_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        return total_size