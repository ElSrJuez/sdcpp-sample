import json
import os
import requests
import base64
import threading
import uuid
import time
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

# Job management for async processing
jobs = {}
jobs_lock = threading.Lock()

class JobStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

def create_job(prompt, size):
    """Create a new background job"""
    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {
            'id': job_id,
            'status': JobStatus.PENDING,
            'prompt': prompt,
            'size': size,
            'progress': 0,
            'message': 'Queued for processing',
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
    return job_id

def get_job(job_id):
    """Get job status"""
    with jobs_lock:
        return jobs.get(job_id, None)

def update_job(job_id, **updates):
    """Update job status"""
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(updates)

def process_image_generation(job_id, prompt, size):
    """Background function to process image generation"""
    try:
        update_job(job_id, status=JobStatus.PROCESSING, message="Starting generation...", progress=10)
        
        # Call SD API
        result = call_sd_api(prompt, size)
        update_job(job_id, message="Processing server response...", progress=80)
        
        # Extract image data
        image_data = result['data'][0]
        b64_image = image_data['b64_json']
        filename = generate_filename(prompt)
        filepath = save_image(b64_image, filename)
        
        update_job(job_id, message="Saving to database...", progress=90)
        
        # Store metadata
        db.add_image(filename, prompt, config['sd_api']['model'], size)
        
        # Generate thumbnail
        thumbnail_url = image_service.get_thumbnail_url(filename)
        
        # Get file info
        file_info = get_file_info(filename)
        file_size = file_info['file_size'] if file_info else 0
        
        # Mark as completed
        update_job(job_id, 
                  status=JobStatus.COMPLETED, 
                  progress=100,
                  message="Generation complete!",
                  result={
                      'filename': filename,
                      'url': f'/images/{filename}',
                      'thumbnail_url': thumbnail_url,
                      'prompt': prompt,
                      'size': size,
                      'file_size': file_size
                  })
                  
    except Exception as e:
        update_job(job_id, 
                  status=JobStatus.FAILED, 
                  error=str(e),
                  message=f"Generation failed: {str(e)}")

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
            timeout=60  # Increased timeout to 60 seconds
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
    """Start async image generation and return job ID"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if len(prompt) > config['files']['max_prompt_length']:
            return jsonify({'error': 'Prompt too long'}), 400
        
        # Get generation parameters
        size_param = data.get('size', config['sd_api']['default_size'])
        
        # Create background job
        job_id = create_job(prompt, size_param)
        
        # Start background processing
        thread = threading.Thread(
            target=process_image_generation, 
            args=(job_id, prompt, size_param)
        )
        thread.daemon = True
        thread.start()
        
        # Return job ID immediately
        return jsonify({
            'job_id': job_id,
            'status': 'pending',
            'message': 'Generation started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate/status/<job_id>', methods=['GET'])
def get_generation_status(job_id):
    """Get the status of a generation job"""
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message'],
        'created_at': job['created_at']
    }
    
    if job['status'] == JobStatus.COMPLETED and job['result']:
        response['result'] = job['result']
    elif job['status'] == JobStatus.FAILED and job['error']:
        response['error'] = job['error']
    
    return jsonify(response)

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