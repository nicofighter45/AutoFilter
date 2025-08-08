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
from analyser import *

class Filter:

    def __init__(self, file, layer, page_nb, should_show):
        self.__file = file
        self.__layer = layer
        self.__images = [None for _ in range(page_nb)]
        self.__should_show = should_show
        self.__texts = [[] for _ in range(page_nb)] # store this properly in an object
        self.__page = 0
        
        
        self.prepare_image()
        self.__text = self.get_text(show=True)
        self.__auto_cycling = True


    def prepare_image(self):
        self.doc = fitz.open(self._file)
        page = self.doc.load_page(self.app.page)
        dpi = 300
        # fitz default is 72 dpi, so scale factor is dpi / 72
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        self.pix = page.get_pixmap(matrix=mat)
        self.pre_img = Image.frombytes("RGB", [self.pix.width, self.pix.height], self.pix.samples)
        self.__layout.set_right_image(self.pre_img)
    
    def get_text(self, column=1, row=1, width_crop=1, height_crop=3, show=False, should_text=True, adder_width=1, adder_height=1):
        column -= 1
        row -= 1
        width, height = self.pix.width//width_crop, self.pix.height//height_crop
        box = (column*width, row*height, (column+adder_width)*width, (row+adder_height)*height)
        img = Image.fromarray(remove_lines(self.pre_img.crop(box)))
        if show:
            self.app.set_left_image(img)
        text = pytesseract.image_to_string(img, lang="fra+eng")
        if should_text:
            self._text = text
        print("\n\n\n", column, row, width_crop, height_crop, "\n", text, "\n\n\n")
        return text

    def __del__(self):
        if hasattr(self, "doc"):
            self.doc.close()
    
    def handle_SN_field(self, name, splitter, splitter_delta, *splitters):
        i = get_last_index_for_string(self.__text, name)
        self.__layout.SN_input.default_text = name
        if i == -1:
            self.__layout.SN_input.set_text("")
        else:
            before_text = self.__text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters):
                before_text = before_text.split(splitter)[0]
            for splitter in ["SN", "S/N"]:
                spl = before_text.split(splitter)
                if len(spl) > 1:
                    before_text = ''.join(spl[1:])
            text = clean_string(before_text)
            for (old, new) in [("A", "À")]:
                text = text.replace(old, new)
            text = ''.join(filter(lambda c: c.isdigit() or c == "À", text))
            if "À" in text:
                if text[0] == "À":
                    self.__layout.SN_input.set_text(text[1:min(len(text), 9)])
                elif text[-1] == "À":
                    self.__layout.SN_input.set_text(text[:-1])
                else:
                    self.__layout.SN_input.set_text(text[:min(len(text), 9)])
            else:
                self.__layout.SN_input.set_text(text[:min(len(text), 4)])
    
    def handle_revision_field(self, name, splitter, splitter_delta, *splitters):
        i =  get_last_index_for_string(self.__text, name)
        if i != -1:
            before_text = self.__text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters) + ["+"]:
                before_text = before_text.split(splitter)[0]
            text = self._clean_string(before_text)
            text = ''.join(filter(lambda c: c.isdigit(), text))
            text = text[min(0,len(text)-2):]
            self.app.product_input.set_text(self.app.product_input.text + "-" + text)

    def handle_one_field(self, name, splitter, splitter_delta, input_field, *splitters):
        i = get_last_index_for_string(self.__text, name)
        input_field.default_text = name
        if i == -1:
            input_field.set_text("")
        else:
            before_text = self._text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters) + ["+", ">", "<"]:
                before_text = before_text.split(splitter)[0]
            text = clean_string(before_text)
            input_field.set_text(text)
    
    def has_title(self, *keys):
        return has_title(self.__text, keys)


    def get_name_of_file(self):
        if self.has_title("SEQUENCES POUR UN OF", "Poste de\ncharge", "Temps\n prépa\n(h)"):
            self.handle_one_field("Produit", "\n", 0, self.__layer.product_input)
            self.handle_SN_field("Texte 2", "\n", 0)
            self.handle_one_field("Désignation", "\n", 0, self.__layer.designation_input)
        elif self.has_title("Check-list"):
            self.handle_one_field("Code article", "\n", 0, self.__layer.product_input, "Nom", "Date", "Cde")
            self.handle_SN_field("S/N", "\n", 0, "Nom", "Date", "Cde")
            self.handle_one_field("Désignation", "\n", 0, self.__layer.designation_input, "Nom", "Date", "Cde")
        elif self.has_title("Fiche Suiveuse Montage"):
            self.get_text(1, 1, 3, 3)
            self.handle_one_field("N° Désignation Agile", "Rév", 0, self.__layer.product_input)
            self.handle_SN_field("N° de série", " ", 1)
            self.get_text(3, 1, 3, 3)
            self.handle_one_field("N° OF", " ", 1, self.__layer.designation_input)
        elif self.has_title("DUAL CARTRIDGE READER"):
            self.get_text(1, 1, 1, 2, show=True)
            self.handle_one_field("Equipment reference", "\n", 0, self.__layer.product_input)
            self.handle_one_field("Equipment denomination", "\n", 0, self.__layer.designation_input)
            self.handle_revision_field("Is. Rev", "\n", 0)
            self.get_text(1, 2, 2, 4)
            self.handle_SN_field("S/N", "\n", 0, "Present")
        elif self.has_title("ACCEPTANCE TEST REPORT", "Cahier de Résultats d'Essais"):
            self.get_text(1, 1, 1, 2, show=True, should_text=False)
            self.handle_one_field("Equipment reference", "\n", 0, self.__layer.product_input)
            self.handle_revision_field("Equipment revision", "\n", 0)
            self.handle_one_field("Equipment denomination", "\n", 0, self.__layer.designation_input)
            self.get_text(1, 2, 2, 4)
            self.handle_SN_field("S/N", "\n", 0, "Present")
        elif self.has_title("Intégration"):
            self.get_text(1, 1, 4, 3)
            self.handle_one_field("N° nomenclature", "\n", 1, self.__layer.product_input)
            if self.__layer.product_input.not_found:
                self.handle_one_field("DID Produit", "\n", 1, self.__layer.product_input)
            self.handle_SN_field("N° de série", "\n", 1)
            self.get_text(3, 1, 3, 3)
            self.handle_one_field("N° de l'OF", "\n", 1, self.__layer.designation_input)
        elif self.has_title("Montage CHAISE FIXE"):
            self.get_text(1, 1, 3, 3)
            self.handle_one_field("N° nomenclature", "\n", 1, self.__layer.product_input)
            self.handle_SN_field("N° série", "\n", 1)
            self.get_text(3, 1, 3, 3)
            self.handle_one_field("N° de l'OF", "\n", 1, self.__layer.designation_input)
        elif self.has_title("FICHE DE REPRISE Standart"):
            pass
        else:
            if self.__layer.page < self.__layer.file_page_nb - 1 and self.__layer.auto_cycling:
                self.__layer.page += 1
                self.prepare_image()
                self.get_text(show=True)
                self.get_name_of_file()
                return
        self.__layer.text_update()


