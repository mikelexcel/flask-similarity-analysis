import logging
from pathlib import Path
import pytesseract
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

_UPSCALE_FACTOR = 4

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts and returns all text found in the image at image_path.
    
    Verify the file exists, convert to greyscale (colour carries no information 
    for OCR and removing it reduces noise for Tesseract), sharpen and upscale 
    four times with LANCZOS.
    Returns an empty string if the file is missing or OCR fails.
    """
    path = Path(image_path)
    if not path.exists():
        logger.error("Image not found: %s", image_path)
        return ""

    try:
        with Image.open(path) as image:
            # Convert to greyscale so sharpening and resizing work on single channel
            image = image.convert("L")

            # Sharpen to nudge blurry characters towards crisper edges
            image = image.filter(ImageFilter.SHARPEN)

            width, height = image.size
            image = image.resize(
                (width * _UPSCALE_FACTOR, height * _UPSCALE_FACTOR),
                Image.Resampling.LANCZOS
            )

            text = pytesseract.image_to_string(image).strip()
            logger.debug("OCR extracted %d characters from %s", len(text), path.name)
            return text

    except Exception as e:
        logger.error("OCR failed for %s: %s", image_path, e)
        return ""