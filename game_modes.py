import simplified_pygame

from settings import ACTIVE_SETTINGS

import tetris


class TetrisGame():
    """
    Regular Tetris game.
    """
    #chuỗi docstring mô tả của lớp TetrisGame
    def __init__(self, w=10, h=25):
        self.well = tetris.TetrisWell(self, w, h)
        self.player = tetris.FallingFigure(self, self.well, controlls=0)
        #controlls=0: 1 người chơi
        self.do_next_turn(self.player)

    @property
    def play(self): return self.well1.play

    def read_events(self, events, dt, key_pressed):
        self.player.read_events(events, dt, key_pressed)
        self.well.read_events(events, dt, key_pressed)

    #kiểm tra va chạm
    def check_collision(self, well, player, figure):
        for i, j in figure:
            if well[i, j] == '#':
                return 'blocked'
        return False

    def do_check_lines(self, well, player):
        full = well.get_full_line()
        cleared = 0
        while full:
            well.remove_line(full)
            player.score_up()
            #score tăng thêm 1
            player.speed_up()
            #tăng tốc
            full=well.get_full_line()
            cleared += 1
        simplified_pygame.mixer.play_sound(f'pop{min(4, cleared)}')
        #bật nhạc 

    def do_game_over(self, player):
        player.play = False

    def do_next_turn(self, player):
        player.drop()

    def draw_game(self, W):
        size = ACTIVE_SETTINGS['size']
        offset = W.with_offset(W.w//2 - self.well.w//2*size, size*10)
        self.well.draw(offset)
        self.player.draw(offset)
        self.player.draw_interface(offset)


class TetrisGame2Players(TetrisGame):
    """
    Two regular independent tetris
    games happening side by side.
    """
    #chuỗi docstring mô tả của lớp TetrisGame2Players
    def __init__(self, w=10, h=25):
        self.well1 = tetris.TetrisWell(self, w, h)
        self.well2 = tetris.TetrisWell(self, w, h)
        self.player1 = tetris.FallingFigure(self, self.well1, controlls=1, mouse_offset=0.75)
        self.player2 = tetris.FallingFigure(self, self.well2, controlls=2, mouse_offset=0.25)

        self.ready = [False, False]
        self.do_next_turn(self.player1)
        self.do_next_turn(self.player2)

    def read_events(self, events, dt, key_pressed):
        self.player1.read_events(events, dt, key_pressed)
        self.player2.read_events(events, dt, key_pressed)
        self.well1.read_events(events, dt, key_pressed)
        self.well2.read_events(events, dt, key_pressed)

    @property
    def play(self):
        return self.well1.play | self.well2.play

    def draw_game(self, W):
        size = ACTIVE_SETTINGS['size']
        #tạo 2 surface cho 2 người chơi có cùng kích thước h*w
        #điểm bắt đầu surface sẽ cùng x khác y
        offset = W.with_offset(W.w//4 - self.well2.w//2*size, size*10)
        self.well2.draw(offset)
        self.player2.draw(offset)
        self.player2.draw_interface(offset)

        offset = W.with_offset(W.w//4*3 - self.well1.w//2*size, size*10)
        self.well1.draw(offset)
        self.player1.draw(offset)
        self.player1.draw_interface(offset)

    def do_next_turn(self, player):
        #1 lúc chỉ được 1 người chơi
        #nếu cả 2 cả cùng điều khiển thì khối hình sẽ rơi tự do
        if player is self.player1:
            self.ready[0] = True
        elif player is self.player2:
            self.ready[1] = True

        if self.ready == [True, True]:
            self.ready = [not self.player1.play, not self.player2.play]
            self.do_drop()

    def do_drop(self):
        self.player1.drop()
        self.player2.drop()


class TetrisGameSpeedUp(TetrisGame2Players):
    """
    When a line is completed,
    opponent's game speed is
    doubled until they complete
    their own line.
    """
    #Khi 1 người chơi hoàn thành 1 hàng ngang thì tốc độ trò chơi của đối thủ tăng lên
    #chuỗi docstring mô tả của lớp TetrisGameSpeedUp
    #hàm draw_game y hệt TetrisGame2Players
    def do_check_lines(self, well, player):
        if player is self.player1:
            other = self.player2
        elif player is self.player2:
            other = self.player1

        full = well.get_full_line()
        cleared = 0
        while full:
            well.remove_line(full)
            player.score_up()
            full = well.get_full_line()
            player.step_duration = player.appropriate_speed()
            #tốc độ của player giữ nguyên
            other.step_duration = other.appropriate_speed() // 2
            #tốc độ của other tăng gấp đôi
            player.message = ''
            other.message = '+ speed +'
            cleared += 1
        simplified_pygame.mixer.play_sound(f'pop{min(4, cleared)}')


class TetrisGameMirror(TetrisGame2Players):
    """
    Two players are receiving
    identical figures.
    """
    #2 người chơi nhận khối hình tiếp theo giống hệt nhau
    #chuỗi docstring mô tả của lớp TetrisMirror
    def __init__(self, w=10, h=25):
        self.well1 = tetris.TetrisWell(self, w, h)
        self.well2 = tetris.TetrisWell(self, w, h)
        self.player1 = tetris.FallingFigure(self, self.well1, controlls=1, mouse_offset=0.75)
        self.player2 = tetris.FallingFigure(self, self.well2, controlls=2, mouse_offset=0.25)

        self.ready = [False, False]
        self.player2.nextfig = self.player1.nextfig#tạo 2 khối hình giống nhau
        self.do_next_turn(self.player1)
        self.do_next_turn(self.player2)
        #lấy hàm do_next_turn của TetrisGame2Players

    def do_drop(self):
        # assume nextfigs are the same
        self.player1.drop()
        self.player2.drop()
        self.player2.nextfig = self.player1.nextfig


class TetrisGameWrestling(TetrisGameMirror):
    """
    Intercept your opponent while
    trying to complete
    your own lines
    """
    #Dùng 1 khối hình khác để ngăn cản đối thủ của bạn, làm cho đối thủ của bạn khó chơi hơn
    #chuỗi docstring mô tả của lớp TetrisGameWrestling
    def __init__(self, w=10, h=25):
        self.well1 = tetris.TetrisWell(self, w, h)
        self.well2 = tetris.TetrisWell(self, w, h)
        self.player1 = tetris.FallingFigure(self, self.well1, controlls=1, mouse_offset=0.75)
        self.player2 = tetris.FallingFigure(self, self.well2, controlls=2, mouse_offset=0.25)
        self.player1.start_x = 7#bắt đầu tại x=7
        self.player2.start_x = 2#bắt đầu tại x=2

        self.ready = [False, False]
        self.player2.nextfig = self.player1.nextfig#tạo 2 khối hình giống nhau
        self.do_next_turn(self.player1)
        self.do_next_turn(self.player2)


    def check_collision(self, well, player, figure):
        for i, j in figure:
            if well[i, j] == '#':
                return 'blocked'

        # in addition, we need to check collisions between figures
        #kiểm tra sự va chạm giữa 2 khối hình giống nhau trong màn hình của 1 người chơi
        if player is self.player1:
            if set(figure) & set(self.player2.figure):
                return 'friend'
        elif player is self.player2:
            if set(figure) & set(self.player1.figure):
                return 'friend'

        return False

    def draw_game(self, W):
        size = ACTIVE_SETTINGS['size']

        offset2 = W.with_offset(W.w//4   - self.well1.w//2*size, size*10)
        offset1 = W.with_offset(W.w//4*3 - self.well1.w//2*size, size*10)

        self.well2.draw(offset2)
        self.well1.draw(offset1)

        self.player2.draw(offset2)
        self.player1.draw(offset1)
        
        #vẽ khối hình dùng để ngăn cản đối phương
        self.player2.draw_ghost(offset1)#hình của người chơi 2 vẽ lên màn hình của người 1
        self.player1.draw_ghost(offset2)#hình của người chơi 1 vẽ lên màn hình của người 2
        #tạo ra các khối hình gồm các hình tròn tạo thành

        self.player2.draw_interface(offset2)
        self.player1.draw_interface(offset1)



class TetrisGameCoop(TetrisGame2Players):

    def do_game_over(self, _):
        self.player1.play = False
        self.player2.play = False

    @property
    def play(self):
        return self.well1.play & self.well2.play

class TetrisGameBalance(TetrisGameCoop):
    """
    Heights of both wells are
    balanced, so that each player
    gets about the same amount of
    empty space.
    """
    #chuỗi docstring mô tả của lớp TetrisGameBalance
    def __init__(self):
        super().__init__(10, 20)
        #self.well1=tetris.TetrisWell(self,10,20)
        #self.well2=tetris.TetrisWell(self,10,20)
        #self.player1=tetris.FallingFigure(self,self.well1,controlls=1,mouse_offset=0.75)
        #self.player2=tetris.FallingFigure(self,self.well2,controlls=2,mouse_offset=0.25)
        #self.ready=[False,False]
        #self.do_next_turn(self.player1)
        #self.do_next_turn(self.player2)
        self.well1.possible_h=30
        self.well2.possible_h=30
    def do_drop(self):
        h1=self.well1.space_left()
        h2=self.well2.space_left()
        if h1 > h2+1:#nếu chiều cao khoảng trống của người 1 -1 > chiều cao khoảng trống của người 2 
            self.well2.borrow_line(self.well1)
            #chiều dài màn hình của người 1 sẽ bị trừ đi 1
            #chiều dài màn hình của người 2 sẽ thêm 1

        if h2 > h1+1:
            self.well1.borrow_line(self.well2)
            #chiều dài màn hình của người 2 sẽ bị trừ đi 1
            #chiều dài màn hình của người 1 sẽ thêm 1
        #nếu h1 hoặc h2 >=30 thì hàm borrow_line không được thực hiện

        self.player1.drop()
        self.player2.drop()

    def draw_game(self, W):
        size = ACTIVE_SETTINGS['size']
        super().draw_game(W.with_offset(0, -size*2))
        #vẽ 2 surface cho 2 người chơi

        sub = W.crop(W.w//4 - 5*size, size*8, size*10, size*self.well2.h).flip(False, True).set_alpha(50)
        #flip(False,True): lật surface theo chiều dọc
        #set_alpha(50): các pixel trong surface sẽ được vẽ hơi trong suốt
        #0: hoàn toàn trong suốt
        #255: hoàn toàn mờ đục
        W.sprite(W.w//4*3 - 5*size, size*(9+self.well1.h), sub)
        #surface sub sẽ nằm phía dưới màn hình của người chơi 2
        sub = W.crop(W.w//4*3 - 5*size, size*8, size*10, size*self.well1.h).flip(False, True).set_alpha(50)
        W.sprite(W.w//4 - 5*size, size*(9+self.well2.h), sub)
        #surface sub sẽ nằm phía dưới màn hình của người chơi 1
        #2 surface sub có chiều cao sẽ thay đổi theo chiều cao màn hình của 2 người chơi

class TetrisGameSwap(TetrisGameCoop):
    """
    Each turn players swap
    their controls.
    """
    #đổi điều khiển sau mỗi lượt chơi
    #chuỗi docstring mô tả của lớp TetrisGameCoop
    def __init__(self):
        super().__init__()
        self.player1.message='<   Left'
        self.player2.message='Right   >'
    def do_drop(self):
        self.player1,self.player2=self.player2,self.player1
        self.player1.well,self.player2.well=self.player2.well, self.player1.well
        self.player1.nextfig, self.player2.nextfig =  self.player2.nextfig, self.player1.nextfig#thay đổi ký tự màu cho nhau
        self.player1.mouse_offset, self.player2.mouse_offset = self.player2.mouse_offset, self.player1.mouse_offset#thay đổi vị trí con chuột
        self.player1.drop()
        self.player2.drop()


class TetrisGameCommonWell(TetrisGameCoop):
    """
    Play together in the same
    big well.
    """
    #2 người cùng chơi với 1 màn hình lớn
    #chuỗi docstring mô tả của lớp TetrisGameCommonWell
    def __init__(self):
        self.well = tetris.TetrisWell(self, 20, 25)#tạo 1 màn hình kích thước 25x20
        self.player1 = tetris.FallingFigure(self, self.well, controlls=1)
        self.player2 = tetris.FallingFigure(self, self.well, controlls=2)

        self.player2.start_x = 5
        self.player1.start_x = 15
        self.ready = [False, False]
        self.do_next_turn(self.player1)
        self.do_next_turn(self.player2)

    def read_events(self, events, dt, key_pressed):
        self.player1.read_events(events, dt, key_pressed)
        self.player2.read_events(events, dt, key_pressed)
        self.well.read_events(events, dt, key_pressed)

    def check_collision(self, well, player, figure):
        for i, j in figure:
            if well[i, j] == '#':
                return 'blocked'
        # in addition, we need to check collisions between figures
        if player is self.player1:
            other = self.player2
        elif player is self.player2:
            other = self.player1
        if set(other.figure) & set(figure):
            return 'friend'
        return False
    def draw_game(self, W):
        size = ACTIVE_SETTINGS['size']
        offset = W.with_offset(W.w//2 - self.well.w//2*size, size*10)
        self.well.draw(offset)
        self.player2.draw(offset)
        self.player1.draw(offset)
        self.player2.draw_interface(offset)
    def do_check_lines(self, well, player):
        pass

    def do_drop(self):
        """ check lines and drop """
        full = self.well.get_full_line()#lấy hàng có đầy đủ khối 
        cleared = 0
        while full:
            self.well.remove_line(full)#xóa hàng
            self.player1.score_up()
            self.player1.speed_up()
            self.player2.score_up()
            self.player2.speed_up()
            #cả 2 đều được tăng score và tăng tốc độ
            full = self.well.get_full_line()
            cleared += 1

        simplified_pygame.mixer.play_sound(f'pop{min(4, cleared)}')
        self.player1.drop()
        self.player2.drop()



class TetrisSeqentialDrop(TetrisGameCoop):
    #có 2 người chơi, mỗi lượt chỉ có 1 người chơi
    def __init__(self, w=10, h=25):
        self.well1 = tetris.TetrisWell(self, w, h)
        self.well2 = tetris.TetrisWell(self, w, h)
        self.player1 = tetris.FallingFigure(self, self.well1, controlls=1)
        self.player2 = tetris.FallingFigure(self, self.well2, controlls=2)

        self.now_playing_1 = False
        self.player2.drop()

    def read_events(self, events, dt, key_pressed):
        if self.now_playing_1:
            self.player1.read_events(events, dt, key_pressed)
        else:
            self.player2.read_events(events, dt, key_pressed)

        self.well1.read_events(events, dt, key_pressed)
        self.well2.read_events(events, dt, key_pressed)

    def do_next_turn(self, player):
        self.now_playing_1 = not self.now_playing_1#chuyển sang người chưa chơi 
        self.do_drop()#

    def do_drop(self):
        if self.now_playing_1:
            self.player1.drop()
        else:
            self.player2.drop()


class TetrisHeartMode(TetrisSeqentialDrop):
    """
    Wells with the shared bottom.
    """
    #chuỗi docstring mô tả của lớp TetrisHeartMode
    def do_next_turn(self, player):
        if self.now_playing_1:
            self.well2.flip_copy_well(self.well1, reverse=True)
            self.now_playing_1 = False
        else:
            self.well1.flip_copy_well(self.well2)
            self.now_playing_1 = True
        self.do_drop()

    def draw_game(self, W):
        size = ACTIVE_SETTINGS['size']
        P1 = simplified_pygame.Canvas(10 * size, 20 * size, dy=5 * size)#tạo P1 có chiều cao bé hơn để tránh che mất khối hình của người chơi 1
        P2 = simplified_pygame.Canvas(10 * size, 30 * size, dy=5 * size)
        P3 = simplified_pygame.Canvas(10 * size, 30 * size, dy=5 * size)

        self.well2.draw(P2)
        self.player2.draw(P2)
        self.player2.draw_interface(W.with_offset(W.w//4 - self.well2.w//2*size, size*10))

        self.well1.draw(P1)
        self.player1.draw(P3)
        self.player1.draw_interface(W.with_offset(W.w//4*3 - self.well1.w//2*size, size*10))

        P3 = P3.rotate(-45)#xoay 45 độ cùng chiều kim đồng hồ
        P2 = P2.rotate(45)#xoay 45 độ ngược chiều kim đồng hồ
        P1 = P1.rotate(-45)#xoay 45 độ cùng chiều kim đồng hồ
        #P2 và P3 đối xứng
        dx = P2.w / 4
        x2 = W.w//2 - int(dx*3)
        x1 = W.w//2 - int(dx)
        x3 = W.w//2
        W.sprite(x3, size*5, P1)
        W.sprite(x2, size*5, P2)
        W.sprite(x1, size*5, P3)
