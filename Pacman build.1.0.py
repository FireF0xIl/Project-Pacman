import pygame
import os
import sys
import random


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        return pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


def terminate():
    pygame.quit()
    sys.exit()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    maxWidth = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(maxWidth, '.'), level_map))


class Board:
    def __init__(self):
        self.level = 1
        self.lvl = load_level("lvl" + str(self.level))
        self.board_size = 40
        for i in range(len(self.lvl)):
            for j in range(len(self.lvl[i])):
                if self.lvl[i][j] == ".":
                    rand = random.randint(0, 100)
                    if rand >= 99:
                        flag = 2
                    elif rand >= 90:
                        flag = 1
                    else:
                        flag = 0
                    Food((j, i), flag)
                elif self.lvl[i][j] == "@":
                    self.pacman = [j, i]
                elif self.lvl[i][j] == "#":
                    Wall((j, i))
                elif self.lvl[i][j] == "$":
                    Ghost((j, i))


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
        self.speed = 2
        self.lives = 3

        self.pos = pos[:]
        self.place = [left_side + self.pos[0] * board_size, self.pos[1] * board_size]
        self.frames = []
        self.cut_sheet(load_image("pacman_r6.png"), 1, 6)
        self.cur_frame = 0
        self.open = True
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.place[0], self.place[1], sheet.get_width() // columns, sheet.get_height() // rows)
        if self.rect.width != self.rect.height:
            self.rect.width, self.rect.height = min(self.rect.width, self.rect.height), min(self.rect.width,
                                                                                            self.rect.height)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def turn_image(self):
        if self.way == "l":
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.way == "d":
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.way == "u":
            self.image = pygame.transform.rotate(self.image, 90)

    def change_way(self):
        try:
            if self.cur_way == "r" and board.lvl[self.pos[1]][self.pos[0] + 1] != "#":  # ->
                self.way = "r"
                self.speed = 2
                self.change_frame()
            elif self.cur_way == "l" and board.lvl[self.pos[1]][self.pos[0] - 1] != "#":  # <-
                self.way = "l"
                self.speed = 2
            elif self.cur_way == "d" and board.lvl[self.pos[1] + 1][self.pos[0]] != "#":  # \/
                self.way = "d"
                self.speed = 2
            elif self.cur_way == "u" and board.lvl[self.pos[1] - 1][self.pos[0]] != "#":  # ^
                self.way = "u"
                self.speed = 2
        except Exception:
            pass

    def check_way(self):
        try:
            if self.way == "l" and board.lvl[self.pos[1]][self.pos[0] - 1] == "#":
                self.speed = 0
            elif self.way == "r" and board.lvl[self.pos[1]][self.pos[0] + 1] == "#":
                self.speed = 0
            elif self.way == "d" and board.lvl[self.pos[1] + 1][self.pos[0]] == "#":
                self.speed = 0
            elif self.way == "u" and board.lvl[self.pos[1] - 1][self.pos[0]] == "#":
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
                if i.pos == self.pos:
                    Gameover()
        if self.way == "l":
            self.place[0] -= self.speed
        elif self.way == "r":
            self.place[0] += self.speed
        elif self.way == "u":
            self.place[1] -= self.speed
        elif self.way == "d":
            self.place[1] += self.speed
        if self.way == "r" and self.place[0] % board_size > board_size / 2 and self.pos[0] * board_size + left_side < \
                self.place[0]:
            self.pos[0] += 1
        elif self.way == "l" and self.place[0] % board_size < board_size / 2 and self.pos[0] * board_size + left_side > \
                self.place[0]:
            self.pos[0] -= 1
        elif self.way == "d" and self.place[1] % board_size > board_size / 2 and self.pos[1] * board_size < self.place[
            1]:
            self.pos[1] += 1
        elif self.way == "u" and self.place[1] % board_size < board_size / 2 and self.pos[1] * board_size > self.place[
            1]:
            self.pos[1] -= 1
        self.hot_change_way()
        if self.place[0] % board_size == 0 and self.place[1] % board_size == 0:
            self.check_way()
            self.change_way()

    def change_frame(self):
        if self.cur_frame + 1 == len(self.frames):
            self.open = False
        elif self.cur_frame == 0:
            self.open = True
        if self.open:
            self.cur_frame += 1
        else:
            self.cur_frame -= 1

    def update(self, event):
        if event:
            self.change_frame()
            self.image = self.frames[self.cur_frame]
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
        self.speed = 2
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

    def first_init(self):
        self.change_way()

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
        if self.way == "r" and self.place[0] % board_size > board_size / 2 and self.pos[0] \
                * board_size + left_side < self.place[0]:
            self.pos[0] += 1
        elif self.way == "l" and self.place[0] % board_size < board_size / 2 and self.pos[0] \
                * board_size + left_side > self.place[0]:
            self.pos[0] -= 1
        elif self.way == "d" and self.place[1] % board_size > board_size / 2 and self.pos[1] \
                * board_size < self.place[1]:
            self.pos[1] += 1
        elif self.way == "u" and self.place[1] % board_size < board_size / 2 and self.pos[1] \
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
        # for i in walls:
        #   i.rect.x == x and i.rect.y == y:
        #      walls.remove(i)


class Food(pygame.sprite.Sprite):
    def __init__(self, pos, flag):
        super().__init__(food)
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
            self.score = 200
            self.cut_sheet(load_image("banana.png"), 1, 7)
        self.image = self.frames[self.cur_frame]

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

    def change_frame(self):
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
        self.open_high_score()

    def render(self, surface):
        for i in range(len(self.text)):
            font = pygame.font.Font(None, self.text_rect[i].height - 4)
            self.rendered_text = font.render(self.text[i], 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(x=self.text_rect[i].x + 2,
                                                             centery=self.text_rect[i].centery + self.space * (i // 2))
            surface.blit(self.rendered_text, self.rendered_rect)

    def open_high_score(self):
        file = open("data\High score", mode="r").readlines()
        self.text.append("High Score:")
        self.text_rect.append(pygame.Rect(1020, 20, 80, 50))
        for i in range(len(file)):
            text = file[i].rstrip().split()
            self.text.append(text[0])
            self.text.append(text[1])
            self.text_rect.append(pygame.Rect(1020, 40 + self.space * (i + 1*i), 80, 40))
            self.text_rect.append(pygame.Rect(1020, 40 + self.space * (i + 2*i), 80, 40))

        print(file)

    def add_score(self, score):
        self.score += score
        self.text[1] = str(self.score).rjust(6, "0")


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

        self.rect = pygame.Rect(width - left_side, 0, 800, height)
        self.image = pygame.transform.scale(load_image("gameover.png"), (800, 800))

    def update(self):
        if self.rect.x != 200:
            self.rect.x -= 5


pygame.init()
width, height = 1200, 800
screen_size = (width, height)

screen = pygame.display.set_mode(screen_size)
screen.fill(pygame.Color("white"))

fps = 50
clock = pygame.time.Clock()
left_side = 200
board_size = 40
wall = "#"

all_sprites = pygame.sprite.Group()
gameover = pygame.sprite.Group()
ghosts = pygame.sprite.Group()
player = pygame.sprite.Group()
walls = pygame.sprite.Group()
food = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
lives = pygame.sprite.Group()

Border(left_side, 0, width - 200, 0)
Border(left_side, height - 1, width - 200, height - 1)
Border(left_side, 0, left_side, height)
Border(width - 201, 0, width - 201, height)

eat = pygame.USEREVENT + 1
time = 200
pygame.time.set_timer(eat, time)

blink = pygame.USEREVENT + 2
blink_time = 1000
pygame.time.set_timer(blink, blink_time)

stats = Stats_board()

running = True
start = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            terminate()
        if event.type == pygame.KEYDOWN and not start:
            start = True
            board = Board()
            pl = Player(board.pacman)
        if event.type == pygame.KEYDOWN:
            player.update(event)

        if event.type == eat:
            player.update(True)
        if event.type == blink:
            food.update(True)
    player.draw(screen)
    screen.fill(pygame.Color("black"))
    # pygame.draw.rect(screen, pygame.Color("red"), (500, 0, 50, 50))
    # pygame.draw.rect(screen, pygame.Color("red"), (0, 0, 200, height))
    # pygame.draw.rect(screen, pygame.Color("red"), (width - 200, 0, 200, height))

    # board.render()
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
