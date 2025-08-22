import os

# pas toucher
LOCAL_FOLDER = os.path.dirname(os.path.abspath(__file__))

## vous pouvez toucher à ces fichiers là
SCAN_FOLDER = R"\\suli-dfs.corp.zodiac.lan\LES_ULIS\DI\_GROUP\scan\AutoFilter"
TESSERACT_EXE = R"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
UNREADABLE_FOLDER = os.path.join(LOCAL_FOLDER, "files\\unreadable")
FILTERED_FOLDER = os.path.join(LOCAL_FOLDER, "files\\filtered")


TESSERACT_LANG_FOLDER = os.path.join(
    LOCAL_FOLDER, "application\\ressources\\tesseract_lang"
)

print("Scanned file folder is", SCAN_FOLDER)
print("Local folder is", LOCAL_FOLDER)
print("Tesseract executable folder is", TESSERACT_EXE)
print("You can change those paths in the path.py file (using the folder configuration on your desktop)")

os.makedirs(UNREADABLE_FOLDER, exist_ok=True)
os.makedirs(FILTERED_FOLDER, exist_ok=True)
