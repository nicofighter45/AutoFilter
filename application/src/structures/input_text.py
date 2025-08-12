import pygame as pg
from constants.window import FPS


class InputText:
    def __init__(self, default_text, position, color, is_focused, text_extension=""):
        self.__text = ""
        self.cursor = 0
        self.__default_text = default_text
        self.__main_default_text = default_text
        self.position = position
        self.__color = color
        self.__text_extension = text_extension
        self.__blink = 0
        self.__font = pg.font.SysFont(None, 32)
        self.not_found = False
        self.__is_focused = is_focused
    
    def reset(self):
        self.__text = ""
        self.cursor = 0
        self.__default_text = self.__main_default_text
        self.not_found = False

    def set_text(self, text, default=None):
        if text == "":
            self.not_found = True
            if default is not None:
                self.__default_text = default
            return
        self.not_found = False
        if self.__text == "":
            self.__text = text
            self.cursor = len(text)
    
    def force_text(self, text):
        self.__text = text
        self.cursor = len(text)

    def insert_text(self, text):
        self.__text = self.__text[: self.cursor] + text + self.__text[self.cursor :]
        self.cursor += len(text)

    def delete_text(self, nb=1):
        if self.cursor >= nb:
            self.__text = self.__text[: self.cursor - nb] + self.__text[self.cursor :]
            self.cursor -= nb

    def delete_forward(self, nb=1):
        if self.cursor-nb <= len(self.__text):
            self.__text = self.__text[: self.cursor] + self.__text[self.cursor + nb :]

    def get_text(self):
        return self.__text

    def get_cursor(self):
        return self.cursor

    def handle_mouse(self, pos):
        if self.__text == "":
            return
        relative_x = pos[0] - (self.position.x + 10)
        acc_width = 0
        self.cursor = 0
        for i in range(len(self.__text) + 1):
            segment = self.__text[:i]
            segment_surface = self.__font.render(segment, True, (0, 0, 0))
            width = segment_surface.get_width()
            if width > relative_x:
                break
            self.cursor = i

    def draw(self, screen):
        pg.draw.rect(screen, self.__color, self.position)
        if self.__text == "":
            default_text = self.__default_text
            if self.not_found:
                default_text += " (Non trouvé)"
            italic_font = pg.font.SysFont(None, 32, italic=True)
            txt_surface = italic_font.render(default_text, True, (120, 120, 120))
            self.cursor = 0
        else:
            txt_surface = self.__font.render(
                self.__text + self.__text_extension, True, (0, 0, 0)
            )

        if self.__is_focused(self):
            if self.__blink % FPS < FPS // 2:
                cursor_pos = min(self.cursor, len(self.__text))
                cursor_text = self.__text[:cursor_pos]
                cursor_surface = self.__font.render(cursor_text, True, (0, 0, 0))
                cursor_x = self.position.x + 10 + cursor_surface.get_width()
                cursor_y = self.position.y + (self.position.height // 2) - 12
                pg.draw.line(
                    screen,
                    (0, 0, 0),
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y + 24),
                    2,
                )
            self.__blink += 1
        # Center vertically, align left horizontally
        text_rect = txt_surface.get_rect()
        text_rect.x = self.position.x + 10  # left padding
        text_rect.centery = self.position.centery
        screen.blit(txt_surface, text_rect)
