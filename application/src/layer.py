import pygame as pg

from constants.window import WIDTH, HEIGHT, convert_rect, WIDTH_RATIO, HEIGHT_RATIO
from structures.clickable import Button
from structures.input_text import InputText
import threading

class Layer:
    def __init__(self, app):
        
        self.__screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        pg.display.set_caption("AutoFilter")

        self.__app = app
        self.__file = app.get_file_manager()
        self.__page = 0
        self.__left_image = None
        self.__right_image = None
        self.__auto_cycling = True
        self.__clipboard = ""

        self.__left_image_rect = convert_rect(50, 350, 1084, 680)
        self.__right_image_rect = convert_rect(1234, 100, 637, 900)
        self.__page_text_rect = (710*WIDTH_RATIO, 290*HEIGHT_RATIO)
        self.__file_text_rect = (20*WIDTH_RATIO, 40*HEIGHT_RATIO)

        
        name_rect = convert_rect(450, 20, 1020, 50)
        product_rect = convert_rect(710, 100, 500, 40)
        SN_rect = convert_rect(710, 150, 500, 40)
        designation_rect= convert_rect(710, 200, 500, 40)

        self.__focused_field = None
        self.name_input = InputText("Nom du fichier", name_rect, (200, 200, 200), self.is_focused, ".pdf")
        self.__product_input = InputText("Produit", product_rect, (200, 200, 200), self.is_focused)
        self.__SN_input = InputText("Numéro de Série", SN_rect, (200, 200, 200), self.is_focused)
        self.__designation_input = InputText("Désignation", designation_rect, (200, 200, 200), self.is_focused)
        self.__inputs = [self.name_input, self.__product_input, self.__SN_input, self.__designation_input]

        self.__text_size = int(32 * WIDTH_RATIO)
        ok_rect = convert_rect(1780, 20, 100, 50)
        return_rect = convert_rect(1650, 20, 100, 50)
        no_rect = convert_rect(1520, 20, 100, 50)
        previous_rect = convert_rect(810, 270, 130, 40)
        next_rect = convert_rect(945, 270, 130, 40)

        self.__ok_button = Button("SAVE", (0, 255, 0), ok_rect, 
            function=lambda: self.change_file(lambda: self.__file.save(self.name_input.get_text())), black_box=True, text_size=self.__text_size)
        self.__return_button = Button("RETURN", (245, 137, 54), return_rect, 
            function=lambda: self.change_file(self.__file.return_to_previous), black_box=True, text_size=self.__text_size)
        self.__no_button = Button("SKIP", (255, 0, 0), no_rect, 
            function=lambda: self.change_file(self.__file.delete), black_box=True, text_size=self.__text_size)
        self.__previous_button = Button("PREVIOUS", (255, 222, 172), previous_rect, 
            function=self.__previous_page, black_box=True, text_size=self.__text_size)
        self.__next_button = Button("NEXT", (255, 222, 172), next_rect, 
            function=self.__next_page, black_box=True, text_size=self.__text_size)
        self.__buttons = [self.__ok_button, self.__return_button, self.__no_button, self.__next_button, self.__previous_button]

    
    def page_update(self, page, text_filter):
        if not self.__auto_cycling:
            return
        main_text_filter = self.__file.get_main_filter()
        if main_text_filter == text_filter:
            self.__page = page
            self.__update_images()
            self.text_update(True)

    def change_file(self, function):
        function()
        self.__page = 0
        for inp in self.__inputs:
            inp.reset()
        text_filter = self.__file.get_main_filter()
        if text_filter is not None:
            self.__page = text_filter.get_current_page()
            self.__update_images()
            self.text_update(True)

    def __previous_page(self):
        self.__auto_cycling = False
        if self.__page > 0:
            self.__page -= 1
            self.__update_images()

    def __next_page(self):
        self.__auto_cycling = False
        if self.__page < self.__file.get_pages_number() - 1:
            self.__page += 1
            self.__update_images()
    
    def __update_images(self):
        text_filter = self.__file.get_main_filter()
        if text_filter is not None:
            image = text_filter.get_image(self.__page)
            if image is not None:
                self.__right_image = pg.image.fromstring(image.tobytes(), image.size, image.mode)
        text_filter = self.__file.get_main_filter()
        if text_filter is not None:
            image = text_filter.get_filtered_image(self.__page)
            if image is not None:
                self.__left_image = pg.image.fromstring(image.tobytes(), image.size, image.mode)
                
    def is_focused(self, field=None):
        if field is None:
            return self.__focused_field is not None
        return field == self.__focused_field

    def unfocus(self):
        self.__focused_field = None
    
    def __arrow_key(self, event):
        key = event.key
        if not self.is_focused() or self.__focused_field.get_text() == "":
            if key == pg.K_LEFT:
                self.__previous_page()
            elif key == pg.K_RIGHT:
                self.__next_page()
        elif key == pg.K_LEFT and self.__focused_field.cursor > 0:
            if event.mod & pg.KMOD_CTRL:
                self.__focused_field.cursor = 0
            else:
                self.__focused_field.cursor -= 1
        elif key == pg.K_RIGHT and self.__focused_field.cursor < len(self.__focused_field.get_text()):
            if event.mod & pg.KMOD_CTRL:
                self.__focused_field.cursor = len(self.__focused_field.get_text())
            else:
                self.__focused_field.cursor += 1
        idx = self.__inputs.index(self.__focused_field)
        if key == pg.K_UP:
            self.__focused_field = self.__inputs[(idx - 1) % len(self.__inputs)]
            self.__focused_field.cursor = len(self.__focused_field.get_text())
        elif key == pg.K_DOWN:
            self.__focused_field = self.__inputs[(idx + 1) % len(self.__inputs)]
            self.__focused_field.cursor = len(self.__focused_field.get_text())

    def letter_field_event(self, event):
        key = event.key
        if key == pg.K_RETURN or key == pg.K_KP_ENTER:
            self.change_file(lambda: self.__file.save(self.name_input.get_text()))
            return
        if not self.is_focused():
            return
        match key:
            case pg.K_BACKSPACE:
                if event.mod & pg.KMOD_CTRL:
                    self.__focused_field.delete_text(self.__focused_field.cursor)
                    self.text_update()
                else:
                    self.__focused_field.delete_text()
                    self.text_update()
            case pg.K_DELETE:
                if event.mod & pg.KMOD_CTRL:
                    self.__focused_field.delete_forward(len(self.__focused_field.get_text()) - self.__focused_field.cursor)
                    self.text_update()
                else:
                    self.__focused_field.delete_forward()
                self.text_update()
            case pg.K_LEFT:
                self.__arrow_key(event)
            case pg.K_RIGHT:
                self.__arrow_key(event)
            case pg.K_UP:
                self.__arrow_key(event)
            case pg.K_DOWN:
                self.__arrow_key(event)
            case pg.K_c if event.mod & pg.KMOD_CTRL:
                self.__clipboard = self.__focused_field.get_text()
            case pg.K_v if event.mod & pg.KMOD_CTRL:
                self.__focused_field.insert_text(self.__clipboard)
                self.text_update()
            case pg.K_TAB:
                idx = self.__inputs.index(self.__focused_field)
                self.__focused_field = self.__inputs[(idx + 1) % len(self.__inputs)]
                self.__focused_field.cursor = len(self.__focused_field.get_text())
            case _ if 32 <= key <= 126 or (event.unicode.isdigit() and event.unicode != "²" and 0 <= int(event.unicode) <= 9) or event.unicode == "-":
                self.__focused_field.insert_text(event.unicode)
                self.text_update()

    def text_update(self, with_filter=False):
        update_page = False
        if with_filter:
            text_filter = self.__file.get_main_filter()
            if text_filter is not None:
                text = text_filter.get_text(self.__page)
                if text is not None:
                    self.__product_input.set_text(text[0], text[3])
                    self.__SN_input.set_text(text[1], text[4])
                    self.__designation_input.set_text(text[2], text[5])
        if self.__focused_field != self.name_input:
            self.name_input.force_text(
                self.__product_input.get_text()
                + "-"
                + self.__SN_input.get_text()
                + "-"
                + self.__designation_input.get_text()
            )
        if self.__focused_field is None:
            if self.__SN_input.not_found:
                self.__focused_field = self.__SN_input
            elif self.__designation_input.not_found:
                self.__focused_field = self.__designation_input
            elif self.__product_input.not_found:
                self.__focused_field = self.__product_input
        if update_page:
            self.__page += 1
            self.__get_page()
    
    def handle_mouse(self, event):
        pos = event.pos
        for var_input in self.__inputs:
            if var_input.position.collidepoint(pos):
                self.__focused_field = var_input
                var_input.handle_mouse(pos)
                break
        for button in self.__buttons:
            button.check_clicked(event)

    def update(self):
        self.__screen.fill((100, 100, 100))
        for var_input in self.__inputs:
            var_input.draw(self.__screen)
        for button in self.__buttons:
            button.draw(self.__screen)
        # Draw text
        font = pg.font.SysFont(None, self.__text_size)
        text_surface = font.render(f"{self.__page+1}/{self.__file.get_pages_number()}", True, (255, 255, 255))
        self.__screen.blit(text_surface, text_surface.get_rect(midleft=(self.__page_text_rect)))
        text_surface = font.render(f"Fichier {self.__file.get_current_file_number()+1}/{self.__file.get_files_number()}", True, (255, 255, 255))
        self.__screen.blit(text_surface, text_surface.get_rect(midleft=(self.__file_text_rect)))
        # Draw left image
        if self.__left_image:
            img = pg.transform.scale(
                self.__left_image, (self.__left_image_rect.width, self.__left_image_rect.height)
            )
            self.__screen.blit(img, self.__left_image_rect.topleft)
        # Draw right image
        if self.__right_image:
            img = pg.transform.scale(
                self.__right_image, (self.__right_image_rect.width, self.__right_image_rect.height)
            )
            self.__screen.blit(img, self.__right_image_rect.topleft)
