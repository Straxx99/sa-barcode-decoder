"""
Quick test with specific image
"""
import requests
import base64
from PIL import Image, ImageEnhance
import io
import json

API_URL = "http://localhost:5000"

# Try all the vehicle disc images we have
test_images = [
    r"C:\Projects\Multi-Model-OCR\test_images\IMG-20251104-WA0005.jpg",  # Known working
    r"C:\Projects\Multi-Model-OCR\test_images\IMG-20251104-WA0004.jpg",
    r"C:\Projects\Multi-Model-OCR\test_images\IMG-20251104-WA0003.jpg",
]

print("="*80)
print("TESTING VEHICLE LICENSE DISC DECODER")
print("="*80)

for image_path in test_images:
    print(f"\nTesting: {image_path.split(chr(92))[-1]}")
    print("-"*80)

    try:
        # Load image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Apply high contrast (client-side preprocessing)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Send to API
        response = requests.post(
            f"{API_URL}/decode",
            json={'image': f'data:image/jpeg;base64,{image_data}'},
            timeout=30
        )

        result = response.json()

        if result.get('success'):
            print("[SUCCESS]")
            print(f"  Make: {result.get('make', 'N/A')}")
            print(f"  Model: {result.get('model', 'N/A')}")
            print(f"  Registration: {result.get('register_number', 'N/A')}")
            print(f"  VIN: {result.get('vin', 'N/A')}")
        else:
            print(f"[FAILED] {result.get('error', 'Unknown')}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

print("\n" + "="*80)
