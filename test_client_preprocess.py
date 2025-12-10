"""
Test with CLIENT-SIDE preprocessing like test_all_images.py does
"""

import requests
import base64
import json
from PIL import Image, ImageEnhance
import io

API_URL = "http://localhost:5000"
image_path = r"C:\Projects\Multi-Model-OCR\test_images\IMG-20251104-WA0005.jpg"

print(f"Testing: {image_path}")

# Open image
img = Image.open(image_path)
if img.mode != 'RGB':
    img = img.convert('RGB')

# Apply high_contrast preprocessing CLIENT-SIDE (like test_all_images.py does)
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

# Convert to base64
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

print(f"Sending preprocessed image to API...")

# Send to API
response = requests.post(
    f"{API_URL}/decode",
    json={'image': image_data},
    timeout=30
)

result = response.json()

# Print result
print("\n" + "="*80)
print("RESULT:")
print("="*80)
print(json.dumps(result, indent=2))
