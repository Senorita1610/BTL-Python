import sys
import pygame
import simplified_pygame
import game_modes as game
import tetris
import settings
from settings import SAVED_SETTINGS, ACTIVE_SETTINGS
import buttons
SCREEN=simplified_pygame.PyGameWindow(
    w=SAVED_SETTINGS['w'],#w=1200
    h=SAVED_SETTINGS['h'],#h=800
    caption='Tetris for two',
    use_icon=True,
    bg_color=ACTIVE_SETTINGS['color_scheme']['background'],#[230,230,230]
    default_font='cambria',
    resizable=True)
import sprites
def window_resize(w=1200, h=800):
    scale = min(w/600, h/400)
    screen_w = int(600 * scale)
    screen_h = int(400 * scale)
    screen_x0 = (w - screen_w) // 2
    screen_y0 = (h - screen_h) // 2
    SCREEN.set_game_resolution(w, h)
    SCREEN.y0 = screen_y0
    ACTIVE_SETTINGS['scale'] = scale
    ACTIVE_SETTINGS['size'] = int(10*scale)
    SAVED_SETTINGS['w'] = w
    SAVED_SETTINGS['h'] = h


class AppControlls(simplified_pygame.EventReaderAsClass):
    key_map = {'joy_start': 'space',
               'joy_back': 'escape'}

    def on_any_key(key):
        global GAME_STATE
        if key == 'escape':
            if GAME_STATE == 'menu':
                SCREEN.exit()
                #nếu đang ở menu mà ấn esc thì close game
            GAME_STATE = {
                'game': 'menu',
                'pause': 'menu',
                'settings': 'menu',
                'select_buttons': 'settings',
                'random_demo': 'settings'}[GAME_STATE]
            #nếu ấn esc mà đang ở game thì sẽ ra menu
        elif key == 'space':
            GAME_STATE = {
                'game': 'pause',
                'pause': 'game',
                'random_demo': 'settings'}.get(GAME_STATE, GAME_STATE)
            #nếu ấn space mà đang ở game thì sẽ tạm dừng
        else:
            GAME_STATE = {
                'pause': 'game',
                'random_demo': 'settings'}.get(GAME_STATE, GAME_STATE)
                #trạng thái game từ pause chuyển thành game

    def on_window_resize(w, h):
        window_resize(w, h)


# ==============================


def swap_menus():
    #chuyển từ menu sang settings và ngược lại
    global GAME_STATE
    GAME_STATE = {
        'menu': 'settings',
        'settings': 'menu'}[GAME_STATE]
    menu_page._mouse_pos = menu_page.buttons[-2]#vị trí button này gần cuối trong menu_page
    menu_settings._mouse_pos = menu_settings.buttons[-1]#vị trí button này ở cuối trong menu_settings


class GameSelector(buttons.ActionButton):
    def draw(self, W, size, scale, selected):
        #vẽ 1 hình chữ nhật màu vàng khi nhấn vào để chọn chế độ chơi
        super().draw(W, size, scale, selected)
        if selected:#nếu chọn
            #vẽ 1 hình chữ nhật màu vàng là hướng dẫn game
            # draw help
            x0 = size*26
            W.rect((x0, size*1, size*15, size*28), (255, 200, 100))
            W.sprite(x0+size*3, size*3, self.action.__name__, scale=scale/2)#tạo 1 surface hướng dẫn của 1 màn vào trong hướng dẫn
            #self.action.__name__ kiểu class simplified_pygame.Canvas
            W.write(x0, 10*size, "    "+self.text, font='cambria-bold', size=size)#viết đoạn text vào trong hướng dẫn
            W.write(x0, 10*size, str(self.action.__doc__), size=size)

    def on_mouse_click(self):
        global GAME
        global GAME_STATE
        GAME = self.action()
        GAME_STATE = 'pause'
        #khi click chuột vào 1 màn bất kỳ thì GAME_STATE='pause'


class ControllSwitch(buttons._Button):
    def __init__(self, ctr, w=14, h=5):
        #ctr: đoạn text
        self.ctr = ctr
        self.h = h
        self.w = w

    def draw(self, W, size, scale, selected):
        #W:SCREEN
        if selected:
            box = (self.x*size, (self.y+0.1)*size, self.w*size, self.h*size)
            W.rect(box, (255, 200, 100))
            #nếu di chuyển chuột vào vùng chọn phím (hình chữ nhật) thì vùng đó sẽ phát lên màu (255,200,100)

        if SAVED_SETTINGS[self.ctr]:
            W.sprite((self.x+7)*size, (self.y+0.5)*size, self.ctr, scale=scale/2)
            #vẽ chuột hoặc bàn phím bên phải, hình nằm trong 1 nửa box
            W.rect(((self.x+3)*size, (self.y+2)*size, size, size), col=SAVED_SETTINGS['color_scheme']['well'])
            #vẽ 1 ô vuông nhỏ màu trắng bên trái
        else:
            W.sprite((self.x+1)*size, (self.y+0.5)*size, self.ctr, scale=scale/2)
            #vẽ chuột hoặc bàn phím bên trái, hình nằm trong 1 nửa box
            W.rect(((self.x+10)*size, (self.y+2)*size, size, size), col=SAVED_SETTINGS['color_scheme']['well'])
            #vẽ 1 ô vuông nhỏ màu trắng bên phải

    def on_mouse_click(self):
        SAVED_SETTINGS[self.ctr] = not SAVED_SETTINGS[self.ctr]
        # guaranty there at least some controlls for everyone
        # đảm bảo rằng có ít nhất 1 điều khiển cho mỗi người
        if SAVED_SETTINGS['arrows'] == SAVED_SETTINGS['wasd'] == SAVED_SETTINGS['mouse']:
            #nếu 3 cái cùng True hoặc cùng False
            for i in 'arrows wasd mouse'.split():
                if i != self.ctr:
                    SAVED_SETTINGS[i] = not SAVED_SETTINGS[i]
                    #2 điều khiển còn lại sẽ bị đảo lại cùng True hoặc cùng False


class ControllSwitchJoy(ControllSwitch):
    def in_box(self, x, y):
        if SCREEN.joysticks_ids:
            return super().in_box(x, y)

    def draw(self, W, size, scale, selected):
        if len(SCREEN.joysticks_ids) == 1:
            return super().draw(W, size, scale, selected)
        elif len(SCREEN.joysticks_ids) > 1:
            if selected:
                box = (self.x*size, (self.y+0.1)*size, self.w*size, self.h*size)
                W.rect(box, (255, 200, 100))
            W.sprite((self.x+7.2)*size, (self.y+0.5)*size, self.ctr, scale=scale/2)
            W.sprite((self.x+0.2)*size, (self.y+0.5)*size, self.ctr, scale=scale/2)
            W.write((self.x+3.5)*size, (self.y+3.5)*size, str(SCREEN.joysticks_ids[SAVED_SETTINGS['controller']]), size=size, pos='.')
            W.write((self.x+10.5)*size, (self.y+3.5)*size, str(SCREEN.joysticks_ids[1-SAVED_SETTINGS['controller']]), size=size, pos='.')

       # else:
         #   W.write((self.x+7)*size, (self.y+2)*size, 'no controllers detected', size=size-2, pos='.', col=SAVED_SETTINGS['color_scheme']['well'])



menu_page = buttons.Menu()
menu_page.append(buttons.Title('Controlls:'), x=27, y=3)#nhãn
menu_page.append(buttons.Label('Left Player             Right Player'), dy=2)#nhãn

#phím và chuột cho người chơi 1 và người chơi 2
menu_page.append(ControllSwitch('arrows'),dy=2)#nút
menu_page.append(ControllSwitch('wasd'),dy=5)#nút
menu_page.append(ControllSwitch('mouse'),dy=5)#nút

#chọn phím và chuột
menu_page.append(ControllSwitchJoy('controller'),dy=5)#nút

menu_page.append(buttons.Title('Single Player:'), x=7, y=3)#nhãn cùng dòng với Title('Controlls')

menu_page.append(GameSelector('Single Player', game.TetrisGame), dy=1)#nút
menu_page.append(buttons.Title('Competition:'), dy=5)#nhãn
menu_page.append(GameSelector('Parallel Match', game.TetrisGame2Players), dy=1)#nút
menu_page.append(GameSelector('Mirror Match', game.TetrisGameMirror), dy=3)#nút
menu_page.append(GameSelector('Wrestling', game.TetrisGameWrestling), dy=3)#nút
menu_page.append(GameSelector('Speed-up', game.TetrisGameSpeedUp), dy=3)#nút
menu_page.append(buttons.Title('Cooperation:'), dy=5)#nhãn
menu_page.append(GameSelector('Control Swap', game.TetrisGameSwap), dy=1)#nút
menu_page.append(GameSelector('Balanced Wells', game.TetrisGameBalance), dy=3)#nút
menu_page.append(GameSelector('Common Well', game.TetrisGameCommonWell), dy=3)#nút
menu_page.append(GameSelector('Heart-shaped Well', game.TetrisHeartMode), dy=3)#nút
menu_page.append(buttons.BigActionButton('Settings', swap_menus), x=26, y=31)#nút
menu_page.append(buttons.BigActionButton('Exit', lambda : SCREEN.exit()), dy=4)#nút

# ==============================


def select_buttons():
    global GAME_STATE
    GAME_STATE = 'select_buttons'#chuyển trạng thái game
    MenuLetterSelector.selector = [
        ['left', 'press [move left]'],
        ['right', 'press [move right]'],
        ['down', 'press [move down]'],
        ['up', 'press [rotate]']]
    SAVED_SETTINGS['letters'] = {}


DEMO_SEQUENCE = []

def demonstrate_randomness():
    #hiển thị ra các hình khối ngẫu nhiên
    global GAME_STATE
    GAME_STATE = 'random_demo'
    rg = tetris.make_random_generator()
    DEMO_SEQUENCE[:] = [rg.draw() for i in range(138)]

def draw_random_demo():
    size = ACTIVE_SETTINGS['size']
    SCREEN.write(size, size, f'Figures generated with {SAVED_SETTINGS["randomness"].upper()} method.   Press any key to continue')
    for i, f in enumerate(DEMO_SEQUENCE):
        x0 = i%23 * 2.5 + 1
        y0 = i//23 * 6 + 5
        if f in 'srT': x0 += 1
        if f == '-': x0 += 0.5
        for y, x in tetris.FIGURE[f]:
            rect = ((x+x0)*size, (y+y0)*size+1, size-2, size-2)
            SCREEN.rect(rect, ACTIVE_SETTINGS['color_scheme'][f])


class MenuLetterSelector(simplified_pygame.EventReaderAsClass):
    #chọn nút nhấn từ bàn phím
    def draw(W):
        size = ACTIVE_SETTINGS['size']
        x0 = SCREEN.w // 2
        y0 = size*26
        with W.part(x0, y0, size*14, size*10, (0, 0, 0, 200)) as C:
            C.write(size*7, size*4, MenuLetterSelector.selector[0][1], col=(255, 255, 255), pos='.')
            #tạo 1 thông báo chọn nút nền đen, chữ trắng 

    @classmethod
    def on_any_key(cls, key):
        (action, _), *cls.selector = cls.selector#đọc nút được chọn từ bàn phím
        # activate saving
        letters = SAVED_SETTINGS['letters']
        letters[key] = action
        SAVED_SETTINGS['letters'] = letters

        sprites.make_letters_sprite()
        if not cls.selector:
            #nếu không chọn gì thì không thể cài đặt những cái khác
            global GAME_STATE
            GAME_STATE = 'settings'


class SetColorButton(buttons.SetButton):
    parameter = 'color_scheme'
    def post_activation(self):
        ACTIVE_SETTINGS['color_scheme'].update(self.value)#cập nhật giá trị màu nền mới
        start_title.__init__()#self.w=11,self.h=35,self.GAME=None
        sprites.make_game_mode_sprites()#thay đổi màu các màn
        SCREEN.bg_color=SAVED_SETTINGS['color_scheme']['background'],#cập nhật màu nền mới


class SetBleedButton(buttons.SmallSetButton):
    #Các khối hình có bị trộn màu hay không
    parameter = 'bleed'
    def post_activation(self):
        ACTIVE_SETTINGS['bleed'] = self.value#self.value: True hoặc False
        start_title.__init__()


class SetKeysButton(buttons.SetButton):
    parameter = 'letters'
    def post_activation(self):
        sprites.make_letters_sprite()
        #QWERT: {'left':'A','right':'D','up':'W','down':'S'}
        #AZERT: {'left':'Q','right':'D','up':'Z','down':'S'}
        #Dvorak: {'left':'E','right':'A','up':'<','down':'O'}
        #Colemak: {'left':'A','right':'S','up':'W','down':'R'}


class SetSoundButton(buttons.SmallSetButton):
    parameter = 'volume'
    def post_activation(self):
        simplified_pygame.mixer.volume = SAVED_SETTINGS['volume']


menu_settings=buttons.Menu()
menu_settings.append(buttons.Title('Color Scheme:'),y=3)#nhãn
menu_settings.append(SetColorButton('Default',settings.DEFAULT_COLORS),dy=1)#nút
menu_settings.append(SetColorButton('Piet Mondrian',settings.MONDRIAN_COLORS),dy=3)#nút
menu_settings.append(SetColorButton('Leonardo da Vinci',settings.LEONARDO_COLORS), dy=3)#nút
menu_settings.append(SetColorButton('John Everett Millais',settings.MILLAIS_COLORS), dy=3)#nút
menu_settings.append(SetColorButton('Vincent van Gogh',settings.VAN_GOGH_COLORS), dy=3)#nút
menu_settings.append(SetColorButton('Gustav Klimt',settings.KLIMT_COLORS), dy=3)#nút

menu_settings.append(buttons.Title('Color blending effect:'), dy=5)
menu_settings.append(SetBleedButton('Off', False), dy=1)
menu_settings.append(SetBleedButton('On', True), dx=4)


menu_settings.append(buttons.Title('Screen:'), dx=-4, dy=5)
menu_settings.append(buttons.ActionButton('Reset Screen Size', window_resize), dy=1)


menu_settings.append(buttons.Title('Keyboard Layout:'), x=14, y=3)
menu_settings.append(SetKeysButton('QWERT', simplified_pygame.WASD_AS_ARROWS), dy=1)
menu_settings.append(SetKeysButton('AZERT', simplified_pygame.ZQSD_AS_ARROWS), dy=3)
menu_settings.append(SetKeysButton('Dvorak', simplified_pygame.AOE_AS_ARROWS), dy=3)
menu_settings.append(SetKeysButton('Colemak', simplified_pygame.WARS_AS_ARROWS), dy=3)

menu_settings.append(buttons.Sprite('wasd'), dx=1, dy=4)#vẽ bàn phím wasd lên SCREEN
menu_settings.append(buttons.ActionButton('Configure Buttons...', select_buttons), dx=-1, dy=5)#Chọn phím tùy thích

menu_settings.append(buttons.Title('Sound:'), x=14, y=30)#âm lượng
menu_settings.append(SetSoundButton('Off', 0), dy=1)
menu_settings.append(SetSoundButton('1/2', 1/2), dx=3, dy=0)
menu_settings.append(SetSoundButton('On', 1), dx=3, dy=0)


menu_settings.append(buttons.Title('Figures Cast Shadows:'), x=28, y=3)
menu_settings.append(buttons.SmallSetButton('Yes', True, 'shadow'), dy=1)
menu_settings.append(buttons.SmallSetButton('No', False, 'shadow'), dx=4)

menu_settings.append(buttons.Title('Generating New Figures:'), dx=-4, dy=5)
menu_settings.append(SetKeysButton('True Random', 'true random', 'randomness'), dy=1)
menu_settings.append(SetKeysButton('Fair Random', 'fair random', 'randomness'), dy=3)
menu_settings.append(SetKeysButton('Regularized', 'regularized', 'randomness'), dy=3)
menu_settings.append(buttons.ConditionalText('randomness', {
    'true random': 'True random may seem unfair,\nfigures have a significant change of \nrepeating or missing for a long time.',
    'fair random': 'Chance of bad sequence \nis reduced compared \nto the true random.',
    'regularized': 'Every figure appears once in \nseven turns; figures \nnever repeat.'}
    ), dy=4)
menu_settings.append(buttons.ActionButton('Demonstrate...', demonstrate_randomness), dy=3)


menu_settings.append(buttons.BigActionButton('Back', swap_menus), x=26, y=31)


# ==============================


def draw_pause(W):
    size = ACTIVE_SETTINGS['size']
    with W.part(0, W.h//2 - size*5, W.w, size*11, (0, 0, 0, 200)) as C:#tạo 1 surface màu đen và bị mờ đủ để thấy được game
        C.write(W.w//2, size*2, 'PAUSE', size=int(2.5*size), col=[255]*3, pos='.')
        C.write(W.w//2, size*7, 'Press any key to continue', size=int(0.7*size), col=[255]*3, pos='.')
        
        if SCREEN.joysticks_ids:
            C.write(W.w//2, size*8, 'Kayboard: Press [esc] to return, [space] for pause', size=int(0.7*size), col=[255]*3, pos='.')
            C.write(W.w//2, size*9, 'Controller: Press [back/select] to return, [start] for pause', size=int(0.7*size), col=[255]*3, pos='.')
        else:
            C.write(W.w//2, size*8, 'Press [esc] to return, [space] for pause', size=int(0.7*size), col=[255]*3, pos='.')


GAME = None
GAME_STATE = "menu"

window_resize(SCREEN.w, SCREEN.h)
simplified_pygame.mixer.volume = SAVED_SETTINGS['volume']#0.5
start_title = tetris.StartTitle()


for events, time_passed, pressed_keys in SCREEN.main_loop(framerate=600):
    AppControlls.read_events(events, time_passed, pressed_keys)
    #event:
    #[] không di chuyển chuột và không nhấn bàn phím
    #[('mouse_move','mouse',(x,y))]: di chuyển chuột
    #[('mouse_click','mouse',(x,y))]: click chuột
    #[('escape','key')]: nhấn esc để thoát ra ngoài
    #[('up','key')]: nhấn phím có mũi tên đi lên
    #[('down','key')]: nhấn phím có mũi tên đi xuống
    #[('left','key')]: nhấn phím có mũi tên sang trái
    #[('right','key')]: nhấn phím có mũi tên sang phải
    #[('xâu','key')]: nhấn phím có tên là xâu đó
    #xâu: tab,capslock,lshift,lctrl,lsuper,...

    #time_passed: số mili giây thực hiện 1 event
    
    #pressed_keys:
    #set(): chưa phím nào được bấm
    #{'1 ký tự'}: 1 phím được bấm
    #set gồm nhiều ký tự: tổ hợp phím được bấm
    
    #điều khiển sự kiện
    if GAME_STATE == 'game':
        GAME.read_events(events, time_passed, pressed_keys)
        #GAME có kiểu là <class 'game_modes.TetrisGame'>
        #action: game_modes.TetrisGame
    elif GAME_STATE == 'menu':
        menu_page.read_events(events, time_passed, pressed_keys)
        start_title.read_events(events, time_passed, pressed_keys)
    elif GAME_STATE == 'settings':
        menu_settings.read_events(events, time_passed, pressed_keys)
        start_title.read_events(events, time_passed, pressed_keys)
    elif GAME_STATE == 'select_buttons':
        MenuLetterSelector.read_events(events, time_passed, pressed_keys)


    if GAME_STATE == 'game':
        GAME.draw_game(SCREEN)
    elif GAME_STATE == "pause":
        GAME.draw_game(SCREEN)
        draw_pause(SCREEN)
    elif GAME_STATE == "menu":
        #vẽ start_title lên SCREEN
        start_title.draw(SCREEN)
        #vẽ các nút,title,label lên SCREEN
        menu_page.draw(SCREEN)
    elif GAME_STATE == "settings":
        start_title.draw(SCREEN)#vẽ start_title lên SCREEN
        menu_settings.draw(SCREEN)
    elif GAME_STATE == "select_buttons":
        start_title.draw(SCREEN)
        menu_settings.draw(SCREEN)
        MenuLetterSelector.draw(SCREEN)
    elif GAME_STATE == "random_demo":
        draw_random_demo()
print('GAME OVER')
