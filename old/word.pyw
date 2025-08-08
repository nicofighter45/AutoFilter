import subprocess
import time
import os
import threading

import PyPDF2
import keyboard
import fitz
import tkinter as tk
import pyautogui

from constants.folders import *
from constants.window import *


class Word:

    def __init__(self, filename):
        self._filename = filename
        self._cropped_file = os.path.join(
            CROPPED_FOLDER, self._filename
        )

        self.__crop_to_page()
        if not self.__convert_with_word(0):
            return
        original_file = os.path.join(SCAN_FOLDER, self._filename)
        destination_file = os.path.join(ORIGINAL_FOLDER, self._filename)
        os.rename(original_file, destination_file)

    def __crop_to_page(self, page_number=0):
        reader = PyPDF2.PdfReader(os.path.join(SCAN_FOLDER, self._filename))
        writer = PyPDF2.PdfWriter()
        writer.add_page(reader.pages[page_number])
        with open(self._cropped_file, "wb") as f:
            writer.write(f)

    def __convert_with_word(self, i):
        subprocess.run(["start", "winword", self._cropped_file], shell=True)
        converted_file = os.path.join(CONVERTED_FOLDER, self._filename)
        if os.path.exists(converted_file):
            try:
                os.remove(converted_file)
            except Exception as e:
                return False
        time.sleep(0.5)
        pyautogui.click(WIDTH // 2, HEIGHT // 2)
        while pyautogui.screenshot().getpixel((0, 0)) != (42, 87, 154):
            time.sleep(0.5)
        pyautogui.click(WIDTH // 2, 0)
        press_and_wait("alt;f;i;u;ctrl+l;ctrl+a")
        keyboard.write(CONVERTED_FOLDER)
        press_and_wait("enter")
        pyautogui.click(825, 443)
        keyboard.write(self._filename)
        keyboard.press_and_release("enter")
        while not os.path.exists(converted_file):
            time.sleep(0.5)
        press_and_wait("alt+f4;tab;enter")
        if os.path.exists(self._cropped_file):
            try:
                os.remove(self._cropped_file)
            except Exception as e:
                return False
        doc = fitz.open(converted_file)
        if len(doc[0].get_text().replace(" ", "").replace("\n", "")) < 30:
            i += 1
            if i == 3:
                return False
            self.__crop_to_page(i)
            return self.__convert_with_word(i)
        return True


current_filename = "None"

def run_tkinter():
    global filename
    root = tk.Tk()
    root.title("Automatic Word Converter")
    root.attributes("-topmost", True)  # Make the window stay on top of other applications
    root.overrideredirect(True)
    root.geometry("1000x100")  # Set the initial size of the window
    root.configure(bg="black")
    label = tk.Label(root, text="Converting file: None", fg="white", bg="black", font=("Calibri", 40), anchor="w")
    label.pack(padx=10, pady=0)
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    root.geometry('+%d+%d' % (ws - 1000, hs - 140))
    
    def update_status():
        label.config(text="Converting file: " + current_filename)
        root.after(1000, update_status)

    update_status()
    root.mainloop()


def press_and_wait(string, t=0.1):
    for char in string.split(";"):
        keyboard.press_and_release(char)
        time.sleep(t)


if __name__ == "__main__":
    def esc_listener():
        while True:
            if keyboard.is_pressed("esc"):
                print("Escape pressed. Exiting program.")
                os._exit(0)


    listener_thread = threading.Thread(target=esc_listener, daemon=True)
    listener_thread.start()
    
    thread = threading.Thread(target=run_tkinter)
    thread.start()
    pyautogui.click(WIDTH-5, HEIGHT-5)
    for filename in os.listdir(CROPPED_FOLDER):
        file_path = os.path.join(CROPPED_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    for filename in os.listdir(SCAN_FOLDER):
        if filename.lower().endswith(".pdf"):
            current_filename = filename
            Word(filename)
    for filename in os.listdir(CROPPED_FOLDER):
        file_path = os.path.join(CROPPED_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
