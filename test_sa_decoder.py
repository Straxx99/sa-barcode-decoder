"""
Test script for SA License Decoder
Tests both SA driver licenses (encrypted) and vehicle discs (text)
"""

import requests
import base64
import json
import os
from pathlib import Path

API_URL = "http://localhost:5000"

def test_image(image_path):
    """Test decoding a single image"""
    print(f"\n{'='*80}")
    print(f"Testing: {os.path.basename(image_path)}")
    print(f"{'='*80}")

    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Send to API
    try:
        response = requests.post(
            f"{API_URL}/decode",
            json={'image': f'data:image/jpeg;base64,{image_data}'},
            timeout=30
        )

        result = response.json()

        # Print results
        print(f"\nStatus: {response.status_code}")
        print(f"Success: {result.get('success', False)}")

        if result.get('success'):
            license_type = result.get('license_type', 'UNKNOWN')
            print(f"License Type: {license_type}")
            print(f"Barcode Format: {result.get('barcode_format', 'N/A')}")
            print(f"Preprocessing Used: {result.get('preprocessing_used', 'N/A')}")

            if license_type == 'SA_DRIVER_LICENSE':
                print("\n>> SA DRIVER LICENSE DECODED!")
                print(f"Version: {result.get('version', 'N/A')}")

                personal_info = result.get('personal_info', {})
                print("\nPersonal Info:")
                print(f"  Surname: {personal_info.get('surname', 'N/A')}")
                print(f"  Initials: {personal_info.get('initials', 'N/A')}")
                print(f"  ID Number: {personal_info.get('id_number', 'N/A')}")
                print(f"  Birth Date: {personal_info.get('birth_date', 'N/A')}")
                print(f"  Gender: {personal_info.get('gender', 'N/A')}")

                license_info = result.get('license_info', {})
                print("\nLicense Info:")
                print(f"  License Number: {license_info.get('license_number', 'N/A')}")
                print(f"  Issue Date: {license_info.get('license_issue_date', 'N/A')}")
                print(f"  Expiry Date: {license_info.get('license_expiry_date', 'N/A')}")
                print(f"  Vehicle Codes: {license_info.get('vehicle_codes', [])}")
                print(f"  Restrictions: {license_info.get('vehicle_restrictions', [])}")

            elif license_type == 'SA_VEHICLE_DISC':
                print("\n>> SA VEHICLE DISC DECODED!")
                print(f"Control Number: {result.get('control_number', 'N/A')}")
                print(f"License Number: {result.get('license_number', 'N/A')}")
                print(f"Register Number: {result.get('register_number', 'N/A')}")
                print(f"VIN: {result.get('vin', 'N/A')}")
                print(f"Make: {result.get('make', 'N/A')}")
                print(f"Model: {result.get('model', 'N/A')}")
                print(f"Color: {result.get('color', 'N/A')}")
                print(f"Expiry Date: {result.get('expiry_date', 'N/A')}")

            elif license_type == 'UNKNOWN':
                print("\n>> UNKNOWN FORMAT")
                print(f"Data Length: {result.get('data_length', 'N/A')}")
                print(f"Raw Data (first 100 chars): {result.get('raw_data', '')[:100]}")

        else:
            print(f"\n>> FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            if 'hint' in result:
                print(f"Hint: {result.get('hint')}")

        # Save full result to JSON
        result_file = f"test_result_{os.path.basename(image_path)}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull result saved to: {result_file}")

        return result

    except Exception as e:
        print(f"\n>> ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Test all SA license and vehicle disc images"""
    print("="*80)
    print("SA LICENSE DECODER TEST SUITE")
    print("="*80)

    # Check API health
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        health = response.json()
        print(f"\n[OK] API Health Check:")
        print(f"   Status: {health.get('status')}")
        print(f"   Decoder: {health.get('decoder')}")
        print(f"   Encryption Support: {health.get('encryption_support')}")
    except Exception as e:
        print(f"\n[FAIL] API Health Check FAILED: {str(e)}")
        print("Make sure app_sa.py is running on port 5000")
        return

    # Test vehicle disc images
    vld_dir = Path(r"C:\Projects\Multi-Model-OCR\test_images\VLD")

    if vld_dir.exists():
        vld_images = list(vld_dir.glob("*.jpg"))
        print(f"\n\nFound {len(vld_images)} vehicle disc images")

        success_count = 0
        for img_path in vld_images:
            result = test_image(str(img_path))
            if result and result.get('success'):
                success_count += 1

        print(f"\n{'='*80}")
        print(f"VEHICLE DISC RESULTS: {success_count}/{len(vld_images)} successfully decoded")
        print(f"{'='*80}")
    else:
        print(f"\n[WARN] Vehicle disc directory not found: {vld_dir}")

    # Test driver license images (if you have any)
    dl_dir = Path(r"C:\Projects\Multi-Model-OCR\test_images\DL")

    if dl_dir.exists():
        dl_images = list(dl_dir.glob("*.jpg"))
        print(f"\n\nFound {len(dl_images)} driver license images")

        success_count = 0
        for img_path in dl_images:
            result = test_image(str(img_path))
            if result and result.get('success'):
                success_count += 1

        print(f"\n{'='*80}")
        print(f"DRIVER LICENSE RESULTS: {success_count}/{len(dl_images)} successfully decoded")
        print(f"{'='*80}")
    else:
        print(f"\n[WARN] Driver license directory not found: {dl_dir}")
        print("   (This is expected if you only have vehicle disc images)")

    print("\n\n[OK] Test suite completed!")


if __name__ == '__main__':
    main()
