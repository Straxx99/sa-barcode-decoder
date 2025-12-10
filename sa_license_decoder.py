"""
South African Driver's License Decoder
Decodes, decrypts and parses SA driving license PDF417 barcodes

Based on: https://www.dynamsoft.com/codepool/south-africa-driving-license-python.html
"""

import rsa
from typing import Dict, List, Optional

# RSA Public Keys for SA Driver's License Decryption
# Version 1 keys
pk_v1_128 = '''-----BEGIN RSA PUBLIC KEY-----
MIGXAoGBAP7S4cJ+M2MxbncxenpSxUmBOVGGvkl0dgxyUY1j4FRKSNCIszLFsMNw
x2XWXZg8H53gpCsxDMwHrncL0rYdak3M6sdXaJvcv2CEePrzEvYIfMSWw3Ys9cRl
HK7No0mfrn7bfrQOPhjrMEFw6R7VsVaqzm9DLW7KbMNYUd6MZ49nAhEAu3l//ex/
nkLJ1vebE3BZ2w==
-----END RSA PUBLIC KEY-----'''

pk_v1_74 = '''-----BEGIN RSA PUBLIC KEY-----
MGACSwD/POxrX0Djw2YUUbn8+u866wbcIynA5vTczJJ5cmcWzhW74F7tLFcRvPj1
tsj3J221xDv6owQNwBqxS5xNFvccDOXqlT8MdUxrFwIRANsFuoItmswz+rfY9Cf5
zmU=
-----END RSA PUBLIC KEY-----'''

# Version 2 keys
pk_v2_128 = '''-----BEGIN RSA PUBLIC KEY-----
MIGWAoGBAMqfGO9sPz+kxaRh/qVKsZQGul7NdG1gonSS3KPXTjtcHTFfexA4MkGA
mwKeu9XeTRFgMMxX99WmyaFvNzuxSlCFI/foCkx0TZCFZjpKFHLXryxWrkG1Bl9+
+gKTvTJ4rWk1RvnxYhm3n/Rxo2NoJM/822Oo7YBZ5rmk8NuJU4HLAhAYcJLaZFTO
sYU+aRX4RmoF
-----END RSA PUBLIC KEY-----'''

pk_v2_74 = '''-----BEGIN RSA PUBLIC KEY-----
MF8CSwC0BKDfEdHKz/GhoEjU1XP5U6YsWD10klknVhpteh4rFAQlJq9wtVBUc5Dq
bsdI0w/bga20kODDahmGtASy9fae9dobZj5ZUJEw5wIQMJz+2XGf4qXiDJu0R2U4
Kw==
-----END RSA PUBLIC KEY-----'''


def detect_version(data: bytes) -> int:
    """Detect SA license version (1 or 2)"""
    v1 = [0x01, 0xe1, 0x02, 0x45]
    v2 = [0x01, 0x9b, 0x09, 0x45]

    if data[:4] == bytes(v1):
        return 1
    elif data[:4] == bytes(v2):
        return 2
    else:
        return 0


def decrypt_data(data: bytes) -> bytes:
    """Decrypt SA license data using RSA public keys"""
    if len(data) != 720:
        raise ValueError(f"Invalid data length: {len(data)}, expected 720 bytes")

    version = detect_version(data)
    if version == 0:
        raise ValueError("Unknown license version")

    # Select appropriate keys
    if version == 1:
        pk128 = pk_v1_128
        pk74 = pk_v1_74
    else:
        pk128 = pk_v2_128
        pk74 = pk_v2_74

    # Decrypt the 5 blocks of 128 bytes
    all_bytes = bytearray()
    pubKey = rsa.PublicKey.load_pkcs1(pk128.encode())

    start = 6  # Skip first 6 bytes (version + zeros)
    for i in range(5):
        block = data[start: start + 128]
        input_val = int.from_bytes(block, byteorder='big', signed=False)
        output_val = pow(input_val, pubKey.e, mod=pubKey.n)

        decrypted_bytes = output_val.to_bytes(128, byteorder='big', signed=False)
        all_bytes += decrypted_bytes

        start = start + 128

    # Decrypt the last block of 74 bytes
    pubKey = rsa.PublicKey.load_pkcs1(pk74.encode())
    block = data[start: start + 74]
    input_val = int.from_bytes(block, byteorder='big', signed=False)
    output_val = pow(input_val, pubKey.e, mod=pubKey.n)

    decrypted_bytes = output_val.to_bytes(74, byteorder='big', signed=False)
    all_bytes += decrypted_bytes

    return bytes(all_bytes)


def read_string(data: bytes, index: int) -> tuple:
    """Read a single string from data"""
    value = ''
    delimiter = 0xe0

    while True:
        currentByte = data[index]
        index += 1

        if currentByte == 0xe0 or currentByte == 0xe1:
            delimiter = currentByte
            break

        value += chr(currentByte)

    return value, index, delimiter


def read_strings(data: bytes, index: int, length: int) -> tuple:
    """Read multiple strings from data"""
    strings = []

    i = 0
    while i < length:
        value = ''
        while True:
            currentByte = data[index]
            index += 1

            if currentByte == 0xe0:
                break
            elif currentByte == 0xe1:
                if value != '':
                    i += 1
                break

            value += chr(currentByte)

        i += 1

        if value != '':
            strings.append(value)

    return strings, index


def read_nibble_date_string(nibble_queue: list) -> str:
    """Read date from nibble queue"""
    m = nibble_queue.pop(0)
    if m == 10:
        return ''

    c = nibble_queue.pop(0)
    d = nibble_queue.pop(0)
    y = nibble_queue.pop(0)

    m1 = nibble_queue.pop(0)
    m2 = nibble_queue.pop(0)

    d1 = nibble_queue.pop(0)
    d2 = nibble_queue.pop(0)

    return f'{m}{c}{d}{y}-{m1}{m2}-{d1}{d2}'


def read_nibble_date_list(nibble_queue: list, length: int) -> list:
    """Read multiple dates from nibble queue"""
    date_list = []

    for i in range(length):
        date_string = read_nibble_date_string(nibble_queue)
        if date_string != '':
            date_list.append(date_string)

    return date_list


def parse_data(data: bytes) -> Dict:
    """Parse decrypted SA license data"""
    # Find the start of strings section (0x82 marker)
    index = 0
    for i in range(len(data)):
        if data[i] == 0x82:
            index = i
            break

    if index == 0:
        raise ValueError("Could not find string section marker (0x82)")

    # Skip marker and next byte
    index += 2

    # Read all string fields
    vehicle_codes, index = read_strings(data, index, 4)
    surname, index, delimiter = read_string(data, index)
    initials, index, delimiter = read_string(data, index)

    prdp_code = ''
    if delimiter == 0xe0:
        prdp_code, index, delimiter = read_string(data, index)

    id_country_of_issue, index, delimiter = read_string(data, index)
    license_country_of_issue, index, delimiter = read_string(data, index)

    vehicle_restrictions, index = read_strings(data, index, 4)
    license_number, index, delimiter = read_string(data, index)

    # Read ID number (13 characters)
    id_number = ''
    for i in range(13):
        id_number += chr(data[index])
        index += 1

    id_number_type = f'{data[index]:02d}'
    index += 1

    # Read binary nibble data
    nibble_queue = []
    while True:
        currentByte = data[index]
        index += 1
        if currentByte == 0x57:
            break

        nibbles = [currentByte >> 4, currentByte & 0x0f]
        nibble_queue += nibbles

    # Parse nibble data
    license_code_issue_dates = read_nibble_date_list(nibble_queue, 4)
    driver_restriction_codes = f'{nibble_queue.pop(0)}{nibble_queue.pop(0)}'
    prdp_permit_expiry_date = read_nibble_date_string(nibble_queue)
    license_issue_number = f'{nibble_queue.pop(0)}{nibble_queue.pop(0)}'
    birthdate = read_nibble_date_string(nibble_queue)
    license_issue_date = read_nibble_date_string(nibble_queue)
    license_expiry_date = read_nibble_date_string(nibble_queue)

    gender_code = f'{nibble_queue.pop(0)}{nibble_queue.pop(0)}'
    gender = 'Male' if gender_code == '01' else 'Female'

    # Return structured data
    return {
        'success': True,
        'license_type': 'SA_DRIVER_LICENSE',
        'version': detect_version(data),
        'personal_info': {
            'surname': surname,
            'initials': initials,
            'id_number': id_number,
            'id_number_type': id_number_type,
            'id_country_of_issue': id_country_of_issue,
            'birth_date': birthdate,
            'gender': gender
        },
        'license_info': {
            'license_number': license_number,
            'license_country_of_issue': license_country_of_issue,
            'license_issue_number': license_issue_number,
            'license_issue_date': license_issue_date,
            'license_expiry_date': license_expiry_date,
            'vehicle_codes': vehicle_codes,
            'vehicle_restrictions': vehicle_restrictions,
            'license_code_issue_dates': license_code_issue_dates,
            'driver_restriction_codes': driver_restriction_codes
        },
        'prdp_info': {
            'code': prdp_code,
            'expiry_date': prdp_permit_expiry_date
        }
    }


def decode_sa_license(barcode_bytes: bytes) -> Dict:
    """
    Main function to decode SA driver's license

    Args:
        barcode_bytes: Raw bytes from PDF417 barcode

    Returns:
        Dictionary with parsed license data
    """
    try:
        if len(barcode_bytes) != 720:
            return {
                'success': False,
                'error': f'Invalid barcode length: {len(barcode_bytes)}, expected 720 bytes'
            }

        # Decrypt the data
        decrypted_data = decrypt_data(barcode_bytes)

        # Parse the decrypted data
        result = parse_data(decrypted_data)

        return result

    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to decode SA license: {str(e)}'
        }


def decode_sa_vehicle_disc(barcode_text: str) -> Dict:
    """
    Decode SA vehicle license disc (not encrypted, just text parsing)

    Format: %MVL2DD93%0153%1099A6ML%1%10990565X1GW%CFM11111%DTR111K%...
    """
    try:
        parts = barcode_text.split('%')

        if len(parts) < 10:
            return {
                'success': False,
                'error': 'Invalid vehicle disc format'
            }

        return {
            'success': True,
            'license_type': 'SA_VEHICLE_DISC',
            'control_number': parts[1] if len(parts) > 1 else '',
            'license_number': parts[2] if len(parts) > 2 else '',
            'register_number': parts[3] if len(parts) > 3 else '',
            'meta4': parts[4] if len(parts) > 4 else '',
            'disk_number': parts[5] if len(parts) > 5 else '',
            'vin': parts[6] if len(parts) > 6 else '',
            'engine_number': parts[7] if len(parts) > 7 else '',
            'description': parts[8] if len(parts) > 8 else '',
            'make': parts[9] if len(parts) > 9 else '',
            'model': parts[10] if len(parts) > 10 else '' if len(parts) > 10 else '',
            'color': parts[11] if len(parts) > 11 else '',
            'expiry_date': parts[12] if len(parts) > 12 else ''
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to parse vehicle disc: {str(e)}'
        }
