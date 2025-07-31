import subprocess
import time
import os

import PyPDF2
import keyboard
import random
import pyautogui

scan_folder = R"C:\Users\UP60071088\Documents\Scan"

local_folder = "C:\\Users\\UP60071088\\Documents\\AutoFilter\\"
filtered_folder = os.path.join(local_folder, "filtered")
unreadable_folder = os.path.join(local_folder, "unreadable")
converted_folder = os.path.join(local_folder, "converted")


def press_and_wait(string, t=0.1):
    for char in string.split(';'):
        keyboard.press_and_release(char)
        time.sleep(t)


def crop_to_first_page(file, crop_file):
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()
    writer.add_page(reader.pages[0])
    with open(crop_file, "wb") as f:
        writer.write(f)


def convert_with_word(filename, crop_file):
    subprocess.run(["start", "winword", crop_file], shell=True)
    time.sleep(10)
    press_and_wait('alt;f;i;u;ctrl+l;ctrl+a')
    keyboard.write(converted_folder)
    press_and_wait('enter;tab;tab;tab;tab;tab')
    keyboard.write(filename)
    press_and_wait('enter;alt+f4;tab;enter')
    time.sleep(2)


def get_file_content(input_file, filename):
    crop_file = os.path.join(local_folder, filename + "cropped.pdf")
    crop_to_first_page(input_file, crop_file)
    convert_with_word(filename, crop_file)
    converted_file = os.path.join(converted_folder, filename)
    while not os.path.exists(converted_file):
        time.sleep(10)
    with open(converted_file, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
    return text_content


def get_content_from_text(text, filename, input_file):
    by_hand = []
    try:
        produit = text.split("Produit")[1][:20].split("\n")[0]
    except (Exception, IndexError) as e:
        by_hand.append("Produit")
    try:
        SN = text.split("SN")[1][:20].split("\n")[0]
    except (Exception, IndexError) as e:
        by_hand.append("SN")
    try:
        nom = text.split("Nom")[1][:20].split("\n")[0]
    except (Exception, IndexError) as e:
        by_hand.append("Nom")
    if by_hand:
        unreadable_file = os.path.join(unreadable_folder, filename)
        os.replace(input_file, unreadable_file)
        return
        subprocess.run(["start", "acrord32", unreadable_file], shell=True)
        print("La lecture automatique a échoué. Veuillez saisir cette valeur à la main")
        for item in by_hand:
            if item == "Produit":
                produit = input("Produit :\n")
            elif item == "SN":
                SN = input("SN :\n")
            elif item == "Nom":
                nom = input("Nom :\n")
    name = f"{produit}-{SN}'-{nom}.pdf".replace(":", "").replace(" ", "").replace("'", "").replace("`", "")
    os.replace(input_file, os.path.join(filtered_folder, name))


for filename in os.listdir(scan_folder):
    input_file = os.path.join(scan_folder, filename)
    text_content = get_file_content(input_file, filename)
    os.remove(input_file)
    
    continue
    name = get_content_from_text(text_content, filename, input_file)
    os.remove(converted_file)
    
