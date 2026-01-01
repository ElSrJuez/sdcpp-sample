"""
Database service for image metadata storage using TinyDB
Simple, lightweight, config-driven approach
"""
import json
from datetime import datetime
from tinydb import TinyDB, Query
from pathlib import Path
import os

class GalleryDB:
    def __init__(self, config):
        self.config = config
        self.db_path = config['gallery']['db_file']
        self.db = TinyDB(self.db_path)
        self.images = self.db.table('images')
    
    def add_image(self, filename, prompt, model=None, size=None, quality='low', seed=None, actual_seed=None):
        """Add AI-specific metadata with generation parameters"""
        
        # Map quality to steps for display
        quality_steps = {'low': 4, 'medium': 10, 'high': 20}
        steps = quality_steps.get(quality, 4)
        
        metadata = {
            'id': len(self.images) + 1,
            'filename': filename,  # Reference to file only
            # AI Generation Parameters (what we actually control)
            'prompt': prompt,
            'model': model or self.config['sd_api']['model'],
            'size': size or self.config['sd_api']['default_size'],
            'quality': quality,
            'generation_timestamp': datetime.now().isoformat(),
            # Generation parameters used
            'parameters': {
                'steps': steps,
                'seed': actual_seed,  # The actual seed used (either specified or generated)
                'user_seed': seed,    # The seed user specified (None if random)
                'method': 'Euler'     # Fixed by server
            }
        }
        
        return self.images.insert(metadata)
    
    def get_all_images(self, limit=None):
        """Get all images, newest generation first"""
        all_images = self.images.all()
        # Sort by generation timestamp, newest first
        sorted_images = sorted(all_images, key=lambda x: x.get('generation_timestamp', ''), reverse=True)
        
        if limit:
            return sorted_images[:limit]
        return sorted_images
    
    def get_image_by_filename(self, filename):
        """Get image metadata by filename"""
        Image = Query()
        return self.images.search(Image.filename == filename)
    
    def get_paginated_images(self, page=1, per_page=None):
        """Get images with pagination"""
        if not per_page:
            per_page = self.config['gallery']['items_per_page']
        
        all_images = self.get_all_images()
        total = len(all_images)
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'images': all_images[start:end],
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_next': end < total,
            'has_prev': page > 1
        }
    
    def delete_image(self, filename):
        """Remove image metadata"""
        Image = Query()
        return self.images.remove(Image.filename == filename)
    
    def get_stats(self):
        """Get gallery statistics - combine DB metadata with live filesystem data"""
        all_images = self.images.all()
        
        if not all_images:
            return {'total': 0, 'total_size': 0}
        
        # Get file sizes from filesystem (live data)
        total_size = 0
        valid_files = 0
        output_dir = Path(self.config['files']['output_dir'])
        
        for img in all_images:
            file_path = output_dir / img['filename']
            if file_path.exists():
                total_size += file_path.stat().st_size
                valid_files += 1
        
        return {
            'total': len(all_images),
            'valid_files': valid_files,  # Files that still exist
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }