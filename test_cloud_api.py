"""
Test SA license disc barcode with Dynamsoft Cloud Barcode Reader API
Free tier: 10,000 scans/month
"""
import base64
import requests
import json
import os

# Test image path
image_path = r"C:\Projects\Multi-Model-OCR\test_images\VLD\IMG-20251104-WA0003.jpg"

print("=" * 70)
print("Testing SA License Disc Barcode with Dynamsoft Cloud API")
print("=" * 70)
print(f"\nImage: {os.path.basename(image_path)}")

# Read and encode image
with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Dynamsoft Cloud API endpoint (using trial)
# Trial key - replace with your own from: https://www.dynamsoft.com/customer/license/trialLicense
api_url = "https://api.dynamsoft.com/codereaderjson/decode"

payload = {
    "image": image_data,
    "template": "{\"ImageParameter\":{\"BarcodeFormatIds\":[\"BF_PDF417\"],\"DeblurLevel\":9,\"ScaleDownThreshold\":10000}}"
}

headers = {
    "Content-Type": "application/json",
    # Trial license - you can get your own free trial key
    "Authorization": "Basic TRIAL"
}

print("\nSending to Dynamsoft Cloud API...")
print("(Using trial mode - no API key needed)")

try:
    response = requests.post(api_url, json=payload, headers=headers, timeout=30)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n" + "=" * 70)
        print(json.dumps(result, indent=2))
        print("=" * 70)

        if result.get('results') and len(result['results']) > 0:
            print("\n✅ SUCCESS! Barcode decoded by Dynamsoft!")
            for i, barcode in enumerate(result['results'], 1):
                print(f"\nBarcode {i}:")
                print(f"  Type: {barcode.get('barcodeFormat')}")
                print(f"  Text Length: {len(barcode.get('barcodeText', ''))}")
                print(f"  First 200 chars: {barcode.get('barcodeText', '')[:200]}")
        else:
            print("\n❌ No barcode found")
    else:
        print(f"\nError: {response.text}")

except requests.Timeout:
    print("\n❌ Request timed out")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 70)
print("NOTE: For production, get a free API key at:")
print("https://www.dynamsoft.com/customer/license/trialLicense")
print("=" * 70)
