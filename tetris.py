import random

import simplified_pygame
from settings import ACTIVE_SETTINGS, SAVED_SETTINGS

FIGURE = {'-': [(0, 0), (1, 0), (-2, 0), (-1, 0)],
          '0': [(0, 0), (-1, 0), (0, 1), (-1, 1)],
          'L': [(0, 0), (-1, -1), (1, 0), (-1, 1)],
          'j': [(0, 0), (-1, 0), (1, 0), (1, 1)],
          's': [(-1, 0), (0, 1), (0, -1), (1, -1)],
          'r': [( 1, 0), (0, 0), (0, -1), (-1, -1)],
          'T': [(-1, 0), (0, 0), (0, -1), (1, 0)]}



INITIAL_SPEED = 300

COLORS = ACTIVE_SETTINGS['color_scheme']
#COLORS={
#   'background':[230,230,230],
#   'well':[255,255,255],
#   '-':[50,50,50],
#   '0':[204,48,48],
#   'L':[0,200,0],
#   'j':[0,0,200],
#   's':[183,157,25],
#   'r':[0,150,150],
#   'T':[175,51,165]}
class TrueRandomGenerator():
    def draw(self):
        return random.choice('-0LjsrT')

class FairRandomGenerator():
    def __init__(self):
        self.seq = '-0LjsrT'
    def draw(self):
        new = random.choice(self.seq)
        #trả về 1 item ngẫu nhiên trong string '-0LjsrT'
        self.seq = self.seq.replace(new, '') + '-0LjsrT'
        #thay thế ký tự new bằng rỗng
        return new

class SequentialRandomGenerator():
    def __init__(self):
        self.seq = ''.join(random.sample(list('-0LjsrT'), 7))
        #self.seq='L-srTj0'
    def draw(self):
        new, seq = self.seq[0], self.seq[1:]
        #new='L'
        #seq='-srTj0'
        if not seq:
            seq = ''.join(random.sample(list('-0LjsrT'), 7))
            if seq[0] == new:
                seq = seq[1:]+new
        self.seq = seq
        return new

def make_random_generator():
    if SAVED_SETTINGS['randomness'] == 'true random':
        return TrueRandomGenerator()
    if SAVED_SETTINGS['randomness'] == 'fair random':
        return FairRandomGenerator()
    if SAVED_SETTINGS['randomness'] == 'regularized':
        return SequentialRandomGenerator()



def rotate_figure(figure):
    if figure == '0^': return '0^', FIGURE['0'], [(0, 0)]#xoay 1 khối hình vuông thì không thay đổi

    if figure == 'T^': return 'T>', [( 1, 0),  (0, 0),   (0, -1),  (0, 1)],  [(0, 0)]
    if figure == 'T>': return 'Tv', [(-1, 0),  (0, 0),   (0,  1),  (1, 0)],  [(0, 0), (1, 0)]
    if figure == 'Tv': return 'T<', [(-1, 0),  (0, 0),   (0, -1),  (0, 1)],  [(0, 0)]
    if figure == 'T<': return 'T^', FIGURE['T'],  [(0, 0), (-1, 0)]

    if figure == '-^': return '->', [( 0, 0),  (0, -1),  (0, -2),  (0, -3)], [(0, 0)]
    if figure == '->': return '-^', FIGURE['-'],  [(0, 0), (0, 1)]

    if figure == 's^': return 's>', [(-1, -2), (-1, -1), (0, -1),  (0, 0)],  [(0, 0), (1, 0)]
    if figure == 's>': return 's^', FIGURE['s'],  [(0, 0), (0, 1)]

    if figure == 'r^': return 'r>', [(1, -2), (1, -1), (0, -1),  (0, 0)],  [(0, 0), (-1, 0)]
    if figure == 'r>': return 'r^', FIGURE['r'],  [(0, 0), (0, 1)]

    if figure == 'Lv': return 'L>', [(0, 0), (0, -1), (0, 1), (1, 1)],  [(0, 0)]
    if figure == 'L>': return 'L^', FIGURE['L'],  [(0, 0), (1, 0)]
    if figure == 'L^': return 'L<', [(0, 0), (0, -1), (0, 1), (-1, -1)],  [(0, 0)]
    if figure == 'L<': return 'Lv', [(0, 0), (-1, 0), (1, 0), (1, -1)],  [(0, 0), (-1, 0)]

    if figure == 'jv': return 'j>', [(0, 0), (0, -1), (0, 1), (1, -1)],  [(0, 0)]
    if figure == 'j>': return 'j^', FIGURE['j'],  [(0, 0), (1, 0)]
    if figure == 'j^': return 'j<', [(0, 0), (0, -1), (0, 1), (-1, 1)],  [(0, 0)]
    if figure == 'j<': return 'jv', [(0, 0), (-1, 0), (1, 0), (-1, -1)],  [(0, 0), (-1, 0)]


class ColorField():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.M = [[None for i in range(w)] for j in range(h)]
        self.left = [[(255, 255, 255, 0) for i in range(w)] for j in range(h)]
        self.bottom = [[(255, 255, 255, 0) for i in range(w)] for j in range(h)]
        self.corner = [[None for i in range(w)] for j in range(h)]

    def __getitem__(self, key):
        x, y = key
        if x <= -1 or y <= -1 or x >= self.w or y >= self.h:
            return None
        else:
            return self.M[y][x]

    def __setitem__(self, key, value):
        x, y = key
        if x <= -1 or y <= -1 or x >= self.w or y >= self.h:
            (200, 200, 200)
        else:
            self.M[y][x] = value

    def blur(self):
        weight = 30
        C = ColorField(self.w, self.h)
        for i in range(self.w):
            for j in range(self.h):
                if self[i, j] is None:
                    continue

                neighbours = [self[i+x, j+y] for x, y in [(0, -1), (0, 1), (1, 0), (-1, 0)] if self[i+x, j+y] is not None]
                if neighbours:
                    r, g, b = zip(*neighbours)
                    r0, g0, b0 = self[i, j]
                    C[i, j] = ((sum(r) + r0*weight) / (len(neighbours)+weight),
                               (sum(g) + g0*weight) / (len(neighbours)+weight),
                               (sum(b) + b0*weight) / (len(neighbours)+weight))
                else:
                    C[i, j] = self[i, j]

                if self[i+1, j] is not None:
                    r0, g0, b0, a0 = self.left[j][i]
                    r1, g1, b1 = self[i+1, j]
                    r2, g2, b2 = self[i, j]
                    C.left[j][i] = ((r1+r2)/2, (g1+g2)/2, (b1+b2)/2, min(255, a0+5))
                if self[i, j+1] is not None:
                    r0, g0, b0, a0 = self.bottom[j][i]
                    r1, g1, b1 = self[i, j+1]
                    r2, g2, b2 = self[i, j]
                    C.bottom[j][i] = ((r1+r2)/2, (g1+g2)/2, (b1+b2)/2, min(255, a0+5))
                if self[i, j+1] is not None and self[i+1, j] is not None and self[i+1, j+1] is not None:
                    r0, g0, b0, a0 = self.left[j][i]
                    r1, g1, b1, a1 = self.bottom[j][i]
                    C.corner[j][i] = ((r1+r0)/2, (g1+g0)/2, (b1+b0)/2, min(a0, a1))
        return C

    def remove_line(self, line_to_remove):
        #xóa màu
        #dịch chuyển màu xuống dưới
        for i in range(line_to_remove, 0, -1):
            for x in range(self.w):
                self.M[i][x] = self.M[i-1][x]
                self.left[i][x] = self.left[i-1][x]
                self.bottom[i][x] = self.bottom[i-1][x]
                self.corner[i][x] = self.corner[i-1][x]
        #xóa toàn bộ hàng đầu tiên từ trên xuống
        for x in range(self.w):
            self.M[0][x] = None
            self.left[0][x] = (255, 255, 255, 0)
            self.bottom[0][x] = (255, 255, 255, 0)
            self.corner[0][x] = None
            self.bottom[line_to_remove][x] = (255, 255, 255, 0)
            self.corner[line_to_remove][x] = None

    def draw(self, C):
        size = ACTIVE_SETTINGS['size']
        for i in range(self.w):
            for j in range(self.h):
                if self.M[j][i] is not None:
                    rect = (i*size+1, j*size+1, size-2, size-2)
                    C.rect(rect, self.M[j][i])

                    if self.left[j][i] is not None:
                        rect = (i*size+size-1, j*size+1, 2, size-2)
                        C.rect(rect, self.left[j][i])

                    if self.bottom[j][i] is not None:
                        rect = (i*size+1, j*size+size-1, size-2, 2)
                        C.rect(rect, self.bottom[j][i])

                    if self.corner[j][i] is not None:
                        rect = (i*size+size-1, j*size+size-1, 2, 2)
                        C.rect(rect, self.corner[j][i])


class TetrisWell(simplified_pygame.EventReader):
    def __init__(self, GAME, w, h):
        self.w = w
        self.h = h
        self.M = [[' ' for i in range(w)] for j in range(h)]

        self.GAME = GAME
        self.C = ColorField(w, h)

    def __getitem__(self, key):
        x, y = key
        if x <= -1 or x >= self.w or y >= self.h:
            return '#'
        elif y <= -1:
            return ' '
        else:
            return self.M[y][x]

    def __setitem__(self, key, value):
        x, y = key
        if x <= -1 or y <= -1 or x >= self.w or y >= self.h:
            return
        else:
            self.M[y][x] = value

    #trả về hàng có đầy đủ các khối hình vuông
    def get_full_line(self):
        for j, line in enumerate(self.M):
            if line == ['#']*self.w:
                return j
        return None

    def space_left(self):
        #ban đầu chiều cao của màn hình là 20 
        h = 0
        while all(self[x, h] != '#' for x in range(self.w)):
            h += 1
        #h: số hàng mà không tồn tại 1 khối hình nào
        return h-1

    #############################
    ## EVENTS HANDLING
    #############################
    def on_repeat_every_300(self):
        # blur
        if SAVED_SETTINGS['bleed']:
            self.C = self.C.blur()

    #############################
    ## DRAWING
    #############################
    #tạo 1 surface hình chữ nhật màu trắng để chơi game
    def draw(self, canvas):
        size = ACTIVE_SETTINGS['size']
        canvas.rect((-1, -1, self.w*size+2, self.h*size+2), COLORS['well'])
        #self.w:11
        #self.h:35
        #size:16
        #COLOR['well']: màu trắng
        with canvas.layer() as layer:
            self.C.draw(layer)

    #############################
    ## GAME
    #############################
    def calcify(self, player):
        for i, j in player.figure:
            self[i, j] = '#'
            self.C[i, j] = COLORS[player.cur[0]]
            if j<0:
                self.GAME.do_game_over(player)

    def remove_line(self, line_to_remove):
        for i in range(line_to_remove, -1, -1):
            for x in range(self.w):
                self[x, i] = self[x, i-1]
                #xóa hàng bằng cách đưa hàng bên trên xuống dưới
        self.C.remove_line(line_to_remove)

    def borrow_line(self, other):
        """ used for the balanced well coop """
        if self.h >= self.possible_h:
            return

        self.h += 1
        self.M = [[' ' for i in range(self.w)]] +self.M
        other.M = other.M[1:]
        other.h -= 1

        self.C.h += 1
        self.C.M = [[None for i in range(self.C.w)]] + self.C.M
        self.C.left = [[None for i in range(self.C.w)]] + self.C.left
        self.C.bottom = [[None for i in range(self.C.w)]] + self.C.bottom
        self.C.corner = [[None for i in range(self.C.w)]] + self.C.corner
        other.C.M = other.C.M[1:]
        other.C.h -= 1

    def flip_copy_well(self, other, reverse=False):
        """ used for heart-shaped coop """
        h, w = self.h, self.w
        for i in range(w):
            for j in range(w):
                if reverse:
                    self.M[h-w+j][i] = other.M[h-i-1][j]
                    self.C.M[h-w+j][i] = other.C.M[h-i-1][j]
                    self.C.corner[h-w+j][i] = other.C.corner[h-i-2][j]
                    self.C.bottom[h-w+j][i] = other.C.left[h-i-1][j]
                    self.C.left[h-w+j][i] = other.C.bottom[h-i-2][j]
                else:
                    self.M[h-i-1][j] = other.M[h-w+j][i]
                    self.C.M[h-i-1][j] = other.C.M[h-w+j][i]
                    self.C.corner[h-i-1][j] = other.C.corner[h-w+j][i-1] if i>0 else (255, 255, 255, 0)
                    self.C.bottom[h-i-1][j] = other.C.left[h-w+j][i-1] if i>0 else (255, 255, 255, 0)
                    self.C.left[h-i-1][j] = other.C.bottom[h-w+j][i]


class FallingFigure(simplified_pygame.EventReader):
    def __init__(self, GAME, well, controlls=1, mouse_offset=0.5):
        self.GAME = GAME
        self.well = well
        self.play = True
        self.message = ''
        self.mouse_offset = mouse_offset

        self.start_x = well.w // 2
        self.random_generator = make_random_generator()
        #tạo ra các màu ngẫu nhiên
        self.nextfig = self.random_generator.draw()
        #self.nextfig là 1 chuỗi ký tự mà 1 ký tự là 1 màu
        self.y = 1  # guaranties drawing of the nexfig

        self.score = 0
        self.step_duration = INITIAL_SPEED #300
        self.timer = 0

        self.cur = None
        self.last_move = None
        if controlls == 0:
            # single-player game
            self.key_map = simplified_pygame.DPAD_AS_ARROWS | SAVED_SETTINGS['letters'] | {'joy_Y': 'up', 'joy_A': 'down'}
            self.use_mouse = True
        elif controlls == 2:
            # second player
            if not SAVED_SETTINGS['wasd']:
                self.key_map |= SAVED_SETTINGS['letters']
            if SAVED_SETTINGS['arrows']:
                self.key_map |= simplified_pygame.DISABLE_ARROWS
            self.use_mouse = not SAVED_SETTINGS['mouse']
            if len(simplified_pygame.MAIN_WINDOW.joysticks_ids) == 1 and not SAVED_SETTINGS['controller']:
                self.key_map |= simplified_pygame.DPAD_AS_ARROWS | {'joy_Y': 'up', 'joy_A': 'down'}
            elif len(simplified_pygame.MAIN_WINDOW.joysticks_ids) > 1:
                self.key_map |= simplified_pygame.DPAD_AS_ARROWS | {'joy_Y': 'up', 'joy_A': 'down'}
                self.joystick_id = simplified_pygame.MAIN_WINDOW.joysticks_ids[SAVED_SETTINGS['controller']]

        elif controlls == 1:
            # first player
            if SAVED_SETTINGS['wasd']:
                self.key_map |= SAVED_SETTINGS['letters']
            if not SAVED_SETTINGS['arrows']:
                self.key_map |= simplified_pygame.DISABLE_ARROWS
            self.use_mouse = SAVED_SETTINGS['mouse']
            if len(simplified_pygame.MAIN_WINDOW.joysticks_ids) == 1 and SAVED_SETTINGS['controller']:
                self.key_map |= simplified_pygame.DPAD_AS_ARROWS | {'joy_Y': 'up', 'joy_A': 'down'}
            elif len(simplified_pygame.MAIN_WINDOW.joysticks_ids) > 1:
                self.key_map |= simplified_pygame.DPAD_AS_ARROWS | {'joy_Y': 'up', 'joy_A': 'down'}
                self.joystick_id = simplified_pygame.MAIN_WINDOW.joysticks_ids[1-SAVED_SETTINGS['controller']]

    def drop(self):
        if not self.play:
            return
        #nếu tồn tại khối hình đang di chuyển thì không thể để khối hình tiếp theo di chuyển xuống 
        figure, self.nextfig = self.nextfig, self.random_generator.draw()
        self.cur = figure+'^'       # figure's name and location
        self.item = FIGURE[figure]  # figure without x and y (khối hình tiếp theo)
        self.x = self.start_x
        self.y = - max(y for x, y in self.item) - 2
        #khối tiếp theo sẽ nằm ở giữa bên trên cùng

    @property
    def figure(self):
        if self.cur:
            return [(i+self.x, j+self.y) for i, j in self.item]
        else:
            return []

    #############################
    ## EVENTS HANDLING
    #############################
    def on_key_up(self):
        self.rotate()
        #ấn nút lên thì xoay khối hình
    def on_key_down(self):
        self.move(0, 1)
        #đi xuống dưới y+1
    def on_key_left(self):
        self.move(-1, 0)
        #đi sang trái x-1
    def on_key_right(self):
        self.move(1, 0)
        #đi sang phải x+1
    def on_hold_down(self, dur, dt):#giữ phím xuống dưới
        if dur > 130:
            self.insist_falling()
            self._hold_duration['down'] -= 10
    def on_hold_left(self, dur, dt):#giữ phím sang trái
        if dur > 130:
            self.move(-1, 0)
            self._hold_duration['left'] -= 25
    def on_hold_right(self, dur, dt):#giữ phím sang phải
        if dur > 130:
            self.move(1, 0)
            self._hold_duration['right'] -= 25
    def update(self, dt):
        self.timer += dt
        if self.timer > self.step_duration:
            self.timer -= self.step_duration
            self.fall()
    def on_mouse_move(self, pos):
        if not self.use_mouse: return
        x, _ = pos
        x = int((x - simplified_pygame.MAIN_WINDOW.w * self.mouse_offset) / ACTIVE_SETTINGS['size']) + self.well.w // 2
        cur_x = self.x
        if x < self.x:
            for i in range(self.x-x):
                self.move(-1, 0)
        elif x > self.x:
            for i in range(x-self.x):
                self.move(1, 0)
    def on_mouse_click(self, _):
        if not self.use_mouse: return
        self.on_key_up()
        #nếu có sử dụng chuột và click thì khối hình sẽ bị xoay 90 độ ngược chiều kim đồng hồ
    def on_mouse_rightclick(self, _):
        if not self.use_mouse: return
        self.on_key_down()
        #chuột phải thì khối hình đi xuống dưới
    def on_hold_mouse_rightclick(self, dur, dt):
        if not self.use_mouse: return
        if dur > 130:
            self.insist_falling()
            self._hold_duration['mouse_rightclick'] -= 10
        #giữ chuột phải thì khối hình đi xuống nhanh hơn
    #############################
    ## DRAWING
    #############################
    def draw(self, C):
        size = ACTIVE_SETTINGS['size']

        #draw_future_fig(self, C, size):
        #vẽ 1 khối hình bên trên cùng của surface game và chưa di chuyển
        if self.y > 0:
            f = self.nextfig
            for i, j in FIGURE[f]:
                rect = ((i + self.start_x)*size+1, (j-3)*size+1, size-2, size-2)
                #tạo 1 hình vuông
                C.rect(rect, COLORS[f])
                #vẽ 1 khối hình có cùng màu COLORS[f]

        #draw_fig(self, C, size):
        #khối hình bắt đầu di chuyển
        if self.cur:
            for i, j in self.figure:
                rect = (i*size+1, j*size+1, size-2, size-2)
                C.rect(rect, COLORS[self.cur[0]])
            if SAVED_SETTINGS['shadow']:#nếu 1 khối di chuyển và chạm vào 1 khối khác thì sẽ bị chuyển màu
                # draw_shadow(self, C, size):
                for i, j in self.figure:
                    while self.well[i, j+1] == ' ':
                        j += 1
                    rect = (i*size+1, j*size+1, size-2, size-2)
                    C.box(rect, COLORS[self.cur[0]])

    def draw_ghost(self,C):
        size=ACTIVE_SETTINGS['size']
        if self.cur:
            for i,j in self.figure:
                rect=(i+0.5)*size,(j+0.5)*size
                C.circle(rect,size/2-1,COLORS[self.cur[0]],width=3)

    def draw_interface(self,C):
        scale=ACTIVE_SETTINGS['scale']
        right=scale*10*self.well.w
        # draw_interface(self, C, size, font):
        C.write(0,-scale*50,f'score\n{self.score}',size=14)
        #hiện score lên SCREEN
        C.write(right,-scale*50,f'speed\n{int(1000/self.step_duration)-2}',size=14,pos='<')
        #hiện speed lên SCREEN
        if not self.play:
            C.write(right//2,-scale*20,'GAME OVER',font='cambria-bold', size=14, pos='.')
            #hiện game over
        elif self.message:
            C.write(right//2, -scale*60, self.message, font='cambria-bold', size=14, pos='.')

    #############################
    ## GAME
    #############################
    def try_to_move(self, dx, dy):
        if not self.play or not self.cur:
            return

        if self.GAME.check_collision(self.well, self, [(i+dx, j+dy) for i, j in self.figure]):
            self.last_move = None
            return 'blocked'
        #kiểm tra xem khối hình đó đã đi hết chiều dài surface game hay chưa
        #nếu có thì trả về 'blocked'

        self.x += dx
        self.y += dy
        return 'moved'
        #nếu không thì khối hình tiếp tục di chuyển và self.y+=1

    def move(self, dx, dy):
        if not self.play or not self.cur:
            return
        self.try_to_move(dx, dy)
        self.last_move = dx, dy

    def insist_falling(self):
        if self.last_move == (0, 1):
            self.try_to_move(0, 1)
            #dx=0: chỉ đi theo chiều dọc nhanh hơn mà không thể đi chéo nhanh hơn được

    def fall(self):
        if not self.play or not self.cur:
            return

        collision = self.GAME.check_collision(self.well, self, [(i, j+1) for i, j in self.figure])
        if not collision:
            self.y += 1

        if collision == 'blocked':
            self.well.calcify(self)
            self.cur = None
            self.GAME.do_check_lines(self.well, self)
            self.GAME.do_next_turn(self)

    def score_up(self):
        self.score += 1

    def appropriate_speed(self):
        """ used for speedup mode """
        if self.score <= 10:
            return 300 - 10*self.score
        elif self.score <= 20:
            return 250 - 5*self.score
        elif self.score <= 45:
            return 190 - 2*self.score
        else:
            return max(1, 145 - self.score)

    def speed_up(self):
        if self.step_duration > 200:
            self.step_duration -= 10
        elif self.step_duration > 150:
            self.step_duration -= 5
        elif self.step_duration > 100:
            self.step_duration -= 2
        elif self.step_duration > 0:
            self.step_duration -= 1

    def rotate(self):
        if not self.play or not self.cur:
            return
        new_pos, new_item, new_coords = rotate_figure(self.cur)
        for dx, dy in new_coords:
            can_rotate = not self.GAME.check_collision(self.well, self, [(self.x+dx+i, self.y+dy+j) for i, j in new_item])
            if can_rotate:
                self.item = new_item
                self.cur = new_pos
                self.x += dx
                self.y += dy
                return 'moved'
        return 'blocked'


class StartTitle(TetrisWell):
    def __init__(self):
        super().__init__(None, w=11, h=35)
        #-0LjsrT
        text = """\
   TTT
    T
    T
    T
    T
   ---
   -
   ---
   -
   ---
     TTT
      T
      T
      T
      T
    rrr
    r r
    rr
    r r
    r r
  jjj
   j
   j
   j
  jjj
   sss
   s
   sss
     s
   sss
LL000rrr --
L 0 0r r  -
LL0 0rr  --
L 0 0r r -
L 000r r --
"""
        for i, line in enumerate(text.splitlines()):
            #i: số thứ tự các dòng bắt đầu từ 0
            #line: xâu ký tự trên 1 dòng
            for j, s in enumerate(line):
                #s: lấy từng ký tự trên 1 line
                if s != ' ':
                    self.C[j, i] = COLORS[s]


    def draw(self, W):#W là SCREEN
        size = ACTIVE_SETTINGS['size']
        #size=10*min(W.w/600,W.h/400)
        W = W.with_offset(W.w//4-size*10, size*2)
        super().draw(W)
        __version__ = '___XiaoHuHuHuH___'
        W.write(0, 35*size, __version__, size=14)
