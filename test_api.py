"""
Test script for barcode API with actual SA license disc images
"""
import base64
import requests
import json

# Test with the first license disc image
image_path = r"C:\Projects\Multi-Model-OCR\test_images\VLD\IMG-20251104-WA0003.jpg"

print(f"Testing barcode API with: {image_path}")
print("-" * 60)

# Read and encode image
with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Call API
url = "http://localhost:5000/decode"
payload = {"image": image_data}

print("Sending image to API...")
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print("-" * 60)

result = response.json()
print(json.dumps(result, indent=2))

if result.get('success') and result.get('barcodes'):
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Barcode decoded!")
    print("=" * 60)
    for i, barcode in enumerate(result['barcodes'], 1):
        print(f"\nBarcode {i}:")
        print(f"  Type: {barcode.get('type')}")
        print(f"  Data length: {len(barcode.get('data', ''))}")
        print(f"  First 200 chars: {barcode.get('data', '')[:200]}")
else:
    print("\n" + "=" * 60)
    print("❌ FAILED - No barcode decoded")
    print("=" * 60)
