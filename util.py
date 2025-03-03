# Utility code


from io import BytesIO
from PIL import Image
import requests
import logging


def download_and_compress_image(url: str, webp_path: str, quality=85) -> bool:
    # Download the image
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to download image from {url}")
        return False

    img = Image.open(BytesIO(response.content))
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Save as WebP
    img.save(webp_path, "WEBP", quality=quality)
    logging.info(f"Downloaded file to {webp_path}")
    return True
