"""
Test the latest car license disc image
"""
import requests
import base64
from PIL import Image, ImageEnhance
import io
import json

API_URL = "http://localhost:5000"

# Test the latest screenshot (your new car license disc)
image_path = r"C:\Projects\Multi-Model-OCR\test_images\Screenshot 2025-12-10 012938.png"

print("="*80)
print("TESTING NEW CAR LICENSE DISC IMAGE")
print("="*80)
print(f"\nImage: {image_path.split(chr(92))[-1]}")

# Load image
img = Image.open(image_path)
if img.mode != 'RGB':
    img = img.convert('RGB')

print(f"Original size: {img.size}")

# Apply high contrast preprocessing (client-side - this is what works!)
print("Applying high contrast preprocessing...")
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

# Convert to base64
buffer = io.BytesIO()
img.save(buffer, format='PNG')
image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

print("Sending to API...")

# Send to API
response = requests.post(
    f"{API_URL}/decode",
    json={'image': f'data:image/png;base64,{image_data}'},
    timeout=60
)

result = response.json()

print("\n" + "="*80)
print("RESULT:")
print("="*80)

if result.get('success'):
    print("\n>> SUCCESS! Car License Disc Decoded!\n")
    print(json.dumps(result, indent=2))

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
    print(f"Description:         {result.get('description', 'N/A')}")
    print("\n" + "="*80)
    print(">> YOUR SOLUTION SUCCESSFULLY DECODED THE NEW IMAGE!")
    print("="*80)
else:
    print(f"\n>> FAILED")
    print(f"Error: {result.get('error', 'Unknown error')}")
    if 'hint' in result:
        print(f"Hint: {result.get('hint')}")

# Save result
with open('latest_disc_result.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nFull result saved to: latest_disc_result.json")
