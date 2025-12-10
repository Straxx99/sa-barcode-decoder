"""
Test all SA license disc images with preprocessing
"""
import requests
import base64
from pathlib import Path
from PIL import Image, ImageEnhance
import io

test_dir = Path(r"C:\Projects\Multi-Model-OCR\test_images\VLD")
images = list(test_dir.glob("*.jpg"))

def preprocess_image(image, method):
    """Apply different preprocessing methods"""
    if method == "original":
        return image
    elif method == "grayscale":
        return image.convert('L').convert('RGB')
    elif method == "high_contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(2.0)
    elif method == "sharp":
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(2.0)
    elif method == "bright":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.5)
    return image

def test_image(image_path, method="original"):
    """Test decoding with different preprocessing"""
    # Open and preprocess image
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    img = preprocess_image(img, method)

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Send to API
    response = requests.post(
        'http://localhost:5000/decode',
        json={'image': image_data},
        timeout=30
    )

    return response.json()

print("=" * 60)
print("Testing SA License Disc Images")
print("=" * 60)

preprocessing_methods = ["original", "grayscale", "high_contrast", "sharp", "bright"]

for img_path in images:
    print(f"\nImage: {img_path.name}")
    print("-" * 60)

    for method in preprocessing_methods:
        result = test_image(img_path, method)

        if result.get('success'):
            print(f"  SUCCESS with '{method}' preprocessing!")
            print(f"  Found {result['count']} barcode(s)")
            for barcode in result['barcodes']:
                print(f"  Data length: {len(barcode.get('data', ''))}")
                print(f"  Preview: {barcode.get('data', '')[:100]}...")
            break
        else:
            print(f"  {method}: No barcode found")
    else:
        print(f"  FAILED: No preprocessing method worked")

print("\n" + "=" * 60)
