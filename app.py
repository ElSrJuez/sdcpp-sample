import json
import os
import requests
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)

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

def call_sd_api(prompt, size=None, count=None):
    """Call the Stable Diffusion API"""
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
    return render_template('index.html')

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
        
        # Call SD API
        result = call_sd_api(prompt)
        
        # Save image
        b64_image = result['data'][0]['b64_json']
        filename = generate_filename(prompt)
        filepath = save_image(b64_image, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/images/{filename}',
            'prompt': prompt
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve generated images"""
    return send_from_directory(output_dir, filename)

if __name__ == '__main__':
    app.run(
        host=config['app']['host'],
        port=config['app']['port'],
        debug=config['app']['debug']
    )