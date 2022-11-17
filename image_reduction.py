import sys

import pygame
import simplified_pygame

import game_modes as game
from tetris import StartTitle
from settings import SAVED_SETTINGS, ACTIVE_SETTINGS


#set screen
SCREEN = simplified_pygame.PyGameWindow(
    w=SAVED_SETTINGS['w'],
    h=SAVED_SETTINGS['h'],
    caption='Tetris for two',
    use_icon=True,
    bg_color=(230, 230, 230),
    default_font='cambria',
    resizable=True)


# upload sprited
# cắt ảnh từ file scr5-copy lưu vào scr5-copy2
S = simplified_pygame.Canvas.load(simplified_pygame.assets_path('../screens/scr5 - Copy.png'), corner_alpha=True).surface
for i in range(500):
    for j in range(500):
        x, y = int(i*5.656854249492381 + 3), int(j*5.656854249492381 +4 )
        S.set_at((i, j), S.get_at((x, y)))
        S.set_at((x, y), (0, 0, 0))

pygame.image.save(S, 'scr5-Copy2.png')

pygame.quit()
