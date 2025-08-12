from abc import abstractmethod

import pygame as pg


class Clickable(pg.Rect):
    """Superclass for all clickable objects"""

    def __init__(self, color, rect):
        self._color = color
        super().__init__(rect)

    def _is_clicked(self, event):
        """Check if the object is clicked"""
        return event.type == pg.MOUSEBUTTONDOWN and self.collidepoint(event.pos)

    def draw(self, screen):
        """Draw the object on the screen"""
        pg.draw.rect(screen, self._color, self)

    @abstractmethod
    def check_clicked(self, event):
        """Check if the object is clicked and perform the action"""
        pass


class Button(Clickable):
    """Class for creating buttons"""

    def __init__(
        self,
        text,
        color,
        rect,
        function=None,
        should_render=True,
        text_size=22,
        black_box=False,
        selected_color=None,
        selected=False,
    ):
        self.__action = function
        self.__text = text
        self.should_render = should_render
        self.__font = pg.font.Font(None, text_size)
        self.__black_box = black_box
        self.selected = selected
        self.__selected_color = selected_color
        super().__init__(color, rect)

    def draw(self, screen):
        """Draw the button on the screen"""
        if not self.should_render:
            return
        if self.selected and self.__selected_color is not None:
            pg.draw.rect(screen, self.__selected_color, self)
        else:
            super().draw(screen)
        text = self.__font.render(self.__text, True, pg.Color("black"))
        screen.blit(
            text,
            (
                self.x + self.width // 2 - text.get_width() // 2,
                self.y + self.height // 2 - text.get_height() // 2,
            ),
        )
        if self.__black_box:
            pg.draw.rect(screen, pg.Color("black"), self, 2)

    def check_clicked(self, event):
        """Check if the button is clicked and perform the action"""
        if not self.should_render:
            return False
        if self._is_clicked(event):
            if self.__action is not None:
                self.__action()
            return True
        return False
