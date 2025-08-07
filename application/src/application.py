import pygame as pg
from PIL import Image, ImageDraw
import win32con
import win32gui

from constants.window import *
from structures.input_text import InputText
from filter import Filter
import os
from constants.path import *
from structures.clickable import Button
import pytesseract
import threading
from PyPDF2 import PdfReader


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
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.width, self.height = WIDTH, HEIGHT
        pg.display.set_caption("AutoFilter")

        self.file_page_nb = 0
        self.running = True
        self.left_image = None
        self.right_image = None
        self.auto_cycling = True
        self.page = -1
        self.name_input = InputText(
            "Nom du fichier",
            pg.Rect(400, 20, WIDTH - 800, 50),
            (200, 200, 200), self,
            ".pdf"
        )
        self.product_input = InputText(
            "Produit", pg.Rect(WIDTH // 2 - 250, 100, 500, 40), (200, 200, 200), self
        )
        self.SN_input = InputText(
            "Numéro de Série", pg.Rect(WIDTH // 2 - 250, 150, 500, 40), (200, 200, 200), self
        )
        self.designation_input = InputText(
            "Désignation", pg.Rect(WIDTH // 2 - 250, 200, 500, 40), (200, 200, 200), self
        )
        self.inputs = [
            self.name_input,
            self.product_input,
            self.SN_input,
            self.designation_input,
        ]
        self.focused_field = None
        self.ok_button = Button("SAVE", (0, 255, 0), (WIDTH -200, 20), (100, 50), function=self.save, selected_color=(0, 200, 0), black_box=True, text_size=32)
        self.no_button = Button("SKIP", (255, 0, 0), (WIDTH -350, 20), (100, 50), function=self.delete, selected_color=(200, 0, 0), black_box=True, text_size=32)
        self.previous_button = Button("PREVIOUS", (255, 222, 172), (WIDTH // 2 - 250+100, 270), (130, 40), function=self.previous_page, black_box=True, text_size=32)
        self.next_button = Button("NEXT", (255, 222, 172), (WIDTH // 2 - 250+235, 270), (130, 40), function=self.next_page, black_box=True, text_size=32)
        self.buttons = [self.ok_button, self.no_button, self.next_button, self.previous_button]
        maximize_window()

        self.files = [f for f in os.listdir(SCAN_FOLDER) if os.path.isfile(os.path.join(SCAN_FOLDER, f))]
        self.fileIndex = -1
    
    def previous_page(self):
            self.auto_cycling = False
            if self.page > 0:
                self.page -= 1
                self.launch_filter()

    def next_page(self):
        self.auto_cycling = False
        if self.page < self.file_page_nb - 1:
            self.page += 1
            self.launch_filter()

    def set_left_image(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.left_image = pg.image.fromstring(data, size, mode)

    def set_right_image(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.right_image = pg.image.fromstring(data, size, mode)

    def handle_keyboard(self, event):
        if event.key == pg.K_ESCAPE:
            self.focused_field = None
        elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
            self.save()
        elif event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
            if self.focused_field is None or self.focused_field.text == "":
                if event.key == pg.K_LEFT:
                    self.previous_page()
                else:
                    self.next_page()
                return
            if event.key == pg.K_LEFT and self.focused_field.cursor > 0:
                self.focused_field.cursor -= 1
            elif event.key == pg.K_RIGHT and self.focused_field.cursor < len(self.focused_field.text):
                self.focused_field.cursor += 1
        elif self.focused_field is None:
            return
        elif event.key == pg.K_BACKSPACE:
            self.focused_field.delete_text()
            self.text_update()
        elif event.key == pg.K_TAB:
            idx = self.inputs.index(self.focused_field)
            self.focused_field = self.inputs[(idx + 1) % len(self.inputs)]
            self.focused_field.cursor = len(self.focused_field.text)
        elif event.key == pg.K_DELETE:
            self.focused_field.delete_forward()
            self.text_update()
        elif event.key == pg.K_LCTRL or event.key == pg.K_RCTRL:
            pass
        elif (event.mod & pg.KMOD_CTRL) and event.unicode:
            pass
        elif 32 <= event.key <= 126 or (event.unicode.isdigit() and 0 <= int(event.unicode) <= 9) or event.unicode == "-":
            self.focused_field.insert_text(event.unicode)
            self.text_update()

    def handle_event(self):
        for event in pg.event.get():
            if (
                event.type == pg.QUIT
            ):
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.handle_keyboard(event)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for var_input in self.inputs:
                    if var_input.position.collidepoint(mouse_pos):
                        self.focused_field = var_input
                        var_input.handle_mouse(mouse_pos)
                        break
                for button in self.buttons:
                    button.check_clicked(event)

    def run(self):
        clock = pg.time.Clock()

        left_rect = pg.Rect(50, 350, WIDTH - ((HEIGHT - 180) * 21 / 29.7)-200, HEIGHT - 400)
        right_rect = pg.Rect(
            WIDTH - 50 - (HEIGHT - 180) * 21 / 29.7,
            100,
            (HEIGHT - 180) * 21 / 29.7,
            HEIGHT - 180,
        )
        while self.running:

            self.handle_event()
            self.draw(left_rect, right_rect)
            pg.display.update()
            clock.tick(FPS)
        pg.quit()
        exit()
    
    def draw(self, left_rect, right_rect):
        self.screen.fill((100, 100, 100))
        for var_input in self.inputs:
            var_input.draw(self.screen)
        for button in self.buttons:
            button.draw(self.screen)
        # Draw left image
        if self.left_image:
            img = pg.transform.scale(
                self.left_image, (left_rect.width, left_rect.height)
            )
            self.screen.blit(img, left_rect.topleft)
        # Draw text above the left image
        font = pg.font.SysFont(None, 36)
        text_surface = font.render(f"{self.page+1}/{self.file_page_nb}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(WIDTH // 2 - 250, 290))
        self.screen.blit(text_surface, text_rect)
        text_surface = font.render(f"Fichier {self.fileIndex+1}/{len(self.files)}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(20, 40))
        self.screen.blit(text_surface, text_rect)
        # Draw right image
        if self.right_image:
            img = pg.transform.scale(
                self.right_image, (right_rect.width, right_rect.height)
            )
            self.screen.blit(img, right_rect.topleft)

    def text_update(self):
        if self.focused_field != self.name_input:
            self.name_input.text = (
                self.product_input.get_text()
                + "-"
                + self.SN_input.get_text()
                + "-"
                + self.designation_input.get_text()
            )
        if self.focused_field is None:
            if self.SN_input.not_found:
                self.focused_field = self.SN_input
            elif self.designation_input.not_found:
                self.focused_field = self.designation_input
            elif self.product_input.not_found:
                self.focused_field = self.product_input

    def save(self):
        if self.fileIndex >= 0:
            filename = self.files[self.fileIndex]
            original_path = os.path.join(SCAN_FOLDER, filename)
            filtered_path = os.path.join(FILTERED_FOLDER, self.name_input.get_text() + ".pdf")
            try:
                os.rename(original_path, filtered_path)
            except FileExistsError as e:
                with open(filtered_path, "rb") as f:
                    self.set_left_image(Image.open(f))
        self.next_file()

    def delete(self):
        if self.fileIndex >= 0:
            filename = self.files[self.fileIndex]
            original_path = os.path.join(SCAN_FOLDER, filename)
            unreadable_path = os.path.join(UNREADABLE_FOLDER, filename)
            os.rename(original_path, unreadable_path)
        self.next_file()

    def next_file(self):
        for input_field in self.inputs:
            input_field.text = ""
            input_field.cursor = 0
            input_field.not_found = False
        self.fileIndex += 1
        pdf_path = os.path.join(SCAN_FOLDER, self.files[self.fileIndex])
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            self.file_page_nb = len(reader.pages)
        self.auto_cycling = True
        self.page = 0
        self.launch_filter()
    
    def launch_filter(self):
        if self.fileIndex < len(self.files):
            threading.Thread(target=lambda: Filter(self.files[self.fileIndex], self).get_name_of_file(), daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.run()
