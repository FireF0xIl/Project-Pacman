import pygame
import random
import sys
import os


def load_image(name):
    fullname = os.path.join('data', name)
    try:
        return pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


def load_file(name):
    fullname = os.path.join('data', name)
    try:
        return open(fullname, mode="r").readlines()
    except FileNotFoundError as message:
        print('Cannot load file:', name)
        raise SystemExit(message)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
            # и подсчитываем максимальную длину
            maxWidth = max(map(len, level_map))
            # дополняем каждую строку пустыми клетками ('.')
            return list(map(lambda x: x.ljust(maxWidth, '.'), level_map))
    except FileNotFoundError:
        return None


def load_music(name):
    fullname = os.path.join('data\\Music', name)
    try:
        return pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load music:', name)
        raise SystemExit(message)


def terminate():
    end_music.stop()
    pygame.quit()
    sys.exit()


class Board:
    def __init__(self):
        self.level = 0
        self.board_size = board_size
        self.create_lvl()

    def create_lvl(self):
        food.empty()
        ghosts.empty()
        walls.empty()
        self.level += 1
        self.lvl = load_level("lvl" + str(self.level))
        if self.lvl is None:
            self.level = 1
            self.lvl = load_level("lvl" + str(self.level))

        for i in range(len(self.lvl)):
            for j in range(len(self.lvl[i])):
                if self.lvl[i][j] == ".":
                    rand = random.randint(0, 1000)
                    if rand >= 990:
                        flag = 2
                    elif rand >= 950:
                        flag = 1
                    else:
                        flag = 0
                    Food((j, i), flag)
                elif self.lvl[i][j] == pacman:
                    self.pacman = [j, i]
                elif self.lvl[i][j] == wall:
                    Wall((j, i))
                elif self.lvl[i][j] == enemy:
                    Ghost((j, i))

    def new_live(self):
        for ghost in ghosts:
            ghost.speed = 0
        pl.alive = False
        pl.speed = 0

    def create_new_live_board(self):
        self.create_board()
        pl.alive = True
        pl.speed = speed
        pygame.time.delay(500)
        main_music.play(-1)

    def create_board(self):
        cur_ghost = 0
        for i in range(len(self.lvl)):
            for j in range(len(self.lvl[i])):
                if self.lvl[i][j] == pacman:
                    pl.pos = [j, i]
                    pl.place = [left_side + pl.pos[0] * board_size, pl.pos[1] * board_size]
                    pl.rect.x, pl.rect.y = pl.place
                    pl.dead_cur_frame = 0
                    pl.way = "l"
                elif self.lvl[i][j] == enemy:
                    t = 0
                    for ghost in ghosts:
                        if t == cur_ghost:
                            ghost.pos = [j, i]
                            ghost.place = [left_side + ghost.pos[0] * board_size, ghost.pos[1] * board_size]
                            ghost.rect.x, ghost.rect.y = ghost.place
                            ghost.way = "l"
                            ghost.speed = speed
                            cur_ghost += 1
                            break
                        t += 1


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(player)
        '''
        self.way:
            l - go left
            r - go right
            u - go up
            d - go down
        '''
        self.ways = {276: "l", 275: "r", 274: "d", 273: "u"}
        self.way = "l"
        self.cur_way = self.way  # current way
        self.speed = speed
        self.lives = 3
        self.pos = pos
        self.place = [left_side + self.pos[0] * board_size, self.pos[1] * board_size]
        self.frames = []
        self.dead_frames = []
        self.cut_sheet(load_image("pacman_r6.png"), 1, 6, True)
        self.cur_frame = 0
        self.open = True
        self.image = self.frames[self.cur_frame]
        self.cut_sheet(load_image("pacman_d_right.png"), 1, 10, False)
        self.dead_cur_frame = 0
        self.alive = True

    def cut_sheet(self, sheet, columns, rows, main):
        self.rect = pygame.Rect(self.place[0], self.place[1], sheet.get_width() // columns, sheet.get_height() // rows)
        if self.rect.width != self.rect.height:
            self.rect.width, self.rect.height = min(self.rect.width, self.rect.height), min(self.rect.width,
                                                                                            self.rect.height)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                if main:
                    self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
                else:
                    self.dead_frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def turn_image(self):
        if self.way == "l":
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.way == "d":
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.way == "u":
            self.image = pygame.transform.rotate(self.image, 90)

    def change_way(self):
        try:
            if self.cur_way == "r" and board.lvl[self.pos[1]][self.pos[0] + 1] != wall:  # ->
                self.way = "r"
                self.speed = speed
            elif self.cur_way == "l" and board.lvl[self.pos[1]][self.pos[0] - 1] != wall:  # <-
                self.way = "l"
                self.speed = speed
            elif self.cur_way == "d" and board.lvl[self.pos[1] + 1][self.pos[0]] != wall:  # \/
                self.way = "d"
                self.speed = speed
            elif self.cur_way == "u" and board.lvl[self.pos[1] - 1][self.pos[0]] != wall:  # ^
                self.way = "u"
                self.speed = speed
        except Exception:
            pass

    def check_way(self):
        try:
            if self.way == "l" and board.lvl[self.pos[1]][self.pos[0] - 1] == wall:
                self.speed = 0
            elif self.way == "r" and board.lvl[self.pos[1]][self.pos[0] + 1] == wall:
                self.speed = 0
            elif self.way == "d" and board.lvl[self.pos[1] + 1][self.pos[0]] == wall:
                self.speed = 0
            elif self.way == "u" and board.lvl[self.pos[1] - 1][self.pos[0]] == wall:
                self.speed = 0
        except Exception:
            pass

    def hot_change_way(self):
        if (self.way == "l" and self.cur_way == "r") or (self.way == "r" and self.cur_way == "l"):
            self.way = self.cur_way
        elif (self.way == "d" and self.cur_way == "u") or (self.way == "u" and self.cur_way == "d"):
            self.way = self.cur_way

    def render(self):
        self.rect.x, self.rect.y = self.place[0], self.place[1]
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            if not ((self.rect.y == 0 and self.way != "u") or (self.rect.bottom == height and self.way != "d")):
                self.speed = 0
        if pygame.sprite.spritecollideany(self, vertical_borders):
            if not ((self.rect.x == left_side and self.way != "l") or (
                    self.rect.right == width - left_side and self.way != "r")):
                self.speed = 0
        if pygame.sprite.spritecollideany(self, ghosts):
            for i in ghosts:
                if i.pos == self.pos and self.alive:
                    main_music.stop()
                    if self.lives == 0:
                        end_music.play(-1)
                        Gameover()
                    else:
                        death_music.play()
                        self.lives -= 1
                        stats.pacman_lives()
                        board.new_live()

        if self.way == "l":
            self.place[0] -= self.speed
        elif self.way == "r":
            self.place[0] += self.speed
        elif self.way == "u":
            self.place[1] -= self.speed
        elif self.way == "d":
            self.place[1] += self.speed
        if self.way == "r" and self.place[0] % board_size > board_size // 4 and self.pos[0] * board_size + left_side < \
                self.place[0]:
            self.pos[0] += 1
        elif self.way == "l" and self.place[0] % board_size < board_size // 4 and self.pos[0] * board_size + left_side > \
                self.place[0]:
            self.pos[0] -= 1
        elif self.way == "d" and self.place[1] % board_size > board_size // 4 and self.pos[1] * board_size < self.place[
            1]:
            self.pos[1] += 1
        elif self.way == "u" and self.place[1] % board_size < board_size // 4 and self.pos[1] * board_size > self.place[
            1]:
            self.pos[1] -= 1
        if self.alive:
            self.hot_change_way()
            if self.place[0] % board_size == 0 and self.place[1] % board_size == 0:
                self.check_way()
                self.change_way()

    def next_lvl(self):
        self.pos = board.pacman
        self.way = "l"
        self.place = [left_side + self.pos[0] * board_size, self.pos[1] * board_size]
        self.rect.x, self.rect.y = self.place[0], self.place[1]
        pygame.time.delay(500)

    def change_frame(self):
        if self.alive:
            if self.cur_frame + 1 == len(self.frames):
                self.open = False
            elif self.cur_frame == 0:
                self.open = True
            if self.open:
                self.cur_frame += 1
            else:
                self.cur_frame -= 1
        else:
            self.dead_cur_frame += 1

    def update(self, event):
        if event:
            self.change_frame()
            if self.alive:
                self.image = self.frames[self.cur_frame]
            else:
                self.image = self.dead_frames[self.dead_cur_frame]
            self.turn_image()
        try:
            self.cur_way = self.ways[event.key]
        except Exception:
            pass


class Ghost(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__(ghosts)
        '''
        self.way:
            l - go left
            r - go right
            u - go up
            d - go down
        '''
        self.ways = {276: "l", 275: "r", 274: "d", 273: "u"}
        self.random_ways = ["l", "r", "d", "u"]
        self.way = "l"
        self.speed = speed
        self.alarm = False  # if pacman has hero mode
        self.pos = list(pos[:])
        self.place = [left_side + self.pos[0] * board_size, self.pos[1] * board_size]

        self.frames = []
        self.image = load_image("ghost_blue_u.png")
        self.rect = pygame.Rect(left_side + self.pos[0] * board_size, self.pos[1] * board_size,
                                self.image.get_width(), self.image.get_height())

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(left_side + self.pos[0] * 40, self.pos[1] * 40, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        if self.rect.width != self.rect.height:
            self.rect.width, self.rect.height = min(self.rect.width, self.rect.height), min(self.rect.width,
                                                                                            self.rect.height)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def check_way(self):
        try:
            if self.way == "l" and (self.pos[0] - 1 <= 0 or board.lvl[self.pos[1]][self.pos[0] - 1] == "#"):
                return True
            elif self.way == "r" and (
                    self.pos[0] + 1 >= len(board.lvl) or board.lvl[self.pos[1]][self.pos[0] + 1] == "#"):
                return True
            elif self.way == "d" and (
                    self.pos[1] + 1 >= len(board.lvl) or board.lvl[self.pos[1] + 1][self.pos[0]] == "#"):
                return True
            elif self.way == "u" and (self.pos[1] - 1 <= 0 or board.lvl[self.pos[1] - 1][self.pos[0]] == "#"):
                return True
            return False
        except Exception:
            return True

    def check_random(self):

        if self.way == "l" and self.pos[1] - 1 < 0:
            return True
        elif self.way == "r" and self.pos[1] + 1 > 19:
            return True
        elif self.way == "d" and self.pos[0] + 1 > 19:
            return True
        elif self.way == "u" and self.pos[0] - 1 < 0:
            return True
        return False

    def change_way(self):
        tmp = self.random_ways[:]
        tmp = tmp[:tmp.index(self.way)] + tmp[tmp.index(self.way) + 1:]
        try:
            if abs(self.pos[0] - pl.pos[0]) < abs(self.pos[1] - pl.pos[1]):
                if self.pos[1] - pl.pos[1] > 0:
                    if board.lvl[self.pos[1]][self.pos[0] - 1] != "#":
                        self.way = "u"
                    else:
                        self.way = random.choice(tmp)
                else:
                    if board.lvl[self.pos[1]][self.pos[0] + 1] != "#":
                        self.way = "d"
                    else:
                        self.way = random.choice(tmp)
            else:
                if self.pos[0] - pl.pos[0] > 0:
                    if board.lvl[self.pos[1]][self.pos[0] - 1] != "#":
                        self.way = "l"
                    else:
                        self.way = random.choice(tmp)
                else:
                    if board.lvl[self.pos[1]][self.pos[0] + 1] != "#":
                        self.way = "r"
                    else:
                        self.way = random.choice(tmp)
            if self.check_way() or self.check_random():
                raise Exception
        except Exception:
            i = 0
            while self.check_way():
                self.way = self.random_ways[i]
                i += 1

    def update(self):
        if self.way == "l":
            self.rect.x -= self.speed
            self.place[0] -= self.speed
        elif self.way == "r":
            self.rect.x += self.speed
            self.place[0] += self.speed
        elif self.way == "u":
            self.rect.y -= self.speed
            self.place[1] -= self.speed
        elif self.way == "d":
            self.rect.y += self.speed
            self.place[1] += self.speed
        if self.way == "r" and self.place[0] % board_size > board_size // 4 and self.pos[0] \
                * board_size + left_side < self.place[0]:
            self.pos[0] += 1
        elif self.way == "l" and self.place[0] % board_size < board_size // 4 and self.pos[0] \
                * board_size + left_side > self.place[0]:
            self.pos[0] -= 1
        elif self.way == "d" and self.place[1] % board_size > board_size // 4 and self.pos[1] \
                * board_size < self.place[1]:
            self.pos[1] += 1
        elif self.way == "u" and self.place[1] % board_size < board_size // 4 and self.pos[1] \
                * board_size > self.place[1]:
            self.pos[1] -= 1

        if self.place[0] % board_size == 0 and self.place[1] % board_size == 0:
            if self.check_way():
                self.change_way()
        elif (self.place[0] % board_size == 0 and self.place[1] % board_size == 0) and (
                pygame.sprite.spritecollideany(self, vertical_borders) or pygame.sprite.spritecollideany(self,
                                                                                                         horizontal_borders)):
            self.change_way()


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(walls)
        self.pos = pos[:]
        self.image = load_image("brick.png")
        self.rect = pygame.Rect(left_side + self.pos[0] * 40, self.pos[1] * 40, self.image.get_width(),
                                self.image.get_height())


class Food(pygame.sprite.Sprite):
    def __init__(self, pos, flag):
        super().__init__(food)
        self.flag = flag
        self.pos = pos[:]
        self.place = [left_side + self.pos[0] * board_size, self.pos[1] * board_size]
        self.frames = []
        self.cur_frame = 0
        if flag == 0:
            self.score = 10
            self.cut_sheet(load_image("food2.png"), 3, 1)
        elif flag == 1:
            self.score = 100
            self.cut_sheet(load_image("orange.png"), 1, 5)
        elif flag == 2:
            self.score = 1000
            self.cut_sheet(load_image("banana.png"), 1, 7)
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(left_side + self.pos[0] * board_size, self.pos[1] * board_size,
                                sheet.get_width() // columns, sheet.get_height() // rows)
        if self.rect.width != self.rect.height:
            self.rect.width, self.rect.height = min(self.rect.width, self.rect.height), \
                                                min(self.rect.width, self.rect.height)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def change_frame(self):
        if self.flag != 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

    def update(self, event=False):
        if event == True:
            self.change_frame()

        if pygame.sprite.spritecollideany(self, player):
            if self.place == pl.place:
                stats.add_score(self.score)
                food.remove(self)


class Stats_board:
    def __init__(self):
        self.score = 0
        self.text = []
        self.text_rect = []
        self.text_color = pygame.Color("white")
        self.font_color = pygame.Color("gray")
        self.text.append("Score:")
        self.text_rect.append(pygame.Rect(40, 20, 160, 60))
        self.text.append(str(self.score).rjust(6, "0"))
        self.text_rect.append(pygame.Rect(50, 80, 100, 50))
        self.lvl = 1
        self.space = 50
        self.pacman_image = pygame.transform.scale(load_image("pacman_live.png"), (40, 40))
        self.pacman_space = 45
        self.lives_text = "Lives:"
        self.lives_rect = pygame.Rect(40, 550, 140, 60)
        self.open_high_score()

    def render(self, surface):
        for i in range(len(self.text)):
            font = pygame.font.Font(None, self.text_rect[i].height - 4)
            self.rendered_text = font.render(self.text[i], 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(x=self.text_rect[i].x + 2,
                                                             centery=self.text_rect[i].centery + self.space * (i // 2))
            surface.blit(self.rendered_text, self.rendered_rect)
        if start:
            font = pygame.font.Font(None, self.lives_rect.height - 4)
            self.rendered_text = font.render(self.lives_text, 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(x=self.lives_rect.x + 2, centery=self.lives_rect.centery)
            surface.blit(self.rendered_text, self.rendered_rect)
            for i in range(self.lives):
                rect = self.lives_rect.copy()
                rect.x, rect.y = self.lives_rect.right - 60 - i * self.pacman_space, self.lives_rect.bottom
                surface.blit(self.pacman_image, rect)

    def open_high_score(self):
        file = load_file("High score")
        self.text.append("High Score:")
        self.text_rect.append(pygame.Rect(1020, 20, 80, 50))
        for i in range(len(file)):
            text = file[i].rstrip().split()
            self.text.append(text[0])
            self.text.append(text[1])
            self.text_rect.append(pygame.Rect(1050, 60 + (self.space * (i)) // 2, 80, 40))
            self.text_rect.append(pygame.Rect(1050, 40 + (self.space * (i)) // 2, 80, 40))

    def add_score(self, score):
        self.score += score
        self.text[1] = str(self.score).rjust(6, "0")

    def pacman_lives(self):
        self.lives = pl.lives


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
        self.image.fill(pygame.Color("blue"))


class Gameover(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(gameover)
        self.rect = pygame.Rect(width - left_side, 0, width - 2 * left_side, height)
        self.image = pygame.transform.scale(load_image("gameover.png"), (width - 2 * left_side, height))
        self.end = False

    def update(self):
        if self.rect.x != left_side:
            self.rect.x -= 5
        else:
            self.end = True

pygame.init()
width, height = 1200, 800
screen_size = (width, height)

screen = pygame.display.set_mode(screen_size)
screen.fill(pygame.Color("black"))

pygame.mixer.init()
pygame.mixer.music.set_volume(2.0)
begin_music = load_music("pacman_beginning.wav")
main_music = load_music("pacman_chomp.wav")
death_music = load_music("pacman_death.wav")
end_music = load_music("pacman_intermission.wav")

fps = 50
clock = pygame.time.Clock()
left_side = 200
board_size = 40
speed = 2
wall = "#"
pacman = "@"
enemy = "$"

all_sprites = pygame.sprite.Group()
gameover = pygame.sprite.Group()
wingame = pygame.sprite.Group()
ghosts = pygame.sprite.Group()
player = pygame.sprite.Group()
walls = pygame.sprite.Group()
food = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
lives = pygame.sprite.Group()


Border(left_side, 0, width - left_side, 0)
Border(left_side, height - 1, width - left_side, height - 1)
Border(left_side, 0, left_side, height)
Border(width - 201, 0, width - 201, height)

eat = pygame.USEREVENT + 1
time = 200
pygame.time.set_timer(eat, time)

blink = pygame.USEREVENT + 2
blink_time = 150
pygame.time.set_timer(blink, blink_time)

stats = Stats_board()

running = True
start = False
pre_game_rect = pygame.Rect(225, 650, 400, 95)
pre_game_text = "Press any button to start"
begin_music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            terminate()

        if event.type == pygame.KEYDOWN and not start:
            begin_music.stop()
            main_music.play(-1)
            start = True
            board = Board()
            pl = Player(board.pacman)
            stats.pacman_lives()

        if event.type == pygame.KEYDOWN:
            player.update(event)

        if event.type == eat:
            player.update(True)

        if event.type == blink:
            food.update(True)

        if start and not pl.alive and pl.dead_cur_frame == len(pl.dead_frames) - 1:
            board.create_new_live_board()

        if start and len(food) == 0:
            board.create_lvl()
            pl.next_lvl()
    screen.fill(pygame.Color("black"))

    if not start:
        font = pygame.font.Font(None, pre_game_rect.height - 4)
        rendered_text = font.render(pre_game_text, 1, pygame.Color("Grey"))
        rendered_rect = rendered_text.get_rect(x=pre_game_rect.x + 2, centery=pre_game_rect.centery)
        screen.blit(rendered_text, rendered_rect)

    horizontal_borders.draw(screen)
    vertical_borders.draw(screen)
    food.draw(screen)
    ghosts.draw(screen)
    player.draw(screen)
    walls.draw(screen)
    if len(gameover) == 0 and start:
        food.update()
        ghosts.update()
        pl.render()
    stats.render(screen)
    gameover.update()
    gameover.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
