"""
Quick test of SA decoder with a single image
"""

import requests
import base64
import json

API_URL = "http://localhost:5000"

# Test with the image that previously worked
image_path = r"C:\Projects\Multi-Model-OCR\test_images\IMG-20251104-WA0005.jpg"

print(f"Testing: {image_path}")

# Read and encode image
with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Send to API
response = requests.post(
    f"{API_URL}/decode",
    json={'image': f'data:image/jpeg;base64,{image_data}'},
    timeout=30
)

result = response.json()

# Print full result
print("\n" + "="*80)
print("RESULT:")
print("="*80)
print(json.dumps(result, indent=2))

# Save to file
with open('test_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\nResult saved to test_result.json")
