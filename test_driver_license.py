"""
Test SA Driver's License RSA Decryption
Place the back-of-license image in the test_images directory and update the path below
"""

import requests
import base64
import json
from PIL import Image, ImageEnhance
import io
import sys

API_URL = "http://localhost:5000"

def test_license(image_path):
    """Test SA driver's license with RSA decryption"""
    print("="*80)
    print("SA DRIVER'S LICENSE RSA DECRYPTION TEST")
    print("="*80)
    print(f"\nImage: {image_path}")

    try:
        # Open image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        print(f"Image size: {img.size}")
        print("Applying client-side preprocessing (high contrast)...")

        # Apply high_contrast preprocessing CLIENT-SIDE (best results)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        print(f"Sending to API...")

        # Send to API
        response = requests.post(
            f"{API_URL}/decode",
            json={'image': image_data},
            timeout=60
        )

        result = response.json()

        # Print result
        print("\n" + "="*80)
        print("RESULT:")
        print("="*80)

        if result.get('success'):
            license_type = result.get('license_type')

            if license_type == 'SA_DRIVER_LICENSE':
                print("\n>> SA DRIVER'S LICENSE SUCCESSFULLY DECODED AND DECRYPTED!")
                print(f"\nVersion: {result.get('version')}")
                print(f"Barcode Format: {result.get('barcode_format')}")
                print(f"Preprocessing Used: {result.get('preprocessing_used')}")

                # Personal Info
                personal = result.get('personal_info', {})
                print("\n--- PERSONAL INFORMATION ---")
                print(f"Surname:        {personal.get('surname')}")
                print(f"Initials:       {personal.get('initials')}")
                print(f"ID Number:      {personal.get('id_number')}")
                print(f"ID Type:        {personal.get('id_number_type')}")
                print(f"Birth Date:     {personal.get('birth_date')}")
                print(f"Gender:         {personal.get('gender')}")
                print(f"ID Country:     {personal.get('id_country_of_issue')}")

                # License Info
                license_info = result.get('license_info', {})
                print("\n--- LICENSE INFORMATION ---")
                print(f"License Number:     {license_info.get('license_number')}")
                print(f"Issue Number:       {license_info.get('license_issue_number')}")
                print(f"Issue Date:         {license_info.get('license_issue_date')}")
                print(f"Expiry Date:        {license_info.get('license_expiry_date')}")
                print(f"License Country:    {license_info.get('license_country_of_issue')}")
                print(f"Vehicle Codes:      {', '.join(license_info.get('vehicle_codes', []))}")
                print(f"Restrictions:       {', '.join(license_info.get('vehicle_restrictions', []))}")
                print(f"Code Issue Dates:   {', '.join(license_info.get('license_code_issue_dates', []))}")
                print(f"Driver Restrictions: {license_info.get('driver_restriction_codes')}")

                # PRDP Info
                prdp = result.get('prdp_info', {})
                if prdp.get('code'):
                    print("\n--- PRDP INFORMATION ---")
                    print(f"PRDP Code:          {prdp.get('code')}")
                    print(f"PRDP Expiry:        {prdp.get('expiry_date')}")

                print("\n" + "="*80)
                print("RSA DECRYPTION SUCCESSFUL!")
                print("="*80)

            elif license_type == 'SA_VEHICLE_DISC':
                print("\n>> This is a Vehicle Disc, not a Driver's License")
                print("For driver's license test, use the BACK of the license card")

            else:
                print(f"\n>> Unknown document type: {license_type}")
                print(f"Raw data length: {result.get('data_length')}")

        else:
            print("\n>> DECODING FAILED")
            print(f"Error: {result.get('error')}")
            if 'hint' in result:
                print(f"Hint: {result.get('hint')}")

        # Save full result
        output_file = 'driver_license_result.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull result saved to: {output_file}")

        return result

    except Exception as e:
        print(f"\n>> ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # Default path - update this with your license back image path
    default_path = r"C:\Projects\Multi-Model-OCR\test_images\DLC\license_back.jpg"

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = default_path

    print("\n" + "="*80)
    print("INSTRUCTIONS:")
    print("="*80)
    print("1. Take a clear photo of the BACK of the SA driver's license")
    print("2. Ensure the PDF417 barcode is visible and in focus")
    print("3. Save the image to test_images/DLC/ folder")
    print("4. Run: python test_driver_license.py <path_to_image>")
    print("="*80)

    import os
    if not os.path.exists(image_path):
        print(f"\nImage not found: {image_path}")
        print("\nUsage: python test_driver_license.py <path_to_license_back_image>")
        print("\nExample:")
        print('  python test_driver_license.py "C:\\Projects\\Multi-Model-OCR\\test_images\\DLC\\license_back.jpg"')
        sys.exit(1)

    test_license(image_path)
