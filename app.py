"""
Flask API for PDF417 Barcode Decoding
Uses pdf417decoder - Pure Python PDF417 decoder with excellent support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf417decoder import PDF417Decoder
from PIL import Image, ImageEnhance
import io
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

@app.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'Barcode Decoding API',
        'version': '2.0',
        'decoder': 'pdf417decoder (Pure Python)',
        'endpoints': {
            '/health': 'GET - Health check',
            '/decode': 'POST - Decode barcode from base64 image'
        },
        'instructions': 'Open barcode-test-python-api.html in your browser to test'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'decoder': 'pdf417decoder (Pure Python)'})

def try_decode_with_preprocessing(original_image):
    """
    Try decoding with different preprocessing methods
    Returns (success, barcode_data, method_used)
    """
    # Define preprocessing functions
    def preprocess_original(img):
        return img

    def preprocess_bright(img):
        return ImageEnhance.Brightness(img).enhance(1.5)

    def preprocess_high_contrast(img):
        return ImageEnhance.Contrast(img).enhance(2.0)

    def preprocess_sharp(img):
        return ImageEnhance.Sharpness(img).enhance(2.0)

    def preprocess_grayscale(img):
        return img.convert('L').convert('RGB')

    def preprocess_very_bright(img):
        return ImageEnhance.Brightness(img).enhance(2.0)

    preprocessing_methods = [
        ("original", preprocess_original),
        ("bright", preprocess_bright),
        ("high_contrast", preprocess_high_contrast),
        ("sharp", preprocess_sharp),
        ("grayscale", preprocess_grayscale),
        ("very_bright", preprocess_very_bright),
    ]

    for method_name, preprocess_func in preprocessing_methods:
        try:
            # Create a copy of the original image
            img_copy = original_image.copy()

            # Apply preprocessing
            processed_img = preprocess_func(img_copy)

            # Ensure it's a valid PIL Image
            if not isinstance(processed_img, Image.Image):
                continue

            # Try to decode
            decoder = PDF417Decoder(processed_img)
            decode_count = decoder.decode()

            if decode_count > 0:
                # Success! Extract all barcodes
                results = []
                for i in range(decode_count):
                    barcode_text = decoder.barcode_data_index_to_string(i)
                    results.append({
                        'type': 'PDF417',
                        'data': barcode_text,
                        'raw': barcode_text
                    })
                return True, results, method_name
        except Exception as e:
            # Try next method
            print(f"Method {method_name} failed: {str(e)}")
            continue

    return False, [], None


@app.route('/decode', methods=['POST'])
def decode_barcode():
    """
    Decode barcode from image with automatic preprocessing

    Request body:
    {
        "image": "base64_encoded_image_data"
    }

    Response:
    {
        "success": true,
        "barcodes": [
            {
                "type": "PDF417",
                "data": "raw barcode text"
            }
        ],
        "preprocessing_used": "bright"
    }
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image provided'}), 400

        # Decode base64 image
        image_data = data['image']

        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data)

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Try decoding with different preprocessing methods
        success, results, method_used = try_decode_with_preprocessing(image)

        if not success:
            return jsonify({
                'success': False,
                'error': 'No PDF417 barcode found in image after trying multiple preprocessing methods',
                'barcodes': []
            })

        return jsonify({
            'success': True,
            'barcodes': results,
            'count': len(results),
            'preprocessing_used': method_used
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {error_details}")  # Log to console
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
