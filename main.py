import sys
import pygame
import os
import pprint

map_file_name = input()
pygame.init()
size = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(size)
FPS = 50


def load_image(name, colorkey=None):  # функция обработки картинки
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):  # обработка отсутствия картинки
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:  # замена выбранного цвета на прозрачный
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    if not os.path.exists(filename):
        print(f'Файла {filename} не существует')
        terminate()

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    global max_width
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Перемещение героя", "",
                  "Новый уровень"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.x = pos_x
        self.y = pos_y

    def swap(self, x, y):
        self.rect.x = tile_width * self.x + (x * tile_width) - WIDTH // 2
        self.rect.y = tile_height * self.y + (y * tile_height) - HEIGHT // 2


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def update(self, *args) -> None:
        for event in args:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT and list(map_list)[self.pos_y][self.pos_x - 1] != '#':
                    for i in range(max_width):
                        map_list[i] = map_list[i][-1] + map_list[i][:-1]
                elif event.key == pygame.K_RIGHT:
                    if self.pos_x < 9 and map_list[self.pos_y][self.pos_x + 1] != '#':
                        for i in range(max_width):
                            map_list[i] += map_list[i][0]
                            map_list[i] = map_list[i][1:]
                    elif self.pos_x == 9 and map_list[self.pos_y][0] != '#':
                        for i in range(max_width):
                            map_list[i] += map_list[i][0]
                            map_list[i] = map_list[i][1:]

                elif event.key == pygame.K_UP and list(map_list)[self.pos_y - 1][self.pos_x] != '#':
                    map_list.insert(0, map_list[-1])
                    map_list.pop(-1)

                elif event.key == pygame.K_DOWN:
                    if self.pos_y < 9 and map_list[self.pos_y + 1][self.pos_x] != '#':
                        map_list.append(map_list[0])
                        map_list.pop(0)
                    elif self.pos_y == 9 and map_list[0][self.pos_x] != '#':
                        map_list.append(map_list[0])
                        map_list.pop(0)

        for i in tiles_group:
            i.kill()
        for y in range(len(map_list)):
            for x in range(len(map_list[y])):
                if map_list[y][x] == '#':
                    Tile('wall', x, y)
                elif map_list[y][x] == '.' or map_list[y][x] == '@':
                    Tile('empty', x, y)


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
clock = pygame.time.Clock()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.swap(self.dx, self.dy)

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = level_x - target.pos_x
        self.dy = level_y - target.pos_y


max_width = 0
player, level_x, level_y = generate_level(load_level(map_file_name))
map_list = load_level(map_file_name)
running = True
camera = Camera()
pygame.display.set_caption('Перемещение героя. Новый уровень')
start_screen()
while running:
    screen.fill((0, 0, 0))
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    player_group.update(*events)
    all_sprites.draw(screen)

    camera.update(player)
    for sprite in tiles_group:
        camera.apply(sprite)
    player_group.draw(screen)
    pygame.display.flip()
terminate()

