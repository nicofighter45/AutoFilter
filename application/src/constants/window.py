import pygame as pg

FPS = 30
DPI = 300
WIDTH = 1920
HEIGHT = 1080
THREAD_FORWARDING = 10

STANDART_WIDTH = 1920
STANDART_HEIGHT = 1080
WIDTH_RATIO = STANDART_WIDTH / WIDTH
HEIGHT_RATIO = STANDART_HEIGHT / HEIGHT


def convert_rect(x, y, w, h):
    return pg.Rect(
        int(x * WIDTH_RATIO),
        int(y * HEIGHT_RATIO),
        int(w * WIDTH_RATIO),
        int(h * HEIGHT_RATIO),
    )
