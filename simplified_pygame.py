import os
import sys
import json
import pygame
import pygame.locals as pygame_locals
__version__ = '1.5'
## ---------------------------------------------------------------------------
## Initialization functions
## ---------------------------------------------------------------------------
SPRITES: dict[str, 'Canvas'] = {}
SOUNDS: dict[str, pygame.mixer.Sound] = {}
FONTS: dict[tuple, pygame.font.Font] = {}
def assets_path(filename, folder='assets'):
    if getattr(sys, 'frozen', False):
    #
        datadir = os.path.dirname(sys.executable)
    #os.path.dirname lấy tên thư mục từ đường dẫn chỉ định
    #/home/User/Documents -> /home/User
    #/home/User/Documents/file.txt -> /home/User/Documents
    #file.txt -> không lấy được tên
    #sys.executable: Một chuỗi cung cấp đường dẫn tuyệt đối của tệp nhị phân thực thi cho trình thông dịch Python
    #Nếu Python không thể truy xuất đường dẫn thực đến tệp thực thi của nó, sys.executable sẽ là một chuỗi trống hoặc None.
    else:
        datadir = os.path.dirname(__file__)
        #Lấy đường dẫn đến tên thư mục chứa file simplified_pygame.py
        #/.../simplified_pygame.py -> /...
    return os.path.join(datadir, folder, filename)
    #os.path.join để nối đường dẫn trong python datadir,folder,filename -> datadir/folder/filename
    #Hàm không có tác dụng kiểm tra đường dẫn có tồn tại hay không
def _get_sprite(sprite_name):
    if sprite_name not in SPRITES:
        SPRITES[sprite_name] = Canvas.load(assets_path(sprite_name.removesuffix('.png')+'.png'))
    return SPRITES[sprite_name]
    #trả về Surface như hình ảnh .png trong folder assets
def _get_sound(sound_name):
    if sound_name not in SOUNDS:
        path = assets_path(sound_name)
        if os.path.exists(path.removesuffix('.wav')+'.wav'):
        #os.path.exists: kiểm tra đường dẫn có tồn tại hay không
        #removesuffix: xóa bỏ hậu tố trong xâu nếu tồn tại
            SOUNDS[sound_name] = pygame.mixer.Sound(path.removesuffix('.wav')+'.wav')
        elif os.path.exists(path.removesuffix('.mp3')+'.mp3'):
            SOUNDS[sound_name] = pygame.mixer.Sound(path.removesuffix('.mp3')+'.mp3')
        else:
            #Nếu không phải wav hoặc mp3 thì trả về 1 ngoại lệ
            raise Exception('sound or music file not found: f{path.removesuffix(".wav")+".wav"} or f{path.removesuffix(".mp3")+".mp3"}')
    return SOUNDS[sound_name]
    #Trả về đối tượng Sound
def _get_font(font_name, size, bold=False, italic=False):
    name_tuple = (font_name, size, bold, italic)
    if name_tuple in FONTS: #nếu tuple thuộc FONTS
        pass
    else:
        font_path = None if font_name is None else assets_path(font_name.removesuffix('.ttf')+'.ttf')
        #đường dẫn đến file font_name.ttf trong thư mục assets
        FONTS[name_tuple] = pygame.font.Font(font_path, size, bold=bold, italic=italic)
        #FONTS[name_tuple]=1 đối tượng Font
    return FONTS[name_tuple]


def init_pygame(caption, use_icon):
    pygame.init()
    #khởi tạo tất cả các modules pygame
    os.environ['SDL_VIDEO_WINDOW_POS'] = '50,50'
    #đặt vị trí cửa sổ game
    info = pygame.display.Info()
    #tạo 1 đối tượng info chứa 1 số thuộc tính để mô tả môi trường đồ họa hiện tại
    pygame.display.set_caption(caption)
    #đặt tên cho cửa sổ game
    if use_icon:
        icon = pygame.image.load(assets_path('icon.ico'))
        pygame.display.set_icon(icon)
    return info

def exit_pygame():
    pygame.quit()
    sys.exit()


## ---------------------------------------------------------------------------
## Canvas
## ---------------------------------------------------------------------------
## Canvas object contains pygame.Surface, simplifying access to some basic drawing


class Canvas():
    #Constructer của class Canvas
    def __init__(self, w, h, dx=0, dy=0, default_font=None):
        self.surface = pygame.Surface((w, h))
        #chiều rộng: w, chiều dài: h
        self.surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
        #pygame.RLEACCEL: cung cấp hiệu suất tốt hơn trên màn hình không tăng tốc
        self.x0 = dx
        self.y0 = dy
        self.default_font = default_font

    @classmethod
    def from_pygame_surface(cls, surface):
        new = Canvas.__new__(Canvas)
        #__new__ là 1 phương thức tĩnh yêu cầu chuyển 1 tham số cls, đại diện cho lớp cần được khởi tạo
        new.surface = surface
        new.x0 = new.y0 = 0
        new.default_font = None
        return new

    @classmethod
    def load(cls, filename, corner_alpha=False):
        new = Canvas.from_pygame_surface(pygame.image.load(filename))
        #pygame.image.load: tải hình ảnh mới từ tệp
        #load(filename) -> Surface
        if corner_alpha:
            new.surface = new.surface.convert_alpha()
            #convert_alpha(): tạo 1 bản sao bề mặt với định dạng pixel mong muốn
            #được tối ưu hóa để chuyển sang màn hình hiện tại
            new.surface.set_colorkey(new.surface.get_at((0, 0)), pygame.RLEACCEL)
            #surface.get_at nhận giá trị màu ở 1 pixel duy nhất
        return new

    #Lưu Canvas vào tệp đã đặt tên
    def save(self,filename):
        pygame.image.save_extended(self.surface, filename)
        #Lưu Surface dưới dạng ảnh png hoặc jpeg
        
    #Thêm (dx,dy) pixel
    def with_offset(self,dx,dy):
        new = Canvas.__new__(Canvas)
        new.surface = self.surface
        new.x0 = self.x0 + dx
        new.y0 = self.y0 + dy
        new.default_font = self.default_font
        return new

    #Chia tách 1 phần của surface. Dùng để cấp phát và sử dụng tài nguyên 1 cách hiệu quả
    def part(self, x, y, w, h, bg_col=(0, 0, 0, 0)):
        return _CanvasContext(x, y, w, h, bg_col, parent=self)
    def layer(self, bg_col=(0, 0, 0, 0)):
        return _CanvasContext(0, 0, self.w, self.h, bg_col, parent=self)

    def _writeln(self, x, y, s, font_object, col=(100, 100, 100), border=False, vert=False):

        #Nếu muốn bôi đậm thì lấy 4 cái txt đè lên nhau (đông,tây,nam,bắc)
        if border:
            txt = font_object.render(s, True, (0, 0, 0))
            #font_object: 1 đối tượng font
            #text s: chỉ 1 dòng duy nhất, các ký tự dòng mới không được hiển thị
            #True: các ký tự nhẵn, không có răng cưa
            #(0,0,0) là màu của text s
            #tạo 1 đối tượng Surface txt từ text s, màu chữ đen
            self.blit(txt, x-1, y)
            self.blit(txt, x,   y-1)
            self.blit(txt, x+1, y)
            self.blit(txt, x,   y+1)
        txt = font_object.render(s, True, col)
        #col: màu dove gray
        #Nếu tạo đoạn text theo chiều dọc
        if vert:
            txt = pygame.transform.rotate(txt, 90)
            #xoay đối tượng txt 90 độ ngược chiều kim đồng hồ
        self.blit(txt, x, y)

    #ghi đoạn text s lên surface nằm ở vị trí (x,y)
    def write(self, x, y, s, font=None, size=20, col=(0, 0, 0), pos='>', border=False, bold=False, italic=False):
        """ Write text """
        if font is None:
            font = self.default_font
        font_object = _get_font(font, int(size), bold=bold, italic=italic)
        for line in s.split('\n'):
            w = font_object.size(line)[0]
            #.size: kích thước cần thiết để hiển thị text, [0] lấy chiều rộng
            x1 = x - {'>': 0, '.': w//2, '<': w}[pos]
            self._writeln(x1, y, line, font_object=font_object, col=col, border=border)
            y += font_object.size(line)[1]
            #[1] lấy chiều cao

    def write_vert(self, x, y, s, font=None, size=20, col=(0, 0, 0), pos='>', border=False, bold=False, italic=False):
        """ Write vertical text"""
        #Viết text theo chiều dọc
        if font is None:
            font = self.default_font
        font_object = _get_font(font, int(size), bold=bold, italic=italic)
        for line in s.split('\n'):
            w = font_object.size(line)[0]
            y1 = y - {'>': 0, '.': w//2, '<': w}[pos]
            self._writeln(x, y1, line, font_object, col, vert=True)
            x += font_object.size(line)[1]


    ## reimplement some pygame drawing routines
    ## ----------------------------------------
    ## hiện thực lại 1 số hàm vẽ trong pygame

    def rect(self, coords, col):
        #col: màu
        x, y, w, h = coords
        if w < 0: x += w; w *= -1
        if h < 0: y += h; h *= -1
        if col is None:
            return
        pygame.draw.rect(self.surface, [int(c) for c in col], (x+self.x0, y+self.y0, w, h))
        #(x+self.x0, y+self.y0, w, h): tọa độ x,y và chiều rộng,chiều cao
        #Vẽ 1 hình chữ nhật có màu col
    def box(self, coords, col):
        x, y, w, h = coords
        if col is None:
            return
        self.lines([x, x+w-1, x+w-1, x, x], [y, y, y+h-1, y+h-1, y], col=col)
        #tạo hình chữ nhật có các cạnh có màu col bọc xung quanh

    def line(self, coords, col, width):
        x, y, w, h = coords
        if col is None:
            return
        pygame.draw.line(self.surface, [int(c) for c in col], start_pos=(x+self.x0, y+self.y0), end_pos=(w+x+self.x0, h+y+self.y0), width=width)
        #start_pos,end_pos: điểm bắt đầu và điểm kết thúc
        #width: độ dày của đoạn thẳng

    def lines(self, X, Y, col, width=1):
        if col is None or len(X) < 2 or len(Y) < 2:
            return
        pygame.draw.lines(self.surface, [int(c) for c in col], False, [(x+self.x0, y+self.y0) for x, y in zip(X, Y)], width)
        #False: không vẽ đoạn thẳng giữa điểm đầu và điểm cuối
        #[(x+self.x0, y+self.y0) for x, y in zip(X, Y)]: chuỗi gồm nhiều tọa độ các điểm (x,y), các điểm liền kề nối với nhau bằng 1 đoạn thẳng
        #width: độ dày của đoạn thẳng

    def circle(self, coords, r, col, width=0):
        if col is None:
            return
        x, y = coords
        pygame.draw.circle(self.surface, center=(x+self.x0, y+self.y0), radius=r, color=col, width=width)
        #center: tâm hình tròn
        #radius: bán kính hình tròn 
        #color: màu đường tròn
        #width=0: phủ kín hình tròn bằng màu col
        #width>0: chỉ tô màu đường tròn
        #width<0: không tô màu cho cả hình tròn

    def fill(self, col):
        self.surface.fill(col)
        #phủ kín surface bằng màu col

    def sprite(self, x, y, sprite, scale=1):
        if isinstance(sprite, pygame.Surface):
            pass
        elif isinstance(sprite, Canvas):
            sprite = sprite.surface
        else:
            sprite = _get_sprite(sprite)
            if isinstance(sprite, Canvas):
                sprite = sprite.surface
        if scale != 1:
            final_size = int(sprite.get_size()[0]*scale), int(sprite.get_size()[1]*scale)
            sprite = pygame.transform.scale(sprite, final_size).convert_alpha()
        self.blit(sprite, x, y)
    def blit(self, surface, x, y):
        self.surface.blit(surface, (self.x0 + x, self.y0 + y))
    def stack(self, sprite, x=0, y=0):
        new = self.copy()
        new.blit(sprite.surface, x, y)
        return new

    def crop(self, x, y, w, h):
        return Canvas.from_pygame_surface(self.surface.subsurface((x+self.x0, y+self.y0, w, h)).copy())
        #tạo 1 bản sao surface có cùng kích thước nhưng khác điểm bắt đầu
    def rotate(self, angle):
        return Canvas.from_pygame_surface(pygame.transform.rotate(self.surface, angle).copy())
        #xoay surface ngược chiều kim đồng hồ
    def flip(self, vertical_flip, horizontal_flip):
        return Canvas.from_pygame_surface(pygame.transform.flip(self.surface, vertical_flip, horizontal_flip).copy())
        #lật hình ảnh theo chiều dọc hoặc chiều ngang với kích thước không đổi
        #vertical_flip: chiều dọc (boolean)
        #horizontal_flip: chiều ngang (boolean)
    def copy(self):
        return Canvas.from_pygame_surface(self.surface.copy())
        #tạo 1 bản sao surface
    def set_alpha(self, *args):
        self.surface.set_alpha(*args)
        #các pixel sẽ được vẽ hơi trong suốt
        return self

    def add_outline(self, col=(0, 0, 0)):
        img = self.surface.copy()
        key = img.get_colorkey() if img.get_colorkey() else (157, 112, 170, 0)
        #Trả về màu hiện tại của surface
        #Nếu colorkey chưa được đặt thì key=(157,112,170,0)
        substance = set()
        #chứa các tuple khác (0,0) và (157,112) và khác nhau
        for x in range(img.get_width()):
            for y in range(img.get_height()):
                c = img.get_at((x, y))
                #trả về màu RGBA tại pixel x,y
                if c != key and c[:3] != col:
                    substance.add((x, y))
        neighbours = set()
        #chứa các tuple khác substance và khác nhau
        for x, y in substance:
            for dx, dy in (-1, 0), (1, 0), (0, 1), (0, -1):
                neighbours.add((x+dx, y+dy))
        neighbours -= substance
        for x, y in neighbours:
            img.set_at((x, y), col)
            #Đặt lại thành màu col cho pixel x,y
        return Canvas.from_pygame_surface(img)

    #Thay thế màu tại pixel x,y
    def replace_colors(self, mapping):
        img = self.surface.copy()
        for x in range(img.get_width()):
            for y in range(img.get_height()):
                c = self.surface.get_at((x, y))
                if c[:3] in mapping:
                    img.set_at((x, y), mapping[c[:3]])
        return Canvas.from_pygame_surface(img)

    @property
    def w(self): return self.surface.get_size()[0]
    #chiều rộng surface
    @property
    def h(self): return self.surface.get_size()[1]
    #chiều cao surface

    def __repr__(self):
        return f'sprite {self.w}x{self.h}'
        #in ra kích thước

class _CanvasContext(Canvas):
    def __init__(self, x, y, w, h, bg_col, parent):
        self.surface = pygame.Surface((w, h), pygame_locals.SRCALPHA)
        #Thêm pixel alpha vào surface
        self.surface.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
        #Đặt màu hiện tại cho surface
        self.x0 = parent.x0
        self.y0 = parent.y0
        self.default_font = parent.default_font
        self._offset = (x, y)
        self._parent = parent
        self.fill(bg_col)
        #Toàn bộ surface được tô bằng màu bg_col RGBA
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._parent.surface.blit(self.surface, self._offset)
        #vẽ self.surface lên 1 surface khác, vị trí vẽ là self._offset


## ---------------------------------------------------------------------------
## Sounds
## ---------------------------------------------------------------------------


class _Mixer():
    def __init__(self):
        self._on = True
        self.volume = 0.5
        self.music_channels = {}

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, val):
        self._on = val
        if val:
            pygame.mixer.unpause()
            #tiếp tục phát lại các âm thanh bị tạm dừng
        else:
            pygame.mixer.pause()
            #tạm thời dừng phát lại tất cả âm thanh

    def play_sound(self, name, volume=1, repeat=0):
        if self.on:
            sound = _get_sound(name)
            sound.play(repeat)
            #repeat=0: âm thanh chỉ được phát 1 lần và không lặp lại
            sound.set_volume(volume*self.volume)
            #đặt lại âm lương trong khoảng 0.0 đến 1.0
            #nếu giá trị < 0.0, âm lượng sẽ không bị thay đổi
            #nếu giá trị > 1.0, âm lượng sẽ được đặt thành 1.0
    
    def play_music(self, name, volume=1, channel=1):
        if self.on:
            if channel in self.music_channels:
                if name == self.music_channels[channel][0]:
                    # music already playing
                    music = self.music_channels[channel][1]
                    music.set_volume(volume*self.volume)
                    return
                else:
                    # channel exists, but other music is playing
                    music = self.music_channels[channel][1]
                    music.stop()
                    #dừng phát nhạc để bật nhạc khác
            # load music
            music = _get_sound(name)
            self.music_channels[channel] = name, music
            music.play(-1)
            #nhạc lặp lại vô hạn
            music.set_volume(volume*self.volume)

    def stop_music(self, name, channel=None):
        self.music_slots[name, channel].stop()



mixer = _Mixer()

play_sound = mixer.play_sound
play_music = mixer.play_music
stop_music = mixer.stop_music


## ---------------------------------------------------------------------------
## Main Window
## ---------------------------------------------------------------------------


MAIN_WINDOW = None
_MAX_TIME_PASSED = 10000


class PyGameWindow(Canvas): #kế thừa từ lớp Canvas
    #h,w: chiều rộng và chiều cao của cửa sổ
    #use_icon: có load 'icon.ico' từ thư mục asserts hay không
    #on_exit: hàm để chạy khi nút exit button (thoát game) trên cửa sổ được bấm vào
    #bg_color: màu background
    #default_font: font được sử dụng
    #resizable: có thay đổi kích thước cửa sổ hay không
    def __init__(self, w, h, *, caption='my game', use_icon=False, on_exit=exit_pygame, bg_color=(0, 0, 0), default_font=None, resizable=False):
        global MAIN_WINDOW
        if MAIN_WINDOW is None:
            MAIN_WINDOW = self
        else:
            raise Exception('Window already created')

        # init python
        info = init_pygame(caption, use_icon)
        #info: VideoInfo(hw = 0, wm = 1,video_mem = 0
        #blit_hw = 0, blit_hw_CC = 0, blit_hw_A = 0,
        #blit_sw = 0, blit_sw_CC = 0, blit_sw_A = 0,
        #bitsize  = 32, bytesize = 4,
        #masks =  (16711680, 65280, 255, 0),
        #shifts = (16, 8, 0, 0),
        #losses =  (0, 0, 0, 8),
        #current_w = 1280, current_h = 720
        #use_icon==False: chưa hiển thị 'icon.ico'
        self._fullscreen_res=(info.current_w, info.current_h)
        #info.current_w, info.current_h: chiều cao và chiều rộng của cửa sổ game hiện tại
        # init the window
        self.fullscreen=False
        self._pygame_flags=pygame.RESIZABLE if resizable else 0
        #cờ flags cho phép thay đổi kích thước
        self.current_res=1
        self.set_game_resolution(w,h)
        self.x0=0
        self.y0=0
        self.default_font=default_font
        self.exit=on_exit
        self.bg_color=bg_color
        self.joysticks_ids=[]
    def update_screen(self):
        if self.scale == 1:
            scaled = self.surface
        else:
            scaled = pygame.transform.scale(self.surface, (self.screen_w, self.screen_h))
        self.screen0.blit(scaled, (self.screen_x0, self.screen_y0))
        pygame.display.flip()
        self.surface.fill(self.bg_color)

    #đặt lại độ phân giải trò chơi. Chuột và hình vẽ xảy ra liên quan đến độ phân giải trò chơi
    def set_game_resolution(self,w,h):
        self.surface = pygame.Surface((w,h))
        #tạo 1 surface dài w pixel và cao h pixel
        self.set_window_resolution(self.current_res)

    #đặt lại độ phân giải của cửa sổ game. Cửa sổ game và surface trò chơi có kích thước tỉ lệ
    def set_window_resolution(self, new_res):
        self.current_res = new_res
        # unpack parameters
        if isinstance(new_res, (int, float)):
            #kiểm tra new_res có là int hoặc float
            #scale>=1
            fullscreen = False
            self.scale = scale = new_res
            w, h = self.w * scale, self.h * scale
            #w,h: kích thước cửa sổ game
            #self.w,self.h: kích thước trò chơi
            self.screen_x0 = self.screen_y0 = 0
            self.screen_w = self.display_w = w
            self.screen_h = self.display_h = h
        else:
            if new_res == 'fullscreen':
                fullscreen = True
                w, h = self._fullscreen_res
            elif isinstance(new_res, (list, tuple)):
                fullscreen = False
                w, h = new_res
            else:
                raise KeyError('Wrong resolution given: ', str(new_res))

            # compute screen's scale compared to game screen
            self.scale = scale = min(w/self.w, h/self.h)
            self.screen_w = int(self.w * scale)
            self.screen_h = int(self.h * scale)
            self.screen_x0 = (w - self.screen_w) // 2
            #trò chơi bắt đầu từ tọa độ self.screen_x0
            self.screen_y0 = (h - self.screen_h) // 2
            #trò chơi bắt đầu từ tọa độ self.screen_y0
            self.display_w = w
            self.display_h = h

        if self.fullscreen and not fullscreen:
            pygame.display.toggle_fullscreen()
            self.screen0 = pygame.display.set_mode((w, h), flags=self._pygame_flags)
        elif not self.fullscreen and fullscreen:
            self.screen0 = pygame.display.set_mode((w, h), flags=self._pygame_flags)
            pygame.display.toggle_fullscreen()
        elif not self.fullscreen and not fullscreen:
            self.screen0 = pygame.display.set_mode((w, h), flags=self._pygame_flags)

        self.fullscreen = fullscreen

    def save(self, filename):
        # need to reload this function to use .screen0 instead of .surface
        pygame.image.save_extended(self.screen0, filename)

    def main_loop(self, framerate):
        Clock = pygame.time.Clock()
        #Được sử dụng để quản lý tốc độ cập nhật màn hình
        pressed_keys = set()
        # joystick_position = [0, 0, 0, 0]

        pygame.joystick.init()
        #Khởi tạo module joystick
        n_joysticks = pygame.joystick.get_count()
        #Trả về số lượng thiết bị cần điều khiển trên hệ thống
        __joysticks = [pygame.joystick.Joystick(x) for x in range(n_joysticks)]
        self.joysticks_ids = [joy.get_instance_id()+1 for joy in __joysticks]
        #id của joy

        while True:
            time_passed = Clock.tick(framerate)
            #Phương thức này nên được gọi một lần trên mỗi khung hình. Nó sẽ tính toán bao nhiêu mili giây đã trôi qua kể từ lần gọi trước.
            time_passed = min(time_passed, _MAX_TIME_PASSED) #_MAX_TIME_PASSED: 10000
            pygame_events = pygame.event.get()
            #Đây là một hàm sẽ trả về danh sách các sự kiện có thể được xử lý lần lượt
            events = []

            # Translate the list of pygame events into human-readable form
            for event in pygame_events:
                try:
                    # system events
                    if event.type == pygame_locals.QUIT:
                        self.exit()
                    elif event.type == pygame_locals.VIDEORESIZE:
                        #VIDEORESIZE: thay đổi kích thước cửa sổ pygame và surface trong nó
                        events.append(('window_resize', 'sys', event.w, event.h))
                    elif event.type in (pygame_locals.JOYDEVICEADDED, pygame_locals.JOYDEVICEREMOVED):
                        # reinit Joistics (khởi tạo lại)
                        n_joysticks = pygame.joystick.get_count()
                        __joysticks = [pygame.joystick.Joystick(x) for x in range(n_joysticks)]
                        self.joysticks_ids = [joy.get_instance_id()+1 for joy in __joysticks]

                    # keyboard
                    elif event.type == pygame_locals.KEYDOWN:
                        #KEYDOWN: nút bàn phím được nhấn
                        key = _KEY_MAPPING[event.key]
                        pressed_keys.add(key)#thêm key
                        events.append((key, 'key'))
                    elif event.type == pygame_locals.KEYUP:
                        #KEYUP: nút bàn phím được thả
                        key = _KEY_MAPPING[event.key]
                        pressed_keys.discard(key)#xóa bỏ key

                    # joystick
                    elif event.type == pygame_locals.JOYBUTTONDOWN:
                        key = _JOYSTICK_MAPPING[event.button]
                        joy = event.instance_id+1
                        pressed_keys.add((key, joy))
                        events.append((key, 'joy', joy))
                    elif event.type == pygame_locals.JOYBUTTONUP:
                        key = _JOYSTICK_MAPPING[event.button]
                        joy = event.instance_id+1
                        pressed_keys.discard((key, joy))

                    #lên,xuống,sang trái,sang phải
                    elif event.type == pygame_locals.JOYHATMOTION:
                        joy = event.instance_id+1
                        for dp_pos, dp_value, key in (0, 1, 'right'), (0, -1, 'left'), (1, 1, 'up'), (1, -1, 'down'):
                            if event.value[dp_pos] == dp_value:
                                events.append(('dpad_'+key, 'joy', joy))
                                pressed_keys.add(('dpad_'+key, joy))
                            else:
                                pressed_keys.discard(('dpad_'+key, joy))

                    #elif event.type == pygame_locals.JOYAXISMOTION:
                        #joystick_position[event.axis] = event.value

                    #xử lý chuột
                    # mouse
                    #event.button: 1-left click, 2-middle click, 3-right click, 4-scroll up, 5-scroll down
                    elif event.type in (pygame_locals.MOUSEBUTTONDOWN, pygame_locals.MOUSEBUTTONUP, pygame_locals.MOUSEMOTION):#click, thả và di chuyển chuột
                        pos_x = (event.pos[0] - self.screen_x0) / self.scale
                        pos_y = (event.pos[1] - self.screen_y0) / self.scale
                        if event.type == pygame_locals.MOUSEBUTTONDOWN and event.button in _MOUSE_MAPPING:
                            key = _MOUSE_MAPPING[event.button]
                            events.append((key, 'mouse', (pos_x, pos_y)))
                            pressed_keys.add(key)
                        elif event.type == pygame_locals.MOUSEBUTTONUP and event.button in _MOUSE_MAPPING:
                            key = _MOUSE_MAPPING[event.button]
                            pressed_keys.discard(key)
                        elif event.type == pygame_locals.MOUSEMOTION:
                            events.append(('mouse_move', 'mouse', (pos_x, pos_y)))
                except KeyError:
                    # currently, not all pygame event keys are presented here
                    pass

            yield events, time_passed, pressed_keys

            # update window
            self.update_screen()


## ---------------------------------------------------------------------------
## EVENT READER
## ---------------------------------------------------------------------------


_KEY_MAPPING = {
    getattr(pygame_locals, k): k[2:].lower() for k in pygame_locals.__all__ if k.startswith('K_')}
    #k[2:].lower() for k in pygame_locals.__all__ if k.startswith('K_'): lấy các phím trên bàn phím máy tính

#_KEY_MAPPING={48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
#1073742094: 'ac_back', 38: 'ampersand', 42: 'asterisk', 64: 'at', 96: 'backquote', 92: 'backslash', 8: 'backspace', 1073741896: 'pause',
#1073741881: 'capslock', 94: 'caret', 1073741980: 'clear', 58: 'colon', 44: 'comma', 1073742005: 'currencysubunit', 1073742004: 'euro',
#127: 'delete', 36: 'dollar', 1073741905: 'down', 1073741901: 'end', 61: 'equals', 27: 'escape', 33: 'exclaim', 1073741882: 'f1',
#1073741891: 'f10', 1073741892: 'f11', 1073741893: 'f12', 1073741928: 'f13', 1073741929: 'f14', 1073741930: 'f15', 1073741883: 'f2',
#1073741884: 'f3', 1073741885: 'f4', 1073741886: 'f5', 1073741887: 'f6', 1073741888: 'f7', 1073741889: 'f8', 1073741890: 'f9',
#62: 'greater', 35: 'hash', 1073741941: 'help', 1073741898: 'home', 1073741897: 'insert', 1073741922: 'kp_0', 1073741913: 'kp_1',
#1073741914: 'kp_2', 1073741915: 'kp_3', 1073741916: 'kp_4', 1073741917: 'kp_5', 1073741918: 'kp_6', 1073741919: 'kp_7', 1073741920: 'kp_8',
#1073741921: 'kp_9', 1073741908: 'kp_divide', 1073741912: 'kp_enter', 1073741927: 'kp_equals', 1073741910: 'kp_minus',
#1073741909: 'kp_multiply', 1073741923: 'kp_period', 1073741911: 'kp_plus', 1073742050: 'lalt', 1073742048: 'lctrl', 1073741904: 'left',
#91: 'leftbracket', 40: 'leftparen', 60: 'less', 1073742051: 'lsuper', 1073742049: 'lshift', 1073741942: 'menu', 45: 'minus',
#1073742081: 'mode', 1073741907: 'numlockclear', 1073741902: 'pagedown', 1073741899: 'pageup', 37: 'percent', 46: 'period', 43: 'plus',
#1073741926: 'power', 1073741894: 'printscreen', 63: 'question', 39: 'quote', 34: 'quotedbl', 1073742054: 'ralt', 1073742052: 'rctrl',
#13: 'return', 1073742055: 'rsuper', 1073741903: 'right', 93: 'rightbracket', 41: 'rightparen', 1073742053: 'rshift', 1073741895: 'scrollock',
#59: 'semicolon', 47: 'slash', 32: 'space', 1073741978: 'sysreq', 9: 'tab', 95: 'underscore', 0: 'unknown', 1073741906: 'up',
#97: 'a', 98: 'b', 99: 'c', 100: 'd', 101: 'e', 102: 'f', 103: 'g', 104: 'h', 105: 'i', 106: 'j', 107: 'k', 108: 'l', 109: 'm', 110: 'n',
#111: 'o', 112: 'p', 113: 'q', 114: 'r', 115: 's', 116: 't', 117: 'u', 118: 'v', 119: 'w', 120: 'x', 121: 'y', 122: 'z'}
_JOYSTICK_MAPPING = {
    0: 'joy_A',
    1: 'joy_B',
    2: 'joy_X',
    3: 'joy_Y',
    4: 'joy_LB',
    5: 'joy_RB',
    6: 'joy_back',
    7: 'joy_start',
    }

_MOUSE_MAPPING = {
    1: 'mouse_click',
    2: 'mouse_midclick',
    3: 'mouse_rightclick',
    4: 'mouse_wheel_up',
    5: 'mouse_wheel_down',
    }

_ALL_KEYS = list(_KEY_MAPPING.values()) + list(_JOYSTICK_MAPPING.values())
#_ALL_KEYS=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'ac_back', 'ampersand', 'asterisk', 'at', 'backquote', 'backslash', 'backspace', 'pause',
#'capslock', 'caret', 'clear', 'colon', 'comma', 'currencysubunit', 'euro', 'delete', 'dollar', 'down', 'end', 'equals', 'escape', 'exclaim',
#'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'greater', 'hash', 'help', 'home', 'insert',
#'kp_0', 'kp_1', 'kp_2', 'kp_3', 'kp_4', 'kp_5', 'kp_6', 'kp_7', 'kp_8', 'kp_9', 'kp_divide', 'kp_enter', 'kp_equals', 'kp_minus', 'kp_multiply',
#'kp_period', 'kp_plus', 'lalt', 'lctrl', 'left', 'leftbracket', 'leftparen', 'less', 'lsuper', 'lshift', 'menu', 'minus', 'mode', 'numlockclear',
#'pagedown', 'pageup', 'percent', 'period', 'plus', 'power', 'printscreen', 'question', 'quote', 'quotedbl', 'ralt', 'rctrl', 'return', 'rsuper',
#'right', 'rightbracket', 'rightparen', 'rshift', 'scrollock', 'semicolon', 'slash', 'space', 'sysreq', 'tab', 'underscore', 'unknown', 'up',
#'a', 'b', 'c', 'd','e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
#,'joy_A','joy_B','joy_X','joy_Y','joy_LB','joy_RB','joy_back','joy_start']

WASD_AS_ARROWS = {'a': 'left', 'd': 'right', 'w': 'up', 's': 'down'}
#trái, phải, lên xuống
ZQSD_AS_ARROWS = {'q': 'left', 'd': 'right', 'z': 'up', 's': 'down'}
WARS_AS_ARROWS = {'a': 'left', 's': 'right', 'w': 'up', 'r': 'down'}
AOE_AS_ARROWS = {'e': 'left', 'a': 'right', 'comma': 'up', 'o': 'down'}

DPAD_AS_ARROWS = {'dpad_left': 'left', 'dpad_right': 'right', 'dpad_up': 'up', 'dpad_down': 'down'}
DISABLE_ARROWS = {'left': None, 'right': None, 'up': None, 'down': None}


class EventReader():
    def __init__(self):
        self.__init_event_reader__()

    def __init_subclass__(cls):
        # if class have its own init, decorate it to call _init_event_reader() beforehand
        if hasattr(cls, '__init__'):
            class_init = cls.__init__

            def make_decorated_init():
                def decorated_init(self, *args, **kwargs):
                    self.__init_event_reader__()
                    class_init(self, *args, **kwargs)
                return decorated_init

            cls.__init__ = make_decorated_init()

    def __init_event_reader__(self):
        """
        Add handles and additional function to the object
        Thêm các hàm chức năng cho đối tượng
        """
        #################
        ## init timers ##
        #################
        # update
        self._update = hasattr(self, 'update')#True,False
        #kiểm tra đối tượng self có thuộc tính update hay không (trả về True hoặc False)

        # timers
        self._timers = []

        # delayed setattr
        self._delayed_setattr = []

        # metronomes
        self._metronomes = {}
        self._metronome_left = {}#{300:0}

        # look for methods with particular names
        for method_name in dir(self):
            #dir() trả về danh sách các thuộc tính hợp lệ của đối tượng
            if method_name.startswith('on_repeat_every_'):
                duration = int(method_name[16:])
                self._metronome_left[duration] = 0
                self._metronomes[duration] = getattr(self, method_name)
                #getattr(): trả về giá trị của thuộc tính bạn muốn tìm

        #################################
        ## init imput devices handlers ##
        #################################
        if not hasattr(self,'key_map'):
            self.key_map={}#dict
            #nếu không có thuộc tính key_map thì tạo 1 thuộc tính dict key_map
        if not hasattr(self,'joystick_id'):
            self.joystick_id=None
        self._handles={}#dict
        #'window_resize':AppControlls.on_window_resize
        #'down': buttons.Menu.on_key_down
        #'left': buttons.Menu.on_key_left
        #'return': buttons.Menu.on_key_return
        #'right': buttons.Menu.on_key_right
        #'up': buttons.Menu.on_key_up
        #'mouse_click': EventReader.__init_event_reader__.<locals>.make_rejector_of_None
        #'mouse_move': FallingFigure.on_mouse_move
        #'mouse_rightclick': EventReader.__init_event_reader__.<locals>
        
        self._category_handles=set()#mouse,key
        # system events
        if hasattr(self, 'on_window_resize'):
            self._handles['window_resize'] = self.on_window_resize
            #on_window_resize là 1 cặp chiều rộng và chiều cao mới của cửa sổ ứng dụng

        # keyboard and joistick
        for key in _ALL_KEYS:
            if hasattr(self, 'on_key_'+key):
                self._handles[key] = getattr(self, 'on_key_'+key)
                #getattr: lấy giá trị của 'on_key'+key

        if hasattr(self, 'on_any_key'):
            self._category_handles.add('key')

        #mouse
        #xử lý chuột
        def make_rejector_of_None(handle):
            def rejector_of_None(z):
                if z is not None:
                    handle(z)
            return rejector_of_None

        for key in _MOUSE_MAPPING.values():
            if hasattr(self, 'on_'+key):
                self._handles[key] = make_rejector_of_None(getattr(self, 'on_'+key))

        if hasattr(self, 'on_mouse_move'):
            self._handles['mouse_move'] = self.on_mouse_move

        if hasattr(self, 'mouse_map'):
            self._category_handles.add('mouse')
            self._mouse_pos = None

        ####################
        ## init hold keys ##
        ####################
        #giữ phím gì đó trong 1 khoảng thời gian
        self._hold_handles={}
        self._hold_duration={}
        for key in _ALL_KEYS:
            if hasattr(self, 'on_hold_'+key):
                self._hold_handles[key] = getattr(self, 'on_hold_'+key)
                self._hold_duration[key] = 0

        #giữ chuột
        for key in _MOUSE_MAPPING.values():
            if hasattr(self, 'on_hold_'+key):
                self._hold_handles[key] = getattr(self, 'on_hold_'+key)
                self._hold_duration[key] = 0

    def __read_events__(self, raw_events, time_passed, raw_key_pressed):
        # map keys
        events=[]
        key_pressed=[] #list các số hoặc tọa độ
        for (key,category,*args) in raw_events:
            if category=='joy':
                if self.joystick_id and args[0]!=self.joystick_id:
                    continue
                events.append((key,'key'))
            else:
                events.append((key,category,*args))
        for key in raw_key_pressed:
            if isinstance(key,tuple):
                if self.joystick_id and key[1]!=self.joystick_id:
                    continue
                key_pressed.append(key[0])
            else:
                key_pressed.append(key)
        if self.key_map:
            events=[(self.key_map.get(key,key),*args) for (key,*args) in events]
            key_pressed={self.key_map.get(key,key) for key in key_pressed}

        # process all event
        for (key,category,*args) in events:
            # some handles apply for the whole categories of events
            if category in self._category_handles:
                if category=='key':
                    self.on_any_key(key)
                elif category=='mouse':
                    self._mouse_pos=pos=self.mouse_map(*args[0])
                    args=[pos]
            # some only apply to specific events
            if key in self._handles:
                self._handles[key](*args)

        # hold keys
        for key, func in self._hold_handles.items():
            if key in key_pressed:
                self._hold_duration[key]+=time_passed
                func(self._hold_duration[key],time_passed)
            else:
                self._hold_duration[key]=0

        # update
        if self._update:
            self.update(time_passed)

        # metronomes
        for duration, func in self._metronomes.items():
            self._metronome_left[duration]+=time_passed
            if self._metronome_left[duration]>duration:
                self._metronome_left[duration]-=duration
                func()

        # timers
        self._timers=[[timer,delay-time_passed] for timer, delay in self._timers]
        while self._timers and self._timers[0][-1]<=0:
            (timer, delay),*self._timers=self._timers
            getattr(self,'on_timer_'+timer)()

        # delayed setattr
        self._delayed_setattr=[[attr,value,delay-time_passed] for attr,value,delay in self._delayed_setattr]
        while self._delayed_setattr and self._delayed_setattr[0][-1]<=0:
            (attr, value,delay),*self._delayed_setattr=self._delayed_setattr
            setattr(self,attr,value)

    def read_events(self, events,time_passed,key_pressed):
        self.__read_events__(events,time_passed,key_pressed)

    def start_timer(self,timer,delay,reset=True):
        if not hasattr(self, 'on_timer_'+timer):
            raise KeyError(f'timer on_timer_{timer} is not declared')
        if reset:
            self._timers=[[key,delay] for key,delay in self._timers if key!=timer]
        self._timers.append([timer, delay])
        # sort by delay only
        self._timers=list(sorted(self._timers,key=lambda x: x[-1]))

    def delayed_setattr(self,attr,value,delay,reset=True):
        if not hasattr(self,attr):
            raise AttributeError(f'no attribute {attr}')
        if reset:
            self._delayed_setattr=[[key,value,delay] for key,value,delay in self._delayed_setattr if key!=attr]
        self._delayed_setattr.append([attr,value,delay])
        # sort by delay only
        self._delayed_setattr=list(sorted(self._delayed_setattr,key=lambda x: x[-1]))

    def delayed_setattr_seq(self,attr,pairs):
        if not hasattr(self,attr):
            raise AttributeError(f'no attribute {attr}')
        self._delayed_setattr=[[key,value,delay] for key,value,delay in self._delayed_setattr if key!=attr]
        self._delayed_setattr+=[[attr,v,d] for v,d in pairs]
        # sort by delay only
        self._delayed_setattr=list(sorted(self._delayed_setattr,key=lambda x: x[-1]))


class EventReaderAsClass():
    def __init_subclass__(cls):
        EventReader.__init_event_reader__(cls)
    @classmethod
    def read_events(cls, events, time_passed, key_pressed):
        EventReader.__read_events__(cls, events, time_passed, key_pressed)

    @classmethod
    def start_timer(cls, timer, delay):
        EventReader.start_timer(cls, timer, delay)

    @classmethod
    def delayed_setattr(cls, attr, value, delay):
        EventReader.delayed_setattr(cls, attr, value, delay)


## ---------------------------------------------------------------------------
## DATA FILE
## ---------------------------------------------------------------------------

from collections import UserDict


class DataFile(UserDict):
    def __init__(self, filename, *args, **kwargs):
        #*args: truyền vào 1 list hoặc 1 tuple
        #**kwargs: dict làm tham số
        self.data = dict(*args, **kwargs)
        path = assets_path(filename, folder='datafiles')
        #...\tetris_for_two-master\tetris_fow_two-master\datafiles\filename
        self._path = path
        try:
            with open(path) as f:
                self.data.update(json.load(f))
                #lấy các key,value trong filename để chèn vào dict self.data
        except:
            # what if datafiles folder does not exist?
            folder = assets_path('', folder='datafiles')
            if not os.path.exists(folder):
                os.mkdir(folder)
                #nếu không tồn tại folder thì tạo 1 folder với path đã cho

    def save(self):
        with open(self._path, 'w') as f:
            json.dump(self.data, f, indent=4)
            #chuyển self.data sang string json (lưu dữ liệu self.data vào f)
    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()
        #đặt lại key,value và lưu lại


## ---------------------------------------------------------------------------
## Other Functions
## ---------------------------------------------------------------------------


def in_box(x, y, box):
    x0, y0, w, h = box
    return x0 <= x < x0+w and y0 <= y <= y0+h
