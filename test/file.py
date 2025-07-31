import pytesseract
from PIL import Image
import os
import fitz

os.environ["HTTP_PROXY"] = "proxy_amer.safran:9009"
os.environ["HTTPS_PROXY"] = "proxy_amer.safran:9009"

scan_folder = R"C:\Users\UP60071088\Documents\Scan"
local_folder = "C:\\Users\\UP60071088\\Documents\\AutoFilter\\"

cropped_folder = os.path.join(local_folder, "cropped")
converted_folder = os.path.join(local_folder, "converted")
filtered_folder = os.path.join(local_folder, "filtered")
unreadable_folder = os.path.join(local_folder, "unreadable")


def get_file(filename):
    input_file = fitz.open(os.path.join(local_folder, filename))
    cropped_file = os.path.join(cropped_folder, filename)
    converted_file = os.path.join(converted_folder, filename)

    for page in input_file:
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        ocr_text = pytesseract.image_to_string(image, lang="fra")

        print(ocr_text)
        break


import numpy as np

get_file("example.pdf")
