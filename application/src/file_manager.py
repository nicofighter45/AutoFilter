import os
import threading
import time
from PyPDF2 import PdfReader

from constants.path import SCAN_FOLDER, FILTERED_FOLDER, UNREADABLE_FOLDER
from processing.filter import Filter
from constants.window import THREAD_FORWARDING

class FileManager:
    def __init__(self, app):
        self.__index = -THREAD_FORWARDING-1
        self.__files = [f for f in os.listdir(SCAN_FOLDER) if os.path.isfile(os.path.join(SCAN_FOLDER, f))]
        self.__renamed_files = [None for _ in self.__files]
        self.__filters = [None for _ in self.__files]
        self.__pages = [0 for _ in self.__files]
        self.__app = app
        
        for _ in range(THREAD_FORWARDING):
            self.__next_file()


    def get_main_filter(self):
        return self.__filters[self.__index]


    def save(self, name):
        if self.__index <= -1 or name == "" or name == "--":
            self.__next_file()
            return
        if self.__filters[self.__index] is not None:
            self.__filters[self.__index].doc.close()
            self.__filters[self.__index] = None
        filename = self.__files[self.__index]
        original_path = os.path.join(SCAN_FOLDER, filename)
        filtered_path = os.path.join(FILTERED_FOLDER, name + ".pdf")
        try:
            os.rename(original_path, filtered_path)
            self.__renamed_files[self.__index] = filtered_path
        except FileExistsError:
            self.save(name + " (1)")
            return
        except OSError:
            self.delete()
        self.__next_file()

    def delete(self):
        if self.__index <= -1:
            return self.__next_file()
        if self.__filters[self.__index] is not None:
            self.__filters[self.__index].doc.close()
            self.__filters[self.__index] = None
        filename = self.__files[self.__index]
        original_path = os.path.join(SCAN_FOLDER, filename)
        unreadable_path = os.path.join(UNREADABLE_FOLDER, filename)
        os.rename(original_path, unreadable_path)
        self.__renamed_files[self.__index] = unreadable_path
        self.__next_file()

    def __next_file(self):
        if self.__index >= len(self.__files)-1:
            return
        self.__index += 1
        if self.__index+THREAD_FORWARDING >= len(self.__files):
            return
        path = os.path.join(SCAN_FOLDER, self.__files[self.__index+THREAD_FORWARDING])
        with open(path, "rb") as f:
            self.__pages[self.__index+THREAD_FORWARDING] = len(PdfReader(f).pages)
        self.launch_filter(self.__index + THREAD_FORWARDING)
        
    def launch_filter(self, index=None):
        if index is None:
            index = self.__index
        if not 0 <= index < len(self.__files):
            return
        file = self.__files[index]
        if self.__filters[index] is not None:
            return
        print("LAUNCHING THREAD", index, self.__files[index])
        text_filter = Filter(os.path.join(SCAN_FOLDER, file), self.get_pages_number(index), self.__app)
        threading.Thread(target=text_filter.filter, daemon=True).start()
        self.__filters[index] = text_filter

    def get_filter(self):
        return self.__filters[self.__index]

    def get_current_file_number(self):
        return self.__index

    def get_pages_number(self, index=None):
        if index is None:
            return self.__pages[self.__index]
        if self.__pages[index] != 0:
            return self.__pages[index]
        if 0 <= index < len(self.__renamed_files):
            with open(os.path.join(SCAN_FOLDER, self.__files[index]), "rb") as f:
                self.__pages[index] = len(PdfReader(f).pages)
                return self.__pages[index]
        return 0

    def get_files_number(self):
        return len(self.__files)
    
    def return_to_previous(self):
        if self.__index == 0:
            return
        if self.__renamed_files[self.__index-1]:
            os.rename(self.__renamed_files[self.__index-1], os.path.join(SCAN_FOLDER, self.__files[self.__index-1]))
            self.__index -= 1
            self.launch_filter()
