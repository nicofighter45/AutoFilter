import os
from PyPDF2 import PdfReader

from constants.path import SCAN_FOLDER, FILTERED_FOLDER, UNREADABLE_FOLDER

class FileManager:
    def __init__(self):
        self.__pages = 0
        self.__index = -1
        self.__files = [f for f in os.listdir(SCAN_FOLDER) if os.path.isfile(os.path.join(SCAN_FOLDER, f))]
        self.__renamed_files = [None for _ in self.__files]
        self.__filters = [None for _ in self.__files]
    
    
    def get_main_filter(self):
        return self.__filters[self.__index]


    def save(self, name):
        if self.__index == -1:
            self.__next_file()
            return
        filename = self.__files[self.__index]
        original_path = os.path.join(SCAN_FOLDER, filename)
        filtered_path = os.path.join(FILTERED_FOLDER, name + ".pdf")
        try:
            os.rename(original_path, filtered_path)
            self.__renamed_files[self.__index] = filtered_path
        except FileExistsError:
            self.save(name + " (1)")
            return
        self.__next_file()

    def delete(self):
        if self.__index == -1:
            return self.__next_file()
        filename = self.__files[self.__index]
        original_path = os.path.join(SCAN_FOLDER, filename)
        unreadable_path = os.path.join(UNREADABLE_FOLDER, filename)
        os.rename(original_path, unreadable_path)
        self.__renamed_files[self.__index] = unreadable_path
        self.__next_file()

    def __next_file(self):
        self.__index += 1
        if self.__index == len(self.__files):
            return
        path = os.path.join(SCAN_FOLDER, self.__files[self.__index])
        with open(path, "rb") as f:
            self.__pages = len(PdfReader(f).pages)
        
        # todo launching a filter
        
    def launch_filter(self, index=None):
        if not 0 <= index < len(self.__files):
            return
        if index is None:
            Filter(file, self.__layer, self.get_file_manager().get_pages_number())
            threading.Thread(target=self.main_filter.get_name_of_file, daemon=True).start()
            self.__running_filters[index] = self.main_filter
        thread = threading.Thread(target=filter.get_name_of_file, daemon=True)
        thread.start()
        self.__running_filters[self.get_file_manager().get_current_file_number()] = thread


    def get_current_file_number(self):
        return self.__index

    def get_pages_number(self, index=None):
        if index is None:
            return self.__pages
        if 0 <= index < len(self.__renamed_files):
            with open(os.path.join(SCAN_FOLDER, self.__files[index]), "rb") as f:
                return len(PdfReader(f).pages)
        return 0

    def get_files_number(self):
        return len(self.__files)
    
    def return_to_previous(self):
        if self.__index == 0:
            return None
        if self.__renamed_files[self.__index-1]:
            os.rename(self.__renamed_files[self.__index], os.path.join(SCAN_FOLDER, self.__files[self.__index]))
            self.__index -= 2
            return self.__next_file()
        return None
