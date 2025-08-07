import fitz
from PIL import Image, ImageDraw, ImageOps, ImageFilter
from constants.path import *
import pygame as pg
import os
import threading
import win32con
import win32gui
import difflib
import numpy as np
import pytesseract
import time
from image_processing import remove_lines

REMOVE_AT_THE_END = [":", " ", "`", "'", "\\v", "•", ".", "\n"]
REPLACE_AT_THE_END = [("OO", "00"), ("—", "-"), ("$", "S")]


def get_sequence(text, pattern, cutoff=0.9):
    pattern_length = len(pattern)
    for i in range(len(text) - pattern_length + 1):
        substring = text[i : i + pattern_length]
        similarity = difflib.SequenceMatcher(None, substring, pattern).ratio()
        #print(similarity, pattern, substring)
        if similarity >= cutoff:
            return i
    return -1


def has_sequence(text, pattern, cutoff=0.9):
    return get_sequence(text, pattern, cutoff) != -1


class Filter:

    def __init__(self, filename, app):
        self._file = os.path.join(SCAN_FOLDER, filename)
        self._name = ""
        self.app = app
        self.prepare_image()
        self._text = self.get_text()


    def prepare_image(self):
        self.doc = fitz.open(self._file)
        page = self.doc.load_page(self.app.page)
        dpi = 300
        # fitz default is 72 dpi, so scale factor is dpi / 72
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        self.pix = page.get_pixmap(matrix=mat)
        self.pre_img = Image.frombytes("RGB", [self.pix.width, self.pix.height], self.pix.samples)
        self.app.set_right_image(self.pre_img)
    
    def get_text(self, column=1, row=1, width_crop=1, height_crop=3):
        column -= 1
        row -= 1
        width, height = self.pix.width//width_crop, self.pix.height//height_crop
        box = (column*width, row*height, (column+1)*width, (row+1)*height)
        img = Image.fromarray(remove_lines(self.pre_img.crop(box)))
        self.app.set_left_image(img)
        text = pytesseract.image_to_string(img, lang="fra+eng")
        self._text = text
        print("\n\n\n", column, row, width_crop, height_crop, "\n", text, "\n\n\n")
        return text

    def __del__(self):
        if hasattr(self, "doc"):
            self.doc.close()
    
    def handle_SN_field(self, name, splitter, splitter_delta, *splitters):
        i = self._get_last_index_for_string(name)
        self.app.SN_input.default_text = name
        if i == -1:
            self.app.SN_input.set_text("")
        else:
            before_text = self._text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters):
                before_text = before_text.split(splitter)[0]
            for splitter in ["SN", "S/N"]:
                spl = before_text.split(splitter)
                if len(spl) > 1:
                    before_text = ''.join(spl[1:])
            text = self._clean_string(before_text)
            for (old, new) in [("O", "0"), ("A", "À")]:
                text = text.replace(old, new)
            text = ''.join(filter(lambda c: c.isdigit() or c == "À", text))
            if "À" in text:
                if text[0] == "À":
                    self.app.SN_input.set_text(text[1:min(len(text), 9)])
                elif text[-1] == "À":
                    self.app.SN_input.set_text(text[:-1])
                else:
                    self.app.SN_input.set_text(text[:min(len(text), 9)])
            else:
                self.app.SN_input.set_text(text[:min(len(text), 4)])
    
    def handle_reference_field(self, name, splitter, splitter_delta, *splitters):
        i = self._get_last_index_for_string(name)
        if i != -1:
            before_text = self._text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters) + ["+"]:
                before_text = before_text.split(splitter)[0]
            text = self._clean_string(before_text).replace("O", "0")
            text = ''.join(filter(lambda c: c.isdigit(), text))
            text = text[min(0,len(text)-2):]
            self.app.product_input.set_text(text + "-" + self.app.product_input.text)

    def handle_one_field(self, name, splitter, splitter_delta, input_field, *splitters):
        i = self._get_last_index_for_string(name)
        input_field.default_text = name
        if i == -1:
            input_field.set_text("")
        else:
            before_text = self._text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters) + ["+"]:
                before_text = before_text.split(splitter)[0]
            text = self._clean_string(before_text)
            for i in range(len(text)):
                char = text[i]
                if char == "O" and 0 < i < len(text)-1 and (text[i+1].isdigit() or text[i-1].isdigit()):
                    text = text[:i] + "0" + text[i+1:]
                elif char == "O" and i == 0:
                    text = "0" + text[1:]
                elif char == "0" and 0 < i < len(text)-1 and (text[i-1].isalpha() or text[i+1].isalpha()):
                    text = text[:i] + "O" + text[i+1:]
                elif char == "0" and i == len(text)-1 and text[i-1].isalpha():
                    text = text[:i] + "O" + text[i+1:]
            input_field.set_text(text)

    def has_title(self, *keys):
        for key in keys:
            if has_sequence(self._text, key):
                print("TITLE IS", key)
                return True
        return False

    def get_name_of_file(self):
        if self.has_title("SEQUENCES POUR UN OF", "Poste de\ncharge", "Temps\n prépa\n(h)"):
            self.handle_one_field("Produit", "\n", 0, self.app.product_input)
            self.handle_SN_field("Texte 2", "\n", 0)
            self.handle_one_field("Désignation", "\n", 0, self.app.designation_input)
        elif self.has_title("Check-list"):
            self.handle_one_field("Code article", "\n", 0, self.app.product_input, "Nom", "Date", "Cde")
            self.handle_SN_field("S/N", "\n", 0, "Nom", "Date", "Cde")
            self.handle_one_field("Désignation", "\n", 0, self.app.designation_input, "Nom", "Date", "Cde")
        elif self.has_title("Fiche Suiveuse Montage"):
            self.get_text(1, 1, 3, 3)
            self.handle_one_field("N° Désignation Agile", "Rév", 0, self.app.product_input)
            self.handle_SN_field("N° de série", " ", 1)
            self.get_text(3, 1, 3, 3)
            self.handle_one_field("N° OF", " ", 1, self.app.designation_input)
        elif self.has_title("ACCEPTANCE TEST REPORT"):
            self.handle_one_field("Equipment revision", "\n", 0, self.app.product_input)
            self.handle_reference_field("Equipment reference", "\n", 0)
            self.handle_one_field("Equipment denomination", "\n", 0, self.app.designation_input)
            self.get_text(1, 2, 2, 4)
            self.handle_SN_field("S/N", "\n", 0, "Presentation")
        elif self.has_title("Intégration"):
            self.get_text(1, 1, 4, 3)
            self.handle_one_field("N° nomenclature", "\n", 1, self.app.product_input)
            self.handle_SN_field("N° de série", "\n", 1)
            self.get_text(3, 1, 3, 3)
            self.handle_one_field("N° de l'OF", "\n", 1, self.app.designation_input)
        else:
            if self.app.page < self.app.file_page_nb - 1 and self.app.auto_cycling:
                self.app.page += 1
                self.prepare_image()
                self.get_text()
                self.get_name_of_file()
                return
        self.app.text_update()

    def _clean_string(self, string):
        for remove in REMOVE_AT_THE_END:
            string = string.replace(remove, "")
        string = string.replace("l", "I").upper()
        for old, new in REPLACE_AT_THE_END:
            string = string.replace(old, new)
        return string

    def _get_last_index_for_string(self, *keys):
        for key in keys:
            j = get_sequence(self._text, key, 1)
            if j == -1:
                j = get_sequence(self._text, key, 0.95)
            if j != -1:
                return j + len(key)
        return -1
