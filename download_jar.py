"""
Download ZXing JAR file from Maven Central
"""
import urllib.request
import shutil
import os

jar_url = "https://github.com/zxing/zxing/releases/download/zxing-3.5.3/javase-3.5.3.jar"
save_path = "zxing/javase/target/javase-3.5.3-jar-with-dependencies.jar"

print(f"Downloading ZXing JAR from Maven Central...")
print(f"URL: {jar_url}")
print(f"Saving to: {save_path}")

# Create directory if needed
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Download with proper headers
req = urllib.request.Request(
    jar_url,
    headers={'User-Agent': 'Mozilla/5.0'}
)

with urllib.request.urlopen(req) as response:
    file_size = response.headers.get('Content-Length')
    if file_size:
        print(f"File size: {int(file_size) / 1024 / 1024:.2f} MB")

    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

print("✓ Download completed successfully!")
print(f"File saved to: {os.path.abspath(save_path)}")
