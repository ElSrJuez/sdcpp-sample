import json
import os
import requests
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path

# Import services
from services.database import GalleryDB
from services.images import ImageService

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)

# Initialize services
db = GalleryDB(config)
image_service = ImageService(config)

# Ensure output directory exists
output_dir = Path(config['files']['output_dir'])
output_dir.mkdir(exist_ok=True)

def generate_filename(prompt):
    """Generate a short, readable filename from prompt and timestamp"""
    # Clean and truncate prompt
    clean_prompt = ''.join(c for c in prompt if c.isalnum() or c.isspace())
    words = clean_prompt.split()[:3]  # First 3 words
    prompt_part = '_'.join(words).lower()
    
    # Simple timestamp
    timestamp = datetime.now().strftime("%m%d_%H%M")
    
    return f"{prompt_part}_{timestamp}.png"

def get_file_info(filename):
    """Get live filesystem data for a file"""
    file_path = output_dir / filename
    if not file_path.exists():
        return None
    
    stat = file_path.stat()
    return {
        'file_size': stat.st_size,
        'created_at': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        'modified_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    }

def call_sd_api(prompt, size=None, count=None):
    """Call the Stable Diffusion API with server's actual supported parameters"""
    payload = {
        "model": config['sd_api']['model'],
        "prompt": prompt,
        "size": size or config['sd_api']['default_size'],
        "n": count or config['sd_api']['default_count'],
        "response_format": config['sd_api']['response_format']
    }
    
    try:
        response = requests.post(
            config['sd_api']['url'],
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"SD API Error: {str(e)}")

def save_image(b64_data, filename):
    """Save base64 image data to file"""
    image_data = base64.b64decode(b64_data)
    filepath = output_dir / filename
    with open(filepath, 'wb') as f:
        f.write(image_data)
    return filepath

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         max_prompt_length=config['files']['max_prompt_length'])

@app.route('/generate', methods=['POST'])
def generate():
    """Generate image from prompt"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if len(prompt) > config['files']['max_prompt_length']:
            return jsonify({'error': 'Prompt too long'}), 400
        
        # Call SD API (server controls all generation parameters)
        size_param = data.get('size', config['sd_api']['default_size'])
        result = call_sd_api(prompt, size_param)
        
        # Extract image data
        image_data = result['data'][0]
        b64_image = image_data['b64_json']
        filename = generate_filename(prompt)
        filepath = save_image(b64_image, filename)
        
        # Store AI-specific metadata (only what we control/know)
        db.add_image(
            filename=filename,
            prompt=prompt,
            model=config['sd_api']['model'],
            size=size_param
        )
        
        # Generate thumbnail
        thumbnail_url = image_service.get_thumbnail_url(filename)
        
        # Get live file info for response
        file_info = get_file_info(filename)
        file_size = file_info['file_size'] if file_info else 0
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/images/{filename}',
            'thumbnail_url': thumbnail_url,
            'prompt': prompt,
            'file_size': file_size
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve generated images"""
    return send_from_directory(output_dir, filename)

@app.route('/thumbs/<filename>')
def serve_thumbnail(filename):
    """Serve thumbnail images"""
    thumbs_dir = Path(config['files']['thumbs_dir'])
    return send_from_directory(thumbs_dir, filename)

@app.route('/gallery')
def gallery():
    """Gallery page"""
    return render_template('gallery.html')

@app.route('/api/gallery')
def api_gallery():
    """API endpoint for gallery data - combines AI metadata with live file info"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', config['gallery']['items_per_page']))
    
    gallery_data = db.get_paginated_images(page, per_page)
    
    # Enrich with thumbnail URLs and live file info
    for image in gallery_data['images']:
        image['thumbnail_url'] = image_service.get_thumbnail_url(image['filename'])
        image['image_url'] = f"/images/{image['filename']}"
        
        # Add live filesystem data
        file_info = get_file_info(image['filename'])
        if file_info:
            image.update(file_info)  # Add file_size, created_at, modified_at
        else:
            image['file_exists'] = False
    
    return jsonify(gallery_data)

@app.route('/api/gallery/stats')
def api_gallery_stats():
    """API endpoint for gallery statistics"""
    stats = db.get_stats()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(
        host=config['app']['host'],
        port=config['app']['port'],
        debug=config['app']['debug']
    )