import random

import pygame
import os
import sys

FPS = 60
all_sprites = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    else:
        image = image.convert_alpha()
        return image


def terminate():
    print("exit")
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tiles_group):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

        if tile_type == 'wall':
            self.add(box_group, tiles_group, all_sprites)
        else:
            self.add(tiles_group, all_sprites)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, player_group):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move_down(self):
        self.rect = self.rect.move(0, +50)

    def move_up(self):
        self.rect = self.rect.move(0, -50)

    def move_right(self):
        self.rect = self.rect.move(+50, 0)

    def move_left(self):
        self.rect = self.rect.move(-50, 0)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


# группы:
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()


def generate_level(level):
    global tiles_group, player_group

    new_player, x, y = None, None, None

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, tiles_group)
            elif level[y][x] == '#':
                Tile('wall', x, y, tiles_group)
            elif level[y][x] == '@':
                Tile('empty', x, y, tiles_group)
                new_player = Player(x, y, player_group)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def play_level():
    player, x, y = generate_level(load_level('map_1.txt'))

    global tiles_group, player_group, box_group
    running = True
    while running:
        pos = (0, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    player.move_down()
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.move_up()
                elif event.key == pygame.K_UP:
                    player.move_up()
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.move_down()
                elif event.key == pygame.K_LEFT:
                    player.move_left()
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.move_right()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()
                    if pygame.sprite.spritecollideany(player, box_group):
                        player.move_left()

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        player_group.draw(screen)
        player.update(pos)

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        pygame.display.flip()
        clock.tick(FPS)


pygame.init()
pygame.display.set_caption('Перемешение героя')
size = width, height = 640, 480
screen = pygame.display.set_mode(size, 0, 32)
# pygame.mouse.set_visible(0)

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass_1.png')
}

player_image = load_image('mar.png')

tile_width = tile_height = 50

clock = pygame.time.Clock()
camera = Camera()

while True:
    start_screen()
    play_level()