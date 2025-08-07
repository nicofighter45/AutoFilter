import pygame as pg
from constants.window import *


class InputText:
    def __init__(self, default_text, position, color, app, text_extension=""):
        self.text = ""
        self.cursor = 0
        self.default_text = default_text
        self.position = position
        self.color = color
        self.text_extension = text_extension
        self.blink = 0
        self.font = pg.font.SysFont(None, 32)
        self.not_found = False
        self.app = app

    def set_text(self, text):
        if self.app.focused_field == self:
            return
        if text == "":
            self.not_found = True
        self.text = text
        self.cursor = len(text)

    def insert_text(self, text):
        self.text = self.text[: self.cursor] + text + self.text[self.cursor :]
        self.cursor += len(text)

    def delete_text(self):
        if self.cursor > 0:
            self.text = self.text[: self.cursor - 1] + self.text[self.cursor :]
            self.cursor -= 1

    def delete_forward(self):
        if self.cursor < len(self.text):
            self.text = self.text[: self.cursor] + self.text[self.cursor + 1 :]

    def get_text(self):
        return self.text

    def get_cursor(self):
        return self.cursor

    def handle_mouse(self, pos):
        if self.text == "":
            return
        relative_x = pos[0] - (self.position.x + 10)
        acc_width = 0
        self.cursor = 0
        for i in range(len(self.text) + 1):
            segment = self.text[:i]
            segment_surface = self.font.render(segment, True, (0, 0, 0))
            width = segment_surface.get_width()
            if width > relative_x:
                break
            self.cursor = i

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.position)
        if self.text == "":
            default_text = self.default_text
            if self.not_found:
                default_text += " (Non trouvé)"
            italic_font = pg.font.SysFont(None, 32, italic=True)
            txt_surface = italic_font.render(default_text, True, (120, 120, 120))
            self.cursor = 0
        else:
            txt_surface = self.font.render(
                self.text + self.text_extension, True, (0, 0, 0)
            )

        if self.app.focused_field == self:
            if self.blink % FPS < FPS // 2:
                cursor_pos = min(self.cursor, len(self.text))
                cursor_text = self.text[:cursor_pos]
                cursor_surface = self.font.render(cursor_text, True, (0, 0, 0))
                cursor_x = self.position.x + 10 + cursor_surface.get_width()
                cursor_y = self.position.y + (self.position.height // 2) - 12
                pg.draw.line(
                    screen,
                    (0, 0, 0),
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + 24),
                    2,
                )
            self.blink += 1
        # Center vertically, align left horizontally
        text_rect = txt_surface.get_rect()
        text_rect.x = self.position.x + 10  # left padding
        text_rect.centery = self.position.centery
        screen.blit(txt_surface, text_rect)
