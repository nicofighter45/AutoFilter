import fitz
from PIL import Image, ImageDraw
from constants.folders import *
import pygame as pg
import os
import threading
import win32con
import win32gui
import difflib

REMOVE_AT_THE_END = [":", " ", "`", "'", "\\v", "—", "•", "."]


def get_sequence(text, pattern, cutoff=0.7):
    pattern_length = len(pattern)
    for i in range(len(text) - pattern_length + 1):
        substring = text[i : i + pattern_length]
        similarity = difflib.SequenceMatcher(None, substring, pattern).ratio()
        #print(similarity, pattern, substring)
        if similarity >= cutoff:
            return i
    return -1


def has_sequence(text, pattern, cutoff=0.7):
    return get_sequence(text, pattern, cutoff) != -1


class Filter:

    def __init__(self, filename, app):
        self._converted_file = os.path.join(CONVERTED_FOLDER, filename)
        self._original_file = os.path.join(ORIGINAL_FOLDER, filename)
        self._doc = fitz.open(self._converted_file)
        self._text = self._doc[0].get_text()
        self._name = ""
        self.app = app

        original_doc = fitz.open(self._original_file)
        pix = original_doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.app.set_right_image(img)
        original_doc.close()

        page = self._doc[0]
        pix = page.get_pixmap()
        self.img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    def __del__(self):
        if hasattr(self, "_doc"):
            self._doc.close()

    def show_converted_file(self):
        pix = self._doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.app.set_left_image(img)
    
    def handle_one_field(self, name, splitter, splitter_delta, input_field, *replacements):
        i = self._get_last_index_for_string(name)
        if i == -1:
            input_field.not_found = True
        else:
            before_text = self._text[i:].split(splitter)[splitter_delta]
            
            text = self._clean_string(before_text)
            for replacement in replacements:
                text = text.replace(replacement, "")
            input_field.set_text(text)
    
    def has_title(self, *keys):
        for key in keys:
            if has_sequence(self._text, key):
                return True
        return False

    def get_name_of_file(self):
        if self.has_title("SEQUENCES POUR UN OF", "Poste de\ncharge", "Temps\n prépa\n(h)", "N° Op"):
            self.handle_one_field("Produit", "\n", 0, self.app.product_input)
            self.handle_one_field("Texte 2", "\n", 0, self.app.SN_input, "SN", "S/N")
            self.handle_one_field("Désignation", "\n", 0, self.app.designation_input)
        elif self.has_title("Check-list"):
            self.handle_one_field("Code article", "\n", 0, self.app.product_input)
            self.handle_one_field("S/N", "\n", 0, self.app.SN_input)
            self.handle_one_field("Désignation", "\n", 0, self.app.designation_input)
        elif self.has_title("Fiche Suiveuse Montage"):
            self.handle_one_field("N° Désignation Agile", "\n", 1, self.app.product_input)
            self.handle_one_field("N° de série", "\n", 1, self.app.SN_input)
            self.handle_one_field("N° OF", "\n", 1, self.app.designation_input)
        elif self.has_title("ACCEPTANCE TEST REPORT"):
            self.handle_one_field("Equipment reference", "\n", 0, self.app.product_input)
            self.handle_one_field("S/N", "\n", 0, self.app.SN_input)
            self.handle_one_field("Equipment denomination", "\n", 0, self.app.designation_input)
        elif self.has_title("Cahier de Résultats d'Essais"):
            self.handle_one_field("N° Désignation Agile", "\n", 1, self.app.product_input)
            # todo
        else:
            for input_field in self.app.inputs:
                input_field.not_found = True
            print("No key")
        self.app.text_update()
        self.show_converted_file()

    def _clean_string(self, string):
        for remove in REMOVE_AT_THE_END:
            string = string.replace(remove, "")
        return string.replace("l", "I").upper().replace("OO", "00")

    def _get_last_index_for_string(self, *keys):
        for key in keys:
            j = get_sequence(self._text, key, 0.95)
            if j != -1:
                return j + len(key)
        return -1

    def _get_from_rectangle(self, i, keys):
        text = self._doc[0].get_textbox(fitz.Rect(keys))

        rect = fitz.Rect(*keys)
        draw = ImageDraw.Draw(self.img)
        x0, y0, x1, y1 = rect
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
        self.set_text(text, i)

    def set_text(self, text, i):
        self.app.set_left_image(self.img)

        for remove in REMOVE_AT_THE_END:
            text = text.replace(remove, "")
        self.app.inputs[i + 1].set_text(text)
