import pygame as pg
from PIL import Image, ImageDraw
import win32con
import win32gui

from constants.window import *
from structures.input_text import InputText


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
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        self.width, self.height = WIDTH, HEIGHT
        pg.display.set_caption("AutoFilter")

        self.running = True
        self.left_image = None
        self.right_image = None
        self.name_input = InputText(
            "Nom du fichier",
            pg.Rect(350, 20, WIDTH - 700, 50),
            (200, 200, 200),
            ".pdf",
        )
        self.product_input = InputText(
            "Produit", pg.Rect(WIDTH // 2 - 300, 100, 600, 40), (200, 200, 200)
        )
        self.SN_input = InputText(
            "Numéro de Série", pg.Rect(WIDTH // 2 - 300, 150, 600, 40), (200, 200, 200)
        )
        self.designation_input = InputText(
            "Désignation", pg.Rect(WIDTH // 2 - 300, 200, 600, 40), (200, 200, 200)
        )
        self.inputs = [
            self.name_input,
            self.product_input,
            self.SN_input,
            self.designation_input,
        ]
        self.focused_field = self.name_input
        maximize_window()

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

    def handle_event(self):
        for event in pg.event.get():
            if (
                event.type == pg.QUIT
                or event.type == pg.KEYDOWN
                and event.key == pg.K_ESCAPE
            ):
                self.running = False
            elif event.type == pg.KEYDOWN and (
                event.key == pg.K_LEFT or event.key == pg.K_RIGHT
            ):
                if event.key == pg.K_LEFT and self.focused_field.cursor > 0:
                    self.focused_field.cursor -= 1
                elif event.key == pg.K_RIGHT and self.focused_field.cursor < len(
                    self.focused_field.text
                ):
                    self.focused_field.cursor += 1
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    self.focused_field.delete_text()
                    self.text_update()
                elif 32 <= event.key <= 126 or (
                    event.unicode.isdigit() and 0 <= int(event.unicode) <= 9
                ):
                    self.focused_field.insert_text(event.unicode)
                    self.text_update()
                elif event.key == pg.K_TAB:
                    idx = self.inputs.index(self.focused_field)
                    self.focused_field = self.inputs[(idx + 1) % len(self.inputs)]
                    self.focused_field.cursor = len(self.focused_field.text)
                elif event.key == pg.K_DELETE:
                    self.focused_field.delete_forward()
                    self.text_update()
                elif event.key == pg.K_RETURN:
                    self.next_file()
                    for input_field in self.inputs:
                        input_field.text = ""
                        input_field.cursor = 0
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for input in self.inputs:
                    if input.position.collidepoint(mouse_pos):
                        self.focused_field = input
                        input.handle_mouse(mouse_pos)
                        break

    def run(self):
        clock = pg.time.Clock()

        left_rect = pg.Rect(100, 100, (HEIGHT - 180) * 21 / 29.7, HEIGHT - 160)
        right_rect = pg.Rect(
            WIDTH - 100 - (HEIGHT - 180) * 21 / 29.7,
            100,
            (HEIGHT - 180) * 21 / 29.7,
            HEIGHT - 180,
        )
        while self.running:

            self.handle_event()
            self.screen.fill((100, 100, 100))
            for input in self.inputs:
                input.draw(self.screen, focused=input == self.focused_field)
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
            pg.display.update()
            clock.tick(FPS)
        pg.quit()
        exit()

    def text_update(self):
        if self.focused_field != self.name_input:
            self.name_input.text = (
                self.product_input.get_text()
                + "-"
                + self.SN_input.get_text()
                + "-"
                + self.designation_input.get_text()
            )

    def next_file(self):
        # Logic to move to the next file
        pass
