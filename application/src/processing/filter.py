import time
import os
import threading
import fitz

from PIL import Image
import pygame as pg
import win32con
import win32gui
import difflib
import numpy as np
import pytesseract

from constants.path import *
from constants.window import DPI
from processing.image_processing import remove_lines
from processing.analyser import *

class Text:
    def __init__(self, pages):
        self.__content = [["", "", "", "", "", "", ""] for _ in range(pages)]
        self.__analysed = [False for _ in range(pages)]

    def is_analysed(self, page):
        return self.__analysed[page]

    def set_analysed(self, page, value=True):
        self.__analysed[page] = value

    def get_content(self, page):
        return self.__content[page]
    
    def get_text(self, page):
        return self.__content[page][0]
    
    def get_product(self, page):
        return self.__content[page][1]
    
    def get_SN(self, page):
        return self.__content[page][2]

    def get_designation(self, page):
        return self.__content[page][3]

    def set_text(self, page, text):
        self.__content[page][0] = text
    
    def set_product(self, page, text):
        self.__content[page][1] = text
    
    def set_SN(self, page, text):
        self.__content[page][2] = text

    def set_designation(self, page, text):
        self.__content[page][3] = text
    
    def get_default_product(self, page):
        return self.__content[page][4]
    
    def get_default_SN(self, page):
        return self.__content[page][5]
    
    def get_default_designation(self, page):
        return self.__content[page][6]

    def set_default_product(self, page, text):
        self.__content[page][4] = text

    def set_default_SN(self, page, text):
        self.__content[page][5] = text

    def set_default_designation(self, page, text):
        self.__content[page][6] = text

class Filter:

    def __init__(self, file, page_nb, app):
        
        self.__file = file
        self.__page = 0
        self.__page_nb = page_nb
        self.__auto_cycling = True
        self.__app = app
        
        self.__images = [None for _ in range(page_nb)]
        self.__filtered_images = [None for _ in range(page_nb)]
        self.__size = [None for _ in range(page_nb)]
        self.__text = Text(page_nb)
        
        self.doc = fitz.open(self.__file)
        
    def filter(self, page_nb=None):
        if page_nb == self.__page:
            return
        if page_nb != None:
            self.__page = page_nb
        if self.__text.is_analysed(self.__page):
            return
        if self.__images[self.__page] == None:
            self.__prepare_image()
        self.__update_raw_text()
        self.__analyse_page()

    def get_image(self, page_nb):
        if self.__images[page_nb] is None:
            self.__page = page_nb
            self.__prepare_image()
        return self.__images[page_nb]
    
    def get_filtered_image(self, page_nb):
        if self.__images[self.__page] is None:
            self.__page = page_nb
            self.__prepare_image()
        if self.__filtered_images[page_nb] is None:
            width, height = self.__size[self.__page][0], self.__size[self.__page][1]
            self.__filtered_images[self.__page] = remove_lines(self.__images[self.__page].crop((0, 0, width, height//2)))
        return self.__filtered_images[page_nb]

    def get_text(self, page_nb):
        content = self.__text.get_content(page_nb)[1:]
        if not self.__text.is_analysed(page_nb):
            return None
        if content != ["" for _ in range(6)]:
            return content
        if self.__page != page_nb:
            self.__page = page_nb
            self.filter()
        return content

    def __prepare_image(self):
        try:
            page = self.doc.load_page(self.__page)
        except ValueError:
            try:
                self.doc = fitz.open(self.__file)
                page = self.doc.load_page(self.__page)
            except fitz.FileNotFoundError:
                print("Not found", self.__file)
                del self
                return
        mat = fitz.Matrix(DPI / 72, DPI / 72)
        pix = page.get_pixmap(matrix=mat)
        self.__size[self.__page] = [pix.width, pix.height]
        self.__images[self.__page] = Image.frombytes("RGB", self.__size[self.__page], pix.samples)

    def __update_raw_text(self):
        width, height = self.__size[self.__page][0], self.__size[self.__page][1]
        if self.__filtered_images[self.__page] == None:
            self.__filtered_images[self.__page] = remove_lines(self.__images[self.__page].crop((0, 0, width, height//2)))
        text = pytesseract.image_to_string(self.__filtered_images[self.__page], lang="fra+eng")
        self.__text.set_text(self.__page, text)

    def __get_cropped_raw_text(self, x, y, w, h):
        width, height = self.__size[self.__page][0], self.__size[self.__page][1]
        img = self.__filtered_images[self.__page].crop((x*width, y*height*2, w*width, h*height*2))
        return pytesseract.image_to_string(img, lang="fra+eng")

    def __handle_field(self, name, splitter, splitter_delta, *splitters, original_text=None):
        if original_text is None:
            original_text = self.__text.get_text(self.__page)
        i = get_last_index_for_string(original_text, name)
        if i == -1:
            return ""
        else:
            before_text = original_text[i:].split(splitter)[splitter_delta]
            for splitter in list(splitters) + ["+", ">", "<"]:
                before_text = before_text.split(splitter)[0]
            text = clean_string(before_text)
            return text

    def __handle_product_field(self, name, splitter, splitter_delta, *splitters, original_text=None):
        self.__text.set_default_product(self.__page, name)
        text = self.__handle_field(name, splitter, splitter_delta, *splitters, original_text=original_text).replace("À", "A")
        self.__text.set_product(self.__page, text)

    def __handle_revision_field(self, name, splitter, splitter_delta, *splitters, original_text=None):
        text = self.__handle_field(name, splitter, splitter_delta, *splitters, original_text=original_text)
        text = ''.join(filter(lambda c: c.isdigit(), text))
        text = text[min(0,len(text)-2):]
        if len(text) == 0:
            return
        if len(text) == 1:
            text = "0" + text
        self.__text.set_product(self.__page, self.__text.get_product(self.__page) + "-" + text)

    def __handle_SN_field(self, name, splitter, splitter_delta, *splitters, original_text=None):
        self.__text.set_default_SN(self.__page, name)
        text = self.__handle_field(name, splitter, splitter_delta, *splitters, original_text=original_text)
        for splitter in ["SN", "S/N"]:
            spl = text.split(splitter)
            if len(spl) > 1:
                text = ''.join(spl[1:])
        for (old, new) in [("A", "À")]:
            text = text.replace(old, new)
        text = ''.join(filter(lambda c: c.isdigit() or c == "À", text))
        if "À" in text:
            if text[0] == "À":
                self.__text.set_SN(self.__page, text[1:min(len(text), 9)])
            elif text[-1] == "À":
                self.__text.set_SN(self.__page, text[:-1])
            else:
                self.__text.set_SN(self.__page, text[:min(len(text), 9)])
        else:
            self.__text.set_SN(self.__page, text[:min(len(text), 4)])

    def __handle_designation_field(self, name, splitter, splitter_delta, *splitters, original_text=None):
        self.__text.set_default_designation(self.__page, name)
        text = self.__handle_field(name, splitter, splitter_delta, *splitters, original_text=original_text)
        self.__text.set_designation(self.__page, text)

    def __has_title(self, *keys):
        return has_keys(self.__text.get_text(self.__page), *keys)

    def get_current_page(self):
        return self.__page

    def __analyse_page(self):
        if self.__has_title("SEQUENCES POUR UN OF", "Poste de\ncharge", "Temps\n prépa\n(h)"):
            self.__handle_product_field("Produit", "\n", 0)
            self.__handle_SN_field("Texte 2", "\n", 0)
            self.__handle_designation_field("Désignation", "\n", 0)
        elif self.__has_title("Check-list"):
            self.__handle_product_field("Code article", "\n", 0, "Nom", "Date", "Cde")
            self.__handle_SN_field("S/N", "\n", 0, "Nom", "Date", "Cde")
            self.__handle_designation_field("Désignation", "\n", 0, "Nom", "Date", "Cde")
        elif self.__has_title("Fiche Suiveuse Montage"):
            self.__handle_product_field("N° Désignation Agile", "Rév", 0)
            self.__handle_SN_field("N° de série", " ", 1)
            text = self.__get_cropped_raw_text(2/3, 0, 1, 1/3)
            self.__handle_designation_field("N° OF", " ", 1, original_text=text)
        elif self.__has_title("DUAL CARTRIDGE READER"):
            self.__handle_product_field("Equipment reference", "\n", 0)
            self.__handle_designation_field("Equipment denomination", "\n", 0)
            self.__handle_revision_field("Is. Rev", "\n", 0)
            text = self.__get_cropped_raw_text(0, 1/4, 1/2, 1/2)
            self.__handle_SN_field("S/N", "\n", 0, "Present", original_text=text)
        elif self.__has_title("ACCEPTANCE TEST REPORT", "Cahier de Résultats d'Essais"):
            self.__handle_product_field("Equipment reference", "\n", 0)
            self.__handle_revision_field("Equipment revision", "\n", 0)
            self.__handle_designation_field("Equipment denomination", "\n", 0)
            text = self.__get_cropped_raw_text(0, 1/4, 1/2, 1/2)
            self.__handle_SN_field("S/N", "\n", 0, "Present", original_text=text)
            if self.__text.get_content(self.__page)[1:4] == ["" for _ in range(3)]:
                self.__handle_product_field("Référence de l'équipement", "\n", 0)
                self.__handle_revision_field("Présentation", "\n", 0, "Date")
                self.__handle_designation_field("Nom de l'équipement", "\n", 0)
                text = self.__get_cropped_raw_text(0, 1/4, 1/2, 1/2)
                self.__handle_SN_field("S/N", "\n", 0, "Présentation", original_text=text)
        elif self.__has_title("Intégration"):
            text = self.__get_cropped_raw_text(0, 0, 1/4, 1/3)
            self.__handle_product_field("N° nomenclature", "\n", 1, original_text=text)
            if self.__text.get_product(self.__page) == "":
                self.__handle_product_field("DID Produit", "\n", 1, original_text=text)
            self.__handle_SN_field("N° de série", "\n", 1, original_text=text)
            text = self.__get_cropped_raw_text(2/3, 0, 1, 1/3)
            self.__handle_designation_field("N° de l'OF", "\n", 1, original_text=text)
        elif self.__has_title("Montage CHAISE FIXE"):
            text = self.__get_cropped_raw_text(0, 0, 0.4, 0.2)
            self.__handle_product_field("N° nomenclature", "\n", 1, original_text=text)
            self.__handle_SN_field("N° série", "\n", 1, original_text=text)
            text = self.__get_cropped_raw_text(2/3, 0, 1, 1/3)
            self.__handle_designation_field("N° de l'OF", "\n", 1, original_text=text)
        elif self.__has_title("FICHE D'ACCOMPAGNEMENT"):
            text = self.__get_cropped_raw_text(0, 0, 0.5, 0.2)
            self.__handle_product_field("Code ARTICLE", "\n", 0, "Indice", "Imdice", original_text=text)
            self.__handle_SN_field("N° de SERIE", "\n", 0, "Assemblage", "DFC", original_text=text)
            self.__handle_revision_field("Indice", "\n", 0, original_text=text)
            self.__handle_designation_field("DESIGNATION", "\n", 0, "Circuit", "à l'électricité",original_text=text)
        else:
            if self.__page < self.__page_nb - 1 and self.__auto_cycling:
                self.__page += 1
                self.__app.get_layer().page_update(self.__page, self)
                self.filter()
            return
        
        """
        if self.__text.get_content(self.__page)[1:4] == ["" for _ in range(3)]:
            if self.__page < self.__page_nb - 1 and self.__auto_cycling:
                self.__page += 1
                self.__app.get_layer().page_update(self.__page, self)
                self.filter()
            return
        """
        
        self.__text.set_analysed(self.__page)
        self.__auto_cycling = False
        self.__app.get_layer().text_update(True)
