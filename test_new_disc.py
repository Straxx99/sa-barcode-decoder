"""
Test the new car license disc image
"""

import requests
import base64
import json
from PIL import Image, ImageEnhance
import io
import sys
import os

API_URL = "http://localhost:5000"

# Find the most recent image
test_dir = r"C:\Projects\Multi-Model-OCR\test_images"
images = []
for f in os.listdir(test_dir):
    if f.lower().endswith(('.jpg', '.png', '.jpeg')):
        full_path = os.path.join(test_dir, f)
        images.append((full_path, os.path.getmtime(full_path)))

# Sort by modification time, get most recent
images.sort(key=lambda x: x[1], reverse=True)
image_path = images[0][0] if images else None

if not image_path:
    print("No images found!")
    sys.exit(1)

print(f"Testing most recent image: {os.path.basename(image_path)}")
print("="*80)

# Load image
img = Image.open(image_path)
if img.mode != 'RGB':
    img = img.convert('RGB')

print(f"Image size: {img.size}")

# Apply client-side preprocessing (high contrast - this is what works!)
print("Applying high contrast preprocessing...")
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

# Convert to base64
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

print("Sending to API...")

# Send to API
response = requests.post(
    f"{API_URL}/decode",
    json={'image': f'data:image/jpeg;base64,{image_data}'},
    timeout=60
)

result = response.json()

print("\n" + "="*80)
print("RESULT:")
print("="*80)

if result.get('success'):
    print("\n✓ SUCCESS! Car License Disc Decoded!\n")
    print(json.dumps(result, indent=2))

    # Display key fields
    if result.get('license_type') == 'SA_VEHICLE_DISC':
        print("\n" + "="*80)
        print("EXTRACTED VEHICLE INFORMATION:")
        print("="*80)
        print(f"Registration Number: {result.get('register_number', 'N/A')}")
        print(f"VIN:                 {result.get('vin', 'N/A')}")
        print(f"Make:                {result.get('make', 'N/A')}")
        print(f"Model:               {result.get('model', 'N/A')}")
        print(f"Color:               {result.get('color', 'N/A')}")
        print(f"Engine Number:       {result.get('engine_number', 'N/A')}")
        print(f"License Number:      {result.get('license_number', 'N/A')}")
        print(f"Control Number:      {result.get('control_number', 'N/A')}")
        print(f"Disk Number:         {result.get('disk_number', 'N/A')}")
        print(f"Description:         {result.get('description', 'N/A')}")
        print("\n" + "="*80)
        print("YOUR SOLUTION WORKS!")
        print("="*80)
else:
    print("\n✗ FAILED")
    print(f"Error: {result.get('error', 'Unknown error')}")
    if 'hint' in result:
        print(f"Hint: {result.get('hint')}")

# Save result
output_file = 'test_new_disc_result.json'
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nFull result saved to: {output_file}")
