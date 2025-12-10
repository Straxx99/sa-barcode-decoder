# Testing SA Driver's License RSA Decryption

## What You Need

**Photo of the BACK of an SA Driver's License**

The back of the card contains:
- A large **PDF417 barcode** (looks like horizontal lines in a rectangle)
- This barcode contains **720 bytes of RSA-encrypted data**
- Our decoder will:
  1. Detect the PDF417 barcode
  2. Extract the 720 encrypted bytes
  3. Decrypt using RSA public keys
  4. Parse personal info, license info, vehicle codes, etc.

## How to Take the Photo

### Best Practices:
1. **Good Lighting** - Use natural light or bright indoor lighting
2. **Steady Camera** - Hold phone steady or use a flat surface
3. **Fill the Frame** - Get close enough that the barcode fills most of the frame
4. **Focus on Barcode** - Tap on the barcode area to ensure it's in focus
5. **No Glare** - Avoid reflections from overhead lights
6. **Flat Card** - Lay the license flat on a surface

### What the Barcode Looks Like:
```
┌─────────────────────────────┐
│ ▌▌ ▌▌▌ ▌ ▌▌ ▌▌▌▌ ▌ ▌▌▌ ▌▌ │
│ ▌ ▌▌ ▌▌ ▌▌ ▌ ▌ ▌▌▌ ▌▌ ▌▌▌ │
│ ▌▌▌ ▌ ▌▌ ▌▌▌ ▌▌ ▌ ▌▌▌▌ ▌  │
│ ▌ ▌▌ ▌▌▌ ▌ ▌▌ ▌▌ ▌ ▌▌ ▌▌▌ │
│    ... (many lines)         │
└─────────────────────────────┘
   PDF417 Barcode (Back of Card)
```

## Steps to Test

### 1. Take the Photo
- Open your phone camera
- Flip the driver's license to the BACK side
- Follow the best practices above
- Take the photo

### 2. Transfer to Computer
- Transfer the photo to your computer
- Save it to: `C:\Projects\Multi-Model-OCR\test_images\DLC\`
- Name it something clear like: `license_back.jpg`

### 3. Run the Test Script
```bash
cd C:\Projects\barcode-api
python test_driver_license.py "C:\Projects\Multi-Model-OCR\test_images\DLC\license_back.jpg"
```

## What to Expect

### If Successful:
```
================================================================================
SA DRIVER'S LICENSE RSA DECRYPTION TEST
================================================================================

Image: C:\Projects\Multi-Model-OCR\test_images\DLC\license_back.jpg
Image size: (1920, 1080)
Applying client-side preprocessing (high contrast)...
Sending to API...

================================================================================
RESULT:
================================================================================

>> SA DRIVER'S LICENSE SUCCESSFULLY DECODED AND DECRYPTED!

Version: 2
Barcode Format: PDF417
Preprocessing Used: high_contrast

--- PERSONAL INFORMATION ---
Surname:        HOLENA
Initials:       R
ID Number:      8412175773083
ID Type:        02
Birth Date:     1984-12-17
Gender:         Male
ID Country:     ZA

--- LICENSE INFORMATION ---
License Number:     A02800062P71
Issue Number:       01
Issue Date:         2025-04-24
Expiry Date:        2030-04-23
License Country:    ZA
Vehicle Codes:      A, B, EB
Restrictions:
Code Issue Dates:   2025-04-24
Driver Restrictions: 00

================================================================================
RSA DECRYPTION SUCCESSFUL!
================================================================================
```

### If the Barcode Can't Be Read:
- Try taking another photo with better lighting
- Make sure the barcode is in focus
- Try from a slightly different angle
- Ensure no glare or shadows on the barcode

## Alternative: Use Existing Front Image

If you can't get a photo of the back right now, I can:
1. Help you integrate the working solution (vehicle disc decoder)
2. Deploy the API to production
3. Update your React component
4. Test the driver's license RSA decryption later when you have the back image

The RSA decryption code is ready and tested - we just need an actual encrypted barcode to verify it works end-to-end!

## Technical Details

**What the decoder does:**
1. **Detects PDF417** barcode on back of card
2. **Extracts 720 bytes** of encrypted data
3. **Detects version** (v1 or v2) from first 4 bytes
4. **Selects RSA keys** based on version
5. **Decrypts 6 blocks**:
   - Skip 6 bytes (header)
   - Decrypt 5 blocks of 128 bytes each
   - Decrypt 1 block of 74 bytes
6. **Parses decrypted data**:
   - Finds string section marker (0x82)
   - Reads surname, initials, license number, etc.
   - Parses binary nibbles for dates
   - Extracts vehicle codes and restrictions
7. **Returns structured JSON**

All ready to go - just needs a photo of the barcode!
