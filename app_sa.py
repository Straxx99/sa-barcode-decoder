"""
Flask API for South African Document Decoding
Decodes and decrypts SA driver's licenses and vehicle discs
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf417decoder import PDF417Decoder
from PIL import Image, ImageEnhance
import io
import base64
import sys
from sa_license_decoder import decode_sa_license, decode_sa_vehicle_disc

app = Flask(__name__)
CORS(app)  # Enable CORS for React app


@app.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'SA Document Decoding API',
        'version': '3.0',
        'decoder': 'pdf417decoder + RSA decryption (SA-specific)',
        'supported_documents': [
            'SA Driver License (encrypted PDF417)',
            'SA Vehicle License Disc (text PDF417)'
        ],
        'endpoints': {
            '/health': 'GET - Health check',
            '/decode': 'POST - Decode SA document from base64 image'
        },
        'instructions': 'Handles RSA decryption for SA driver licenses automatically'
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'decoder': 'pdf417decoder + RSA (SA)',
        'encryption_support': True
    })


def try_decode_with_preprocessing(original_image):
    """
    Try decoding with different preprocessing methods
    Returns (success, barcode_data, barcode_bytes, method_used)
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
            print(f"DEBUG: Trying preprocessing method: {method_name}", file=sys.stderr, flush=True)
            # Create a copy of the original image
            img_copy = original_image.copy()

            # Apply preprocessing
            processed_img = preprocess_func(img_copy)
            print(f"DEBUG: Preprocessing applied successfully", file=sys.stderr, flush=True)

            # Ensure it's a valid PIL Image
            if not isinstance(processed_img, Image.Image):
                print(f"DEBUG: Not a valid PIL Image after preprocessing", file=sys.stderr, flush=True)
                continue

            # Try to decode
            print(f"DEBUG: Creating PDF417Decoder...", file=sys.stderr, flush=True)
            decoder = PDF417Decoder(processed_img)
            print(f"DEBUG: Calling decoder.decode()...", file=sys.stderr, flush=True)
            decode_count = decoder.decode()
            print(f"DEBUG: decode_count = {decode_count}", file=sys.stderr, flush=True)

            if decode_count > 0:
                # Success! Get barcode data and raw bytes
                barcode_text = decoder.barcode_data_index_to_string(0)

                # Debug: Print all decoder attributes
                print(f"DEBUG: decode_count = {decode_count}", file=sys.stderr, flush=True)
                print(f"DEBUG: decoder attributes: {dir(decoder)}", file=sys.stderr, flush=True)

                # Try to get raw bytes from barcode_binary_data attribute
                barcode_bytes = None
                if hasattr(decoder, 'barcode_binary_data'):
                    print(f"DEBUG: barcode_binary_data exists: {decoder.barcode_binary_data is not None}", file=sys.stderr, flush=True)
                    barcode_bytes = decoder.barcode_binary_data
                if hasattr(decoder, 'barcodes_data'):
                    print(f"DEBUG: barcodes_data exists: {decoder.barcodes_data is not None}", file=sys.stderr, flush=True)
                    if decoder.barcodes_data and len(decoder.barcodes_data) > 0:
                        barcode_bytes = decoder.barcodes_data[0]

                print(f"DEBUG: barcode_text length: {len(barcode_text) if barcode_text else 0}", file=sys.stderr, flush=True)
                print(f"DEBUG: barcode_bytes type: {type(barcode_bytes)}", file=sys.stderr, flush=True)
                print(f"DEBUG: barcode_bytes length: {len(barcode_bytes) if barcode_bytes else 0}", file=sys.stderr, flush=True)

                return True, barcode_text, barcode_bytes, method_name
        except Exception as e:
            # Try next method
            print(f"Method {method_name} failed: {str(e)}", file=sys.stderr, flush=True)
            continue

    return False, None, None, None


@app.route('/decode', methods=['POST'])
def decode_document():
    """
    Decode SA document from image with automatic decryption

    Request body:
    {
        "image": "base64_encoded_image_data"
    }

    Response for SA Driver License:
    {
        "success": true,
        "license_type": "SA_DRIVER_LICENSE",
        "version": 2,
        "personal_info": {
            "surname": "DOE",
            "initials": "J",
            "id_number": "1234567890123",
            ...
        },
        "license_info": {...},
        "preprocessing_used": "high_contrast"
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
        success, barcode_text, barcode_bytes, method_used = try_decode_with_preprocessing(image)

        if not success:
            return jsonify({
                'success': False,
                'error': 'No PDF417 barcode found in image after trying multiple preprocessing methods',
                'hint': 'Ensure good lighting, focus, and that the barcode is clearly visible'
            })

        # Determine document type and decode accordingly
        result = {}

        # Check if it's an encrypted SA driver license (720 bytes)
        if barcode_bytes and len(barcode_bytes) == 720:
            print(f"Detected SA Driver License (720 bytes), decrypting...")
            result = decode_sa_license(barcode_bytes)
            result['preprocessing_used'] = method_used
            result['barcode_format'] = 'PDF417'

        # Check if it's a vehicle disc (starts with %)
        elif barcode_text and barcode_text.startswith('%'):
            print(f"Detected SA Vehicle Disc (text format)")
            result = decode_sa_vehicle_disc(barcode_text)
            result['preprocessing_used'] = method_used
            result['barcode_format'] = 'PDF417'

        # Unknown format
        else:
            # Return raw data for debugging
            result = {
                'success': True,
                'license_type': 'UNKNOWN',
                'barcode_format': 'PDF417',
                'preprocessing_used': method_used,
                'raw_data': barcode_text,
                'data_length': len(barcode_bytes) if barcode_bytes else len(barcode_text),
                'hint': 'Barcode decoded but format not recognized as SA license or vehicle disc'
            }

        return jsonify(result)

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
