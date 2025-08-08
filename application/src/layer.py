import pygame as pg

from constants.window import WIDTH, HEIGHT, convert_rect, WIDTH_RATIO, HEIGHT_RATIO
from structures.clickable import Button
from structures.input_text import InputText

class Layer:
    def __init__(self, app):
        
        self.__screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        pg.display.set_caption("AutoFilter")

        self.__file = app.get_file_manager()
        self.__page = -1
        self.__left_image = None
        self.__right_image = None

        self.__left_image_rect = convert_rect(50, 350, 1084, 680)
        self.__right_image_rect = convert_rect(1234, 100, 637, 900)
        self.__page_text_rect = (710*WIDTH_RATIO, 290*HEIGHT_RATIO)
        self.__file_text_rect = (20*WIDTH_RATIO, 40*HEIGHT_RATIO)

        
        name_rect = convert_rect(450, 20, 1020, 50)
        product_rect = convert_rect(710, 100, 500, 40)
        SN_rect = convert_rect(710, 150, 500, 40)
        designation_rect= convert_rect(710, 200, 500, 40)

        self.__focused_field = None
        self.name_input = InputText("Nom du fichier", name_rect, (200, 200, 200), self, ".pdf")
        self.product_input = InputText("Produit", product_rect, (200, 200, 200), self)
        self.SN_input = InputText("Numéro de Série", SN_rect, (200, 200, 200), self)
        self.designation_input = InputText("Désignation", designation_rect, (200, 200, 200), self)
        self.__inputs = [self.__name_input, self.__product_input, self.__SN_input, self.__designation_input]

        self.__text_size = 32 * WIDTH_RATIO
        ok_rect = convert_rect(1720, 20, 100, 50)
        return_rect = convert_rect(1630, 20, 100, 50)
        no_rect = convert_rect(1420, 20, 100, 50)
        previous_rect = convert_rect(810, 270, 130, 40)
        next_rect = convert_rect(945, 270, 130, 40)

        self.__ok_button = Button("SAVE", (0, 255, 0), ok_rect, 
            function=app.launch_filter(self.__file.save()), black_box=True, text_size=self.__text_size)
        self.__return_button = Button("RETURN", (245, 137, 54), return_rect, 
            function=app.launch_filter(self.__file.return_to_previous), black_box=True, text_size=self.__text_size)
        self.__no_button = Button("SKIP", (255, 0, 0), no_rect, 
            function=app.launch_filter(self.__file.delete()), black_box=True, text_size=self.__text_size)
        self.__previous_button = Button("PREVIOUS", (255, 222, 172), previous_rect, 
            function=self.previous_page, black_box=True, text_size=self.__text_size)
        self.__next_button = Button("NEXT", (255, 222, 172), next_rect, 
            function=self.next_page, black_box=True, text_size=self.__text_size)
        self.__buttons = [self.__ok_button, self.__return_button, self.__no_button, self.__next_button, self.__previous_button]

    def previous_page(self):
        self.__autocycling = False
        if self.__page > 0:
            self.__page -= 1
            self.__app.launch_filter()

    def next_page(self):
        self.__autocycling = False
        if self.__page < self.__file.get_pages_number() - 1:
            self.__page += 1
            self.__app.launch_filter()

    def set_left_image(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.__left_image = pg.image.fromstring(data, size, mode)

    def set_right_image(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        self.__right_image = pg.image.fromstring(data, size, mode)

    def is_focused(self):
        return self.focused_field is not None

    def unfocus(self):
        self.focused_field = None
    
    def arrow_key(self, key):
        if not self.is_focused() or self.__focused_field.text == "":
            if event.key == pg.K_LEFT:
                self.previous_page()
            else:
                self.next_page()
            return
        if event.key == pg.K_LEFT and self.__layer.focused_field.cursor > 0:
            self.__layer.focused_field.cursor -= 1
        elif event.key == pg.K_RIGHT and self.__layer.focused_field.cursor < len(self.__layer.focused_field.text):
            self.__layer.focused_field.cursor += 1

    def letter_field_event(self, key):
        if not self.is_focused():
            return
        match key:
            case pg.K_BACKSPACE:
                self.__focused_field.delete_text()
                self.__text_update()
            case pg.K_TAB:
                idx = self.__inputs.index(self.__focused_field)
                self.__focused_field = self.__inputs[(idx + 1) % len(self.__inputs)]
                self.__focused_field.cursor = len(self.__focused_field.text)
            case pg.K_DELETE:
                self.__focused_field.delete_forward()
                self.__text_update()
            case pg.K_LCTRL | pg.K_RCTRL:
                pass
            case _ if (event.mod & pg.KMOD_CTRL) and event.unicode:
                pass
            case _ if 32 <= key <= 126 or (event.unicode.isdigit() and event.unicode != "²" and 0 <= int(event.unicode) <= 9) or event.unicode == "-":
                self.__focused_field.insert_text(event.unicode)
                self.__text_update()

    def text_update(self):
        if self.__focused_field != self.__name_input:
            self.__name_input.text = (
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
    
    def handle_mouse(self, pos):
        for var_input in self.__inputs:
            if var_input.position.collidepoint(mouse_pos):
                self.__focused_field = var_input
                var_input.handle_mouse(mouse_pos)
                break
        for button in self.buttons:
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
