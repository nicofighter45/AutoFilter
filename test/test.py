import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
os.environ["TESSDATA_PREFIX"] = "C:/Users/UP60071088/Documents/AutoFilter/application/ressources/tesseract_lang"

LOCAL_FOLDER = "C:\\Users\\UP60071088\\Documents\\AutoFilter\\"
ORIGINAL_FOLDER = os.path.join(LOCAL_FOLDER, "files\\original")

# Get all files in the ORIGINAL_FOLDER
files_in_folder = [f for f in os.listdir(ORIGINAL_FOLDER) if os.path.isfile(os.path.join(ORIGINAL_FOLDER, f))]
import fitz  # PyMuPDF

# Convert all PDF files in the folder to images
for file_name in files_in_folder:
    if file_name.lower().endswith('.pdf'):
        pdf_path = os.path.join(ORIGINAL_FOLDER, file_name)
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, lang="fra")
        print(text)
        doc.close()
        input("\n\n\nPress Enter to continue...")