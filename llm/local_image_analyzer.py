from PIL import Image
import pytesseract
import os
import base64
import io

class LocalImageAnalyzer:
    """
    Analyzes images locally using Tesseract OCR.
    No external API calls are made.
    """
    def __init__(self):
        tesseract_path = os.getenv("TESSERACT_PATH")
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
        self.tesseract_available = False
        try:
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
        except Exception:
            pass

    def analyze(self, base64_image: str, query: str = "") -> str:
        try:
            image_bytes = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("RGB")

            ocr_text = ""
            if self.tesseract_available:
                try:
                    ocr_text = pytesseract.image_to_string(image, lang="eng")
                    ocr_text = ocr_text.strip()
                except Exception as e:
                    print(f"OCR Error: {e}")
                    ocr_text = ""

            width, height = image.size

            description_parts = []
            if ocr_text:
                description_parts.append(f"Text found in image: {ocr_text}")
            description_parts.append(f"Image dimensions: {width}x{height} pixels")

            return "\n".join(description_parts) if description_parts else "No text found in image."
        except Exception as e:
            return f"Error analyzing image locally: {e}"
            
    def analyze_image(self, base64_image: str, query: str = "") -> str:
        # Alias for backward compatibility with app.py if needed, though app.py will be updated to use .analyze() or we just map it here
        return self.analyze(base64_image, query)
        
    def is_mind_map(self, base64_image: str) -> bool:
        # Local fallback since we don't have a vision model to easily classify this offline without downloading another heavy model.
        return False

    def is_ready(self) -> bool:
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
