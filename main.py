import subprocess
import time
import os

import PyPDF2
import keyboard
import random
import pyautogui

from word import Word
from folders import *
from timing import *
from filter import Filter
import threading
import sys


def get_file_content(file):
    with open(file, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
    return text_content


"""
subprocess.run(["start", "acrord32", UNREADABLE_FOLDER], shell=True)
        print("La lecture automatique a échoué. Veuillez saisir cette valeur à la main")
        for item in by_hand:
            if item == "Produit":
                produit = input("Produit :\n")
            elif item == "SN":
                SN = input("SN :\n")
            elif item == "Nom":
                nom = input("Nom :\n")
"""


def get_content_from_text(text, filename, input_file):
    filter = Filter(text)
    name = filter.get_name_of_file(input_file)
    if name == "":
        unreadable_file = os.path.join(UNREADABLE_FOLDER, filename)
        # os.replace(input_file, unreadable_file)
        return
    os.replace(input_file, os.path.join(FILTERED_FOLDER, name))


"""
for filename in os.listdir(CONVERTED_FOLDER):
    file = os.path.join(CONVERTED_FOLDER, filename)
    text_content = get_file_content(file)
    name = get_content_from_text(text_content, filename, file)
"""
    
    
"""
file = os.path.join(CONVERTED_FOLDER, "test.pdf")
text_content = get_file_content(file)
name = get_content_from_text(text_content, "test.pdf", file)
"""


def esc_listener():
    while True:
        if keyboard.is_pressed('esc'):
            print("Escape pressed. Exiting program.")
            os._exit(0)

listener_thread = threading.Thread(target=esc_listener, daemon=True)
listener_thread.start()

for filename in os.listdir(SCAN_FOLDER):
    file = os.path.join(SCAN_FOLDER, filename)
    Word(filename)
    os.replace(file, os.path.join(CONVERTED_FOLDER, filename))


