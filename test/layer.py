import pytesseract
import cv2
from pdf2image import convert_from_path
import re

# Path to the Tesseract executable (if not in PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)


def extract_text_with_coordinates(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return data


def find_text_near_pattern(data, pattern):
    results = []
    pattern_re = re.compile(pattern)

    for i, text in enumerate(data["text"]):
        if pattern_re.search(text):
            # Check to the right
            if i + 1 < len(data["text"]) and data["top"][i] == data["top"][i + 1]:
                results.append(data["text"][i + 1])
            # Check below
            elif i + 1 < len(data["text"]) and data["left"][i] == data["left"][i + 1]:
                results.append(data["text"][i + 1])

    return results


def main(pdf_path, pattern):
    images = pdf_to_images(pdf_path)

    for image in images:
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        data = extract_text_with_coordinates(image_cv)
        results = find_text_near_pattern(data, pattern)

        for result in results:
            print(f"Found text near pattern: {result}")


# Example usage
pdf_path = "path_to_your_file.pdf"
pattern = "your_special_text_string"
main(pdf_path, pattern)
