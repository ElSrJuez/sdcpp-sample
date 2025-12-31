"""
One-time migration script to add existing images to gallery database
"""
import json
import os
from datetime import datetime
from pathlib import Path
import re

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize paths
output_dir = Path(config['files']['output_dir'])
db_file = config['gallery']['db_file']

# Load or create gallery database
if os.path.exists(db_file):
    with open(db_file, 'r') as f:
        db_data = json.load(f)
else:
    db_data = {"images": {}}

existing_files = {entry['filename'] for entry in db_data['images'].values()}

print(f"Found {len(existing_files)} images already in database")

# Find all PNG files in output directory
png_files = list(output_dir.glob('*.png'))
print(f"Found {len(png_files)} PNG files in {output_dir}")

# Pattern to extract info from filename: word1_word2_word3_MMDD_HHMM.png
filename_pattern = re.compile(r'^(.+?)_(\d{4})_(\d{4})\.png$')

new_entries = 0
next_id = max([int(k) for k in db_data['images'].keys()], default=0) + 1

for png_file in png_files:
    filename = png_file.name
    
    # Skip if already in database
    if filename in existing_files:
        continue
        
    # Try to extract info from filename
    match = filename_pattern.match(filename)
    
    if match:
        prompt_part, date_part, time_part = match.groups()
        
        # Reconstruct likely prompt from filename
        words = prompt_part.split('_')
        reconstructed_prompt = ' '.join(words).title()
        
        # Create timestamp from filename date/time
        try:
            # Assume current year if not specified
            year = datetime.now().year
            month = int(date_part[:2])
            day = int(date_part[2:])
            hour = int(time_part[:2])
            minute = int(time_part[2:])
            
            file_datetime = datetime(year, month, day, hour, minute)
            generation_timestamp = file_datetime.isoformat()
        except ValueError:
            # Fallback to file creation time
            file_stat = png_file.stat()
            generation_timestamp = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
            reconstructed_prompt = f"Generated image from {filename}"
    else:
        # Fallback for files that don't match pattern
        file_stat = png_file.stat()
        generation_timestamp = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
        reconstructed_prompt = f"Generated image from {filename}"
    
    # Add to database
    db_data['images'][str(next_id)] = {
        'id': next_id,
        'filename': filename,
        'prompt': reconstructed_prompt,
        'model': config['sd_api']['model'],
        'size': config['sd_api']['default_size'],
        'generation_timestamp': generation_timestamp
    }
    
    print(f"Added: {filename} -> '{reconstructed_prompt}'")
    new_entries += 1
    next_id += 1

# Save updated database
with open(db_file, 'w') as f:
    json.dump(db_data, f, indent=2)

print(f"\nMigration complete!")
print(f"- Added {new_entries} new entries")
print(f"- Total images in database: {len(db_data['images'])}")
print(f"- Database saved to: {db_file}")