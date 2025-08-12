import os

SCAN_FOLDER = R"C:\\Users\\UP60071088\\Documents\\Scan"
LOCAL_FOLDER = "C:\\Users\\UP60071088\\Documents\\AutoFilter\\"
TESSERACT_EXE = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

TESSERACT_LANG_FOLDER = os.path.join(
    LOCAL_FOLDER, "application\\ressources\\tesseract_lang"
)
UNREADABLE_FOLDER = os.path.join(LOCAL_FOLDER, "files\\unreadable")
FILTERED_FOLDER = os.path.join(LOCAL_FOLDER, "files\\filtered")
