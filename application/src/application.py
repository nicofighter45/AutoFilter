import threading
import os

import win32con
import win32gui
import pygame as pg
import pytesseract

from filter import Filter
from layer import Layer
from file_manager import FileManager
from constants.path import *
from constants.window import FPS


def maximize_window():
    window_handle = win32gui.FindWindow(None, "AutoFilter")
    if window_handle:
        window_placement = win32gui.GetWindowPlacement(window_handle)
        if window_placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
        win32gui.ShowWindow(window_handle, win32con.SW_MAXIMIZE)


class App:
    def __init__(self):
               
        pg.init()
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
        os.environ["TESSDATA_PREFIX"] = TESSERACT_LANG_FOLDER
        
        self.__layer = Layer(self)
        self.__file_manager = FileManager()
        self.__running = True

        maximize_window()
        
    def __handle_keyboard(self, event):
        match event.key:
            case pg.K_ESCAPE:
                if not self.__layer.is_focused():
                    self.__running = False
                self.__layer.unfocus()
            case (pg.K_RETURN, pg.K_KP_ENTER):
                self.launch_filter(self.get_file_manager().save(self.__layer.name_input.get_text()))
            case (pg.K_LEFT, pg.K_RIGHT):
                self.__layer.arrow_key(event.key)
            case _:
                self.__layer.letter_field_event(event.key)

    def __handle_event(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                self.__running = False
            elif event.type == pg.KEYDOWN:
                self.__handle_keyboard(event)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.__layer.handle_mouse(event.pos)

    def run(self):
        clock = pg.time.Clock()

        while self.__running:
            self.__handle_event()
            self.__layer.update()
            pg.display.update()
            clock.tick(FPS)
        
        pg.quit()
        exit()

    def get_file_manager(self):
        return self.__file_manager

    def get_layer(self):
        return self.__layer


if __name__ == "__main__":
    App().run()
