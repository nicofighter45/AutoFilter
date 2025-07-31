import subprocess
import time
import os

import PyPDF2
import keyboard

from folders import *
from timing import *


class Word:

    def __init__(self, filename):
        self._filename = filename
        self._cropped_file = os.path.join(
            CROPPED_FOLDER, self._filename + "cropped.pdf"
        )
        self._converted_file = os.path.join(CONVERTED_FOLDER, self._filename)

        self.__crop_to_first_page()
        self.__convert_with_word()
        os.remove(self._cropped_file)
        return self._converted_file

    def __crop_to_first_page(self):
        reader = PyPDF2.PdfReader(self._filename)
        writer = PyPDF2.PdfWriter()
        writer.add_page(reader.pages[0])
        with open(self._cropped_file, "wb") as f:
            writer.write(f)

    def __convert_with_word(self):
        subprocess.run(["start", "winword", self._cropped_file], shell=True)
        time.sleep(WAIT_FOR_WORD_OPENING)
        press_and_wait("alt;f;i;u;ctrl+l;ctrl+a")
        keyboard.write(CONVERTED_FOLDER)
        press_and_wait("enter;tab;tab;tab;tab;tab")
        keyboard.write(self._converted_file)
        press_and_wait("enter;alt+f4;tab;enter")


def press_and_wait(string, t=0.1):
    for char in string.split(";"):
        keyboard.press_and_release(char)
        time.sleep(t)
