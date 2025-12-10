"""
Test the image that we know works (IMG-20251104-WA0005.jpg)
"""
import requests
import base64
from pathlib import Path

# Path to test image that worked before
image_path = r"C:\Projects\Multi-Model-OCR\test_images\VLD\IMG-20251104-WA0005.jpg"

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
data = response.json()
print(f"\nResponse:")

if data.get('success'):
    print(f"  SUCCESS! Found {data['count']} barcode(s)")
    print(f"  Preprocessing method used: {data.get('preprocessing_used')}")
    for i, barcode in enumerate(data['barcodes'], 1):
        print(f"\n  Barcode {i}:")
        print(f"    Type: {barcode['type']}")
        print(f"    Data Length: {len(barcode.get('data', ''))}")
        print(f"    Full Data:")
        print(f"    {barcode.get('data', '')}")
else:
    print(f"  FAILED: {data.get('error')}")
