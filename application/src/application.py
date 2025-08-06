import pygame as pg
from PIL import Image, ImageDraw
import win32con
import win32gui

from constants.window import *
from structures.input_text import InputText
from filter import Filter
import os
from constants.folders import *
from structures.clickable import Button


def maximize_window():
    window_handle = win32gui.FindWindow(None, "AutoFilter")
    if window_handle:
        window_placement = win32gui.GetWindowPlacement(window_handle)
        if window_placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
        win32gui.ShowWindow(window_handle, win32con.SW_MAXIMIZE)


class App:
    def __init__(self):
        
        for f in os.listdir(CROPPED_FOLDER):
            file_path = os.path.join(CROPPED_FOLDER, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.width, self.height = WIDTH, HEIGHT
        pg.display.set_caption("AutoFilter")

        self.running = True
        self.left_image = None
        self.right_image = None
        self.name_input = InputText(
            "Nom du fichier",
            pg.Rect(400, 20, WIDTH - 800, 50),
            (200, 200, 200),
            ".pdf",
        )
        self.product_input = InputText(
            "Produit", pg.Rect(WIDTH // 2 - 250, 100, 500, 40), (200, 200, 200)
        )
        self.SN_input = InputText(
            "Numéro de Série", pg.Rect(WIDTH // 2 - 250, 150, 500, 40), (200, 200, 200)
        )
        self.designation_input = InputText(
            "Désignation", pg.Rect(WIDTH // 2 - 250, 200, 500, 40), (200, 200, 200)
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
        self.buttons = [self.ok_button, self.no_button]
        maximize_window()

        self.converted_files = []
        self.converted_files = [
            f
            for f in os.listdir(CONVERTED_FOLDER)
            if os.path.isfile(os.path.join(CONVERTED_FOLDER, f))
        ]
        self.fileIndex = -1

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
        if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
            self.save()
        elif self.focused_field is None:
            return
        elif event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
            if event.key == pg.K_LEFT and self.focused_field.cursor > 0:
                self.focused_field.cursor -= 1
            elif event.key == pg.K_RIGHT and self.focused_field.cursor < len(self.focused_field.text):
                self.focused_field.cursor += 1
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
                or event.type == pg.KEYDOWN
                and event.key == pg.K_ESCAPE
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

        left_rect = pg.Rect(50, 100, (HEIGHT - 180) * 21 / 29.7, HEIGHT - 160)
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
            var_input.draw(self.screen, focused=var_input == self.focused_field)
        for button in self.buttons:
            button.draw(self.screen)
        # Draw left image
        if self.left_image:
            img = pg.transform.scale(
                self.left_image, (left_rect.width, left_rect.height)
            )
            self.screen.blit(img, left_rect.topleft)
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
    
    def save(self):
        if self.fileIndex >= 0:
            filename = self.converted_files[self.fileIndex]
            original_path = os.path.join(ORIGINAL_FOLDER, filename)
            converted_path = os.path.join(CONVERTED_FOLDER, filename)
            filtered_path = os.path.join(FILTERED_FOLDER, self.name_input.get_text() + ".pdf")
            converted_filtered_path = os.path.join(CONVERTED_FILTERED_FOLDER, filename)
            os.rename(original_path, filtered_path)
            os.rename(converted_path, converted_filtered_path)
        self.next_file()

    def delete(self):
        if self.fileIndex >= 0:
            filename = self.converted_files[self.fileIndex]
            original_path = os.path.join(ORIGINAL_FOLDER, filename)
            converted_path = os.path.join(CONVERTED_FOLDER, filename)
            unreadable_path = os.path.join(UNREADABLE_FOLDER, filename)
            converted_filtered_path = os.path.join(CONVERTED_FILTERED_FOLDER, filename)
            os.rename(original_path, unreadable_path)
            os.rename(converted_path, converted_filtered_path)
        self.next_file()

    def next_file(self):
        for input_field in self.inputs:
            input_field.text = ""
            input_field.cursor = 0
            input_field.not_found = False
        self.fileIndex += 1
        if self.fileIndex < len(self.converted_files):
            Filter(self.converted_files[self.fileIndex], self).get_name_of_file()


if __name__ == "__main__":
    app = App()
    app.run()
