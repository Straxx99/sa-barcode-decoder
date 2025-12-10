"""
Test with cropping and enhanced preprocessing
"""

import requests
import base64
import json
from PIL import Image, ImageEnhance
import io

API_URL = "http://localhost:5000"
image_path = r"C:\Projects\Multi-Model-OCR\test_images\DLC\license_back.png"

print("Loading image...")
img = Image.open(image_path)
print(f"Original size: {img.size}")

# Crop to just the barcode area (top portion of the card)
# The barcode is roughly in the top 30% of the image
width, height = img.size
barcode_height = int(height * 0.3)  # Top 30% of image
img_cropped = img.crop((0, 0, width, barcode_height))

print(f"Cropped to barcode area: {img_cropped.size}")

# Convert to RGB
if img_cropped.mode != 'RGB':
    img_cropped = img_cropped.convert('RGB')

# Try different preprocessing methods
preprocessing_methods = [
    ("original", lambda x: x),
    ("high_contrast", lambda x: ImageEnhance.Contrast(x).enhance(2.5)),
    ("very_high_contrast", lambda x: ImageEnhance.Contrast(x).enhance(3.0)),
    ("sharp_contrast", lambda x: ImageEnhance.Sharpness(ImageEnhance.Contrast(x).enhance(2.5)).enhance(2.0)),
    ("inverted", lambda x: ImageEnhance.Brightness(x).enhance(0.5)),
]

for method_name, preprocess_func in preprocessing_methods:
    print(f"\nTrying: {method_name}")

    # Apply preprocessing
    processed = preprocess_func(img_cropped.copy())

    # Convert to base64
    buffer = io.BytesIO()
    processed.save(buffer, format='PNG')
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Send to API
    response = requests.post(
        f"{API_URL}/decode",
        json={'image': image_data},
        timeout=60
    )

    result = response.json()

    if result.get('success'):
        print(f"SUCCESS with {method_name}!")
        print(json.dumps(result, indent=2))

        # Save result
        with open(f'license_result_{method_name}.json', 'w') as f:
            json.dump(result, f, indent=2)
        break
    else:
        print(f"  Failed: {result.get('error', 'Unknown error')}")
else:
    print("\nAll methods failed. The barcode might have too much glare or damage.")
