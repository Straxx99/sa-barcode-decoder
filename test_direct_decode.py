"""
Test PDF417 decoding directly without API
"""
from PIL import Image, ImageEnhance
from pdf417decoder import PDF417Decoder

image_path = r"C:\Projects\Multi-Model-OCR\test_images\VLD\IMG-20251104-WA0005.jpg"

print(f"Loading image: {image_path}")
img = Image.open(image_path)

print(f"Image mode: {img.mode}, Size: {img.size}")

# Convert to RGB
if img.mode != 'RGB':
    img = img.convert('RGB')

# Try with brightness enhancement
print("\nTrying with brightness enhancement...")
bright_img = ImageEnhance.Brightness(img).enhance(1.5)

decoder = PDF417Decoder(bright_img)
count = decoder.decode()

print(f"Decode count: {count}")

if count > 0:
    print("SUCCESS!")
    for i in range(count):
        data = decoder.barcode_data_index_to_string(i)
        print(f"\nBarcode {i+1}:")
        print(f"Length: {len(data)}")
        print(f"Data: {data}")
else:
    print("No barcode found")
