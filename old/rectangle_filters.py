import fitz
from PIL import Image, ImageDraw
import folders
import pygame as pg
import os
import threading
import win32con
import win32gui

FILTERS = {"SEQUENCES POUR UN OF": ((280, 115, 540, 140), (0, 0, 100, 100))}

REMOVE_AT_THE_END = [":", " ", "`", "'", "\\v", "—"]

WIDTH, HEIGHT = 1920, 1080


class Window:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(
            (WIDTH, HEIGHT), pg.RESIZABLE
        )  # No flags: normal window
        self.width, self.height = WIDTH, HEIGHT
        pg.display.set_caption("AutoFilter")
        self.font = pg.font.SysFont(None, 32)
        self.input_text = ""
        self.cursor = 0
        self.blink = 0
        self.left_image = None
        self.right_image = None
        self.shouldUpdate = True

        window_handle = win32gui.FindWindow(None, "AutoFilter")
        if window_handle:
            window_placement = win32gui.GetWindowPlacement(window_handle)
            if window_placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
            win32gui.ShowWindow(window_handle, win32con.SW_MAXIMIZE)

    def set_input_text(self, text):
        self.input_text = text
        self.shouldUpdate = True

    def set_left_image(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.left_image = pg.image.fromstring(data, size, mode)
        self.shouldUpdate = True

    def set_right_image(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.right_image = pg.image.fromstring(data, size, mode)
        self.shouldUpdate = True

    def run(self):
        clock = pg.time.Clock()

        input_box = pg.Rect(350, 20, WIDTH - 700, 50)
        left_rect = pg.Rect(100, 100, (HEIGHT - 180) * 21 / 29.7, HEIGHT - 160)
        right_rect = pg.Rect(
            WIDTH - 100 - (HEIGHT - 180) * 21 / 29.7,
            100,
            (HEIGHT - 180) * 21 / 29.7,
            HEIGHT - 180,
        )
        running = True
        while running:
            for event in pg.event.get():
                if (
                    event.type == pg.QUIT
                    or event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE
                ):
                    running = False
                elif event.type == pg.KEYDOWN and (
                    event.key == pg.K_LEFT or event.key == pg.K_RIGHT
                ):
                    if event.key == pg.K_LEFT and self.cursor > 0:
                        self.cursor -= 1
                    elif event.key == pg.K_RIGHT and self.cursor < len(self.input_text):
                        self.cursor += 1
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        if len(self.input_text) > 0 and self.cursor > 0:
                            self.input_text = (
                                self.input_text[: self.cursor - 1]
                                + self.input_text[self.cursor :]
                            )
                            self.cursor -= 1
                    else:
                        self.cursor += 1
                        self.input_text = (
                            self.input_text[: self.cursor - 1]
                            + event.unicode
                            + self.input_text[self.cursor - 1 :]
                        )

            self.shouldUpdate = True
            self.screen.fill((100, 100, 100))
            # Draw input box
            pg.draw.rect(self.screen, (200, 200, 200), input_box)
            if self.input_text == "":
                # Render default italic text
                default_text = "Tappez du texte pour renommer le fichier"
                italic_font = pg.font.SysFont(None, 32, italic=True)
                txt_surface = italic_font.render(default_text, True, (120, 120, 120))
            else:
                txt_surface = self.font.render(
                    self.input_text + ".pdf", True, (0, 0, 0)
                )
                # Draw blinking cursor if focused
                if self.blink % 60 < 30:  # Blinks every half second at 60 FPS
                    # Place the cursor after the last self.cursor characters
                    cursor_pos = min(self.cursor, len(self.input_text))
                    cursor_text = self.input_text[:cursor_pos]
                    cursor_surface = self.font.render(cursor_text, True, (0, 0, 0))
                    cursor_x = input_box.x + 10 + cursor_surface.get_width()
                    cursor_y = input_box.y + (input_box.height // 2) - 12
                    pg.draw.line(
                        self.screen,
                        (0, 0, 0),
                        (cursor_x, cursor_y),
                        (cursor_x, cursor_y + 24),
                        2,
                    )
                self.blink += 1
            # Center vertically, align left horizontally
            text_rect = txt_surface.get_rect()
            text_rect.x = input_box.x + 10  # left padding
            text_rect.centery = input_box.centery
            self.screen.blit(txt_surface, text_rect)
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
            clock.tick(60)
        pg.quit()
        exit()


window = Window()


class Filter:

    def __init__(self, filename):
        self._converted_file = os.path.join(folders.CONVERTED_FOLDER, filename)
        self._original_file = os.path.join(folders.ORIGINAL_FOLDER, filename)
        self._doc = fitz.open(self._converted_file)
        self._text = self._doc[0].get_text()
        self._name = ""

        original_doc = fitz.open(self._original_file)
        pix = original_doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        window.set_right_image(img)
        original_doc.close()

    def __del__(self):
        if hasattr(self, "_doc"):
            self._doc.close()

    def show_converted_file(self):
        pix = self._doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        window.set_left_image(img)

    def get_name_of_file(self):
        for document_key in FILTERS.keys():
            if self._text[:50].find(document_key) == -1:
                continue
            for field_position in FILTERS[document_key]:
                self._get_from_strings(field_position)
                self._name += "-"
            break
        else:
            print("no key detected", self._converted_file)
            self.show_converted_file()
            return ""

        if len(self._not_detected) != 0:
            print("not detected", self._not_detected)
            self.show_converted_file()
            return ""

        self._name = self._name[:-1]
        for remove in REMOVE_AT_THE_END:
            self._name = self._name.replace(remove, "")
        if "--" in self._name or self._name[0] == "-" or self._name[-1] == "-":
            print("missing detect", self._name)
            self.show_converted_file()
            return ""
        print("Successfully filtered", self._name)
        return self._name + ".pdf"

    def _get_from_strings(self, keys):
        hasnt_been_called = True
        text = self._doc[0].get_textbox(fitz.Rect(keys))
        print("extracted text", text)

        scale_factor = 1  # Example scale factor
        rect = fitz.Rect(*[coord * scale_factor for coord in keys])
        # Show the scaled rectangle using tkinter

        page = self._doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Draw the rectangle on the image
        draw = ImageDraw.Draw(img)
        x0, y0, x1, y1 = rect
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)

        # Show image in tkinter window
        window.set_left_image(img)
        window.shouldUpdate = True
        return


filter = Filter(R"20250804153153.pdf")
thread = threading.Thread(target=filter.get_name_of_file)
thread.start()
window.run()
