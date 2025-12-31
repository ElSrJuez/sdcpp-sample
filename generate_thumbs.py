"""
Generate thumbnails for existing images
"""
import json
from pathlib import Path
from services.images import ImageService

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize image service
image_service = ImageService(config)

# Load gallery database
with open(config['gallery']['db_file'], 'r') as f:
    db_data = json.load(f)

print("Generating thumbnails for existing images...")

generated = 0
skipped = 0

for entry in db_data['images'].values():
    filename = entry['filename']
    
    # Check if thumbnail already exists
    thumb_path = Path(config['files']['thumbs_dir']) / filename
    if thumb_path.exists():
        print(f"✓ Thumbnail exists: {filename}")
        skipped += 1
        continue
    
    # Generate thumbnail
    result = image_service.generate_thumbnail(filename)
    if result:
        print(f"✓ Generated thumbnail: {filename}")
        generated += 1
    else:
        print(f"✗ Failed to generate thumbnail: {filename}")

print(f"\nThumbnail generation complete!")
print(f"- Generated: {generated} thumbnails")
print(f"- Skipped (already existed): {skipped} thumbnails")
print(f"- Total images processed: {len(db_data['images'])}")

# Cleanup any orphaned thumbnails
cleaned = image_service.cleanup_thumbnails()
if cleaned > 0:
    print(f"- Cleaned up: {cleaned} orphaned thumbnails")