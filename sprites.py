from settings import SAVED_SETTINGS, DEFAULT_COLORS
from simplified_pygame import SPRITES, Canvas, assets_path

# upload sprited
sprites = Canvas.load(assets_path('menu_sprites.png'), corner_alpha=True)
items = """ \
    _TetrisGame _TetrisHeartMode _TetrisGameWrestling
    _TetrisGame2Players _TetrisGameMirror _TetrisGameSpeedUp
    _TetrisGameSwap _TetrisGameBalance _TetrisGameCommonWell
    empty_wasd arrows controller
    mouse
    """
#cắt ảnh từ file menu_sprites.png trong thư mục assets
for k, line in enumerate(items.split('\n')):
    for i, U in enumerate(line.split()):
        X, Y = 5 + i*176, 5 + k*106
        SPRITES[U] = sprites.crop(X, Y, 175, 105)
def make_game_mode_sprites():
    new_color = SAVED_SETTINGS['color_scheme']#màu nền mới
    color_scheme = {tuple(col): tuple(new_color[k]) for k, col in DEFAULT_COLORS.items()}
    #color_scheme: 1 dict bao gồm key là màu DEFAULT_COLORS, value là màu mới
    
    sprites = [spr for spr in SPRITES if spr.startswith('_')]
    #sprites=['_TetrisGame','_TetrisHeartMode','_TetrisGameWrestling','_TetrisGame2Players','_TetrisGameMirror','_TetrisGameSpeedUp','_TetrisGameSwap',
    #'_TetrisGameBalance','_TetrisGameCommonWell']
    for spr in sprites:
        SPRITES[spr[1:]] = SPRITES[spr].replace_colors(color_scheme)
        #thay đổi màu của mỗi màn chơi

def make_letters_sprite():
    #chọn tên 4 phím để chơi
    SPRITES['wasd'] = s = SPRITES['empty_wasd'].copy()
    letters = {v: k.replace('comma', '<').replace('period', '>').upper() for k, v in SAVED_SETTINGS['letters'].items()}
    if 'up' in letters:
        s.write(62, 10, letters['up'], size=20, font='cambria', col=(0, 0, 0), pos='.')
    if 'down' in letters:
        s.write(62, 50, letters['down'], size=20, font='cambria', col=(0, 0, 0), pos='.')
    if 'left' in letters:
        s.write(22, 50, letters['left'], size=20, font='cambria', col=(0, 0, 0), pos='.')
    if 'right' in letters:
        s.write(102, 50, letters['right'], size=20, font='cambria', col=(0, 0, 0), pos='.')


make_game_mode_sprites()
make_letters_sprite()
