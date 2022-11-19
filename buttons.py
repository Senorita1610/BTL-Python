import simplified_pygame
from settings import ACTIVE_SETTINGS, SAVED_SETTINGS


class Menu(simplified_pygame.EventReader):
    def __init__(self):
        self.buttons=[] #danh sách các nút bấm
        self.labels=[] #danh sách các nhãn
        self._x=0
        self._y=0
        self.key_map=simplified_pygame.DPAD_AS_ARROWS | {b: 'return' for b in 'space joy_Y joy_A joy_A joy_A'.split()}
        #self.key_map={'dpad_left': 'left','dpad_right':'right','dpad_up':'up','dpad_down':'down','space':'return','joy_Y':'return','joy_A':'return'}
    def append(self, button, x=None, y=None, dx=0, dy=0):
        button.x = self._x=(self._x+dx) if x is None else x
        button.y = self._y=(self._y+dy) if y is None else y
        if hasattr(button, 'in_box'):
            self.buttons.append(button)
        else:
            self.labels.append(button)
    def draw(self, W):
        size = ACTIVE_SETTINGS['size']
        scale = ACTIVE_SETTINGS['scale']
        x0 = simplified_pygame.MAIN_WINDOW.w // 2 - size * 12
        W = W.with_offset(x0, 0)


        for b in self.labels:
            b.draw(W, size, scale)
        for b in self.buttons:
            b.draw(W, size, scale, selected=self._mouse_pos == b)

    def mouse_map(self, x, y):
        size = ACTIVE_SETTINGS['size']
        x = (x - simplified_pygame.MAIN_WINDOW.w/2) / size + 12
        y = int((y - simplified_pygame.MAIN_WINDOW.y0)/size + 1)
        for b in self.buttons:
            if b.in_box(x, y):
                return b

    def on_mouse_click(self, button):
        button.on_mouse_click()
        simplified_pygame.mixer.play_sound('pop0')

    def on_key_return(self):
        if self._mouse_pos:
            self.on_mouse_click(self._mouse_pos)

    def on_key_up(self):
        cur = self._mouse_pos
        if cur:
            x, y0 = cur.x + cur.w//2, cur.y
            for y in range(y0-1, -1, -1):
                for b in self.buttons:
                    if b.in_box(x, y):
                        self._mouse_pos = b
                        return
        self._mouse_pos = sorted(self.buttons, key = lambda b: b.y)[0]

    def on_key_down(self):
        cur = self._mouse_pos
        if cur:
            x, y0 = cur.x + cur.w//2, cur.y + cur.h
            for y in range(y0+1, 50):
                for b in self.buttons:
                    if b.in_box(x, y):
                        self._mouse_pos = b
                        return
        self._mouse_pos = sorted(self.buttons, key = lambda b: b.y)[-1]

    def on_key_left(self):
        cur = self._mouse_pos
        if cur:
            x0, y = cur.x, cur.y + cur.h//2
            for x in range(x0-1, -1, -1):
                for b in self.buttons:
                    if b.in_box(x, y):
                        self._mouse_pos = b
                        return
        self._mouse_pos = sorted(self.buttons, key = lambda b: b.x)[0]

    def on_key_right(self):
        cur = self._mouse_pos
        if cur:
            x0, y = cur.x + cur.w, cur.y + cur.h//2
            for x in range(x0+1, 50):
                for b in self.buttons:
                    if b.in_box(x, y):
                        self._mouse_pos = b
                        return
        self._mouse_pos = sorted(self.buttons, key = lambda b: b.x)[-1]



class Label:
    def __init__(self, text):
        self.text = text

    #vẽ label tương tự title nhưng font là default_font
    def draw(self, W, size, scale):
        W.write(self.x*size, self.y*size, self.text, size=size)

    def __repr__(self):
        return str(self.text)


class Title(Label):
    def draw(self, W, size, scale):
        W.write(self.x*size, self.y*size, self.text, size=size, font='FrostbiteBossFight-dL0Z')


class ConditionalText:
    def __init__(self, parameter, descriptions):
        self.parameter = parameter
        self.descriptions = descriptions

    def draw(self, W, size, scale):
        val = SAVED_SETTINGS[self.parameter]
        text = self.descriptions.get(val, '')#lấy đoạn text từ giá trị val
        W.write(self.x*size, self.y*size, text, size=size*0.8)
        #viết đoạn text lên SCREEN

    def __repr__(self):
        return str(self.parameter)


class Sprite:
    def __init__(self, sprite):
        self.sprite = sprite

    def draw(self, W, size, scale):
        W.sprite(self.x*size, self.y*size, self.sprite, scale=scale/2)

    def __repr__(self):
        return str(self.sprite)


class _Button:
    def __init__(self, text, w=10, h=3):
        self.text = text
        self.w = w
        self.h = h

    def draw(self, W, size, scale, selected):
        if selected:
            box = (self.x*size, (self.y+0.1)*size, self.w*size, self.h*size)
            W.rect(box, (255, 200, 100))

        W.write((self.x+1)*size, (self.y+1)*size, self.text, size=size)

    def in_box(self, x, y):
        return simplified_pygame.in_box(x, y, (self.x, self.y, self.w, self.h))

    def on_mouse_click(self):
        pass


class SetButton(_Button):

    parameter = None

    def __init__(self, text, value, parameter=None, w=10, h=3):
        super().__init__(text, w=w, h=h)
        if parameter is not None:
            self.parameter = parameter
        self.value = value

    def draw(self, W, size, scale, selected):
        box = (self.x*size, (self.y+0.1)*size, self.w*size, self.h*size)
        if selected:
            W.rect(box, (255, 200, 100))
            #nếu di chuyển chuột vào vùng muốn chọn thì vùng đó sẽ đổi thành màu (255,200,100)
        elif SAVED_SETTINGS[self.parameter] == self.value:
            col = [min(255, x+30) for x in ACTIVE_SETTINGS['color_scheme']['background']]
            W.rect(box, col)
            #vẽ 1 hình chữ nhật màu ACTIVE_SETTINGS['color_scheme']['background'] vào tên màu đã chọn trước đó

        W.write((self.x+1)*size, (self.y+1)*size, self.text, size=size)
        #vẽ đoạn text lên SCREEN

    def on_mouse_click(self):
        SAVED_SETTINGS[self.parameter] = self.value#nếu click chuột thì giá trị màu mới sẽ được lưu lại
        self.post_activation()

    def post_activation(self):
        pass

    def __repr__(self):
        return str(self.value)


class SmallSetButton(SetButton):

    def draw(self, W, size, scale, selected):
        box = (self.x*size, (self.y+0.2)*size, self.w*size, (self.h-0.2)*size)
        if selected:
            W.rect(box, (255, 200, 100))
        elif SAVED_SETTINGS[self.parameter] == self.value:
            col = [min(255, x+30) for x in ACTIVE_SETTINGS['color_scheme']['background']]
            W.rect(box, col)

        W.write((self.x + self.w/2)*size, (self.y+1)*size, self.text, size=size, pos='.')

    def __init__(self, text, value, parameter=None, w=3, h=3):
        super().__init__(text, parameter=parameter, value=value, w=w, h=h)


class ActionButton(_Button):
    #reset kích thước màn hình
    def __init__(self, text, action, w=10, h=3):
        super().__init__(text, w=w, h=h)
        self.action = action

    def on_mouse_click(self):
        self.action()


class BigActionButton(ActionButton):

    def __init__(self, text, action, w=14, h=4):
        super().__init__(text, action=action, w=w, h=h)

    def draw(self, W, size, scale, selected):
        if selected:
            box = (self.x*size, (self.y+0.1)*size, self.w*size, self.h*size)
            W.rect(box, (255, 200, 100))

        W.write((self.x+self.w/2)*size, (self.y+1)*size, self.text, size=size, font='FrostbiteBossFight-dL0Z', pos='.')
