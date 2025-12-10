"""
Test script to decode SA license disc barcode using the Flask API
"""
import requests
import base64
from pathlib import Path

# Path to test image
image_path = r"C:\Projects\Multi-Model-OCR\test_images\VLD\IMG-20251104-WA0003.jpg"

# Read and encode image
with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Send to API
print(f"Testing barcode decode with: {Path(image_path).name}")
print("Sending request to API...")

response = requests.post(
    'http://localhost:5000/decode',
    json={'image': image_data},
    timeout=30
)

# Print results
print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse:")
print(response.json())

if response.status_code == 200:
    data = response.json()
    if data.get('success') and data.get('barcodes'):
        print(f"\n✅ SUCCESS! Found {data['count']} barcode(s)")
        for i, barcode in enumerate(data['barcodes'], 1):
            print(f"\nBarcode {i}:")
            print(f"  Type: {barcode['type']}")
            print(f"  Data Length: {len(barcode.get('data', ''))}")
            print(f"  Raw Data Preview: {barcode.get('data', '')[:200]}...")
    else:
        print(f"\n❌ No barcode found")
else:
    print(f"\n❌ API Error")
