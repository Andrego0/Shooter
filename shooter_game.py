from random import randint
from typing import Any
from pygame import *
import pickle
init()
mixer.init()
font.init()
#створи вікно гри
screen_info = display.Info()
WIDTH, HEIGHT = screen_info.current_w,screen_info.current_h
FPS = 120

font1 = font.SysFont("Arial", 40)
font2 = font.SysFont("Arial", 55)

mixer.music.load("ObservingTheStar.ogg")
mixer.music.set_volume(0.4)
mixer.music.play(loops=-1)

fire_sound = mixer.Sound('laser3.wav')

flags= FULLSCREEN

window = display.set_mode((WIDTH, HEIGHT), flags) #створюємо вікно 
display.set_caption("Maze")
clock = time.Clock() # Створюємо ігровий таймер

#задай фон сцени
bg = image.load("infinite_starts.jpg") # завантажуємо картинку в гру
bg = transform.scale(bg, (WIDTH, HEIGHT)) #змінюємо розмір картинки
bg_y1 = 0
bg_y2 = -HEIGHT

player_img = image.load('MK 1K.png')
bullet_img = image.load('Laser01.png')
enemy_img = image.load('blue_ufo_gmc_0022.png')
asteroid_img = image.load('meteor4.png')

sprites = sprite.Group()

class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, width, height, x, y):
        super().__init__()
        self.image = transform.scale(sprite_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)
        sprites.add(self)

    def draw(self, window):
        window.blit(self.image, self.rect)

class Player(GameSprite):
    def __init__(self, sprite_image, width, height, x, y):
        super().__init__(sprite_image, width, height, x, y)
        self.hp = 100
        self.damage = 20
        self.points = 0
        self.speed = 5
        self.bg_speed = 2

    def update(self):
        global hp_textda
        self.old_pos = self.rect.x, self.rect.y
        
        keys = key.get_pressed() #отримуємо список натиснутих клавіш
        if keys[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
            self.bg_speed = 4
        elif keys[K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            self.bg_speed = 1
        else:
            self.bg_speed = 2
        if keys[K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.right < WIDTH    :
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(self.rect.centerx, self.rect.y)
        fire_sound.play()

enemys = sprite.Group()

class Enemy(GameSprite):
    def __init__(self):
        rand_x = randint(0, WIDTH-70)
        y = -150 
        super().__init__(enemy_img, 100, 70, rand_x, y)
        self.speed = 2
        enemys.add(self)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()
asteroids = sprite.Group()

class Asteroid(GameSprite):
    def __init__(self):
        rand_x = randint(0, WIDTH-70)
        y = -150 
        super().__init__(asteroid_img, 100, 70, rand_x, y)
        self.speed = 2
        asteroids.add(self)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()

bullets = sprite.Group()

class Bullet(GameSprite):
    def __init__(self, player_x, player_y):
        super().__init__(bullet_img, 20, 40, player_x, player_y)
        self.rect.centerx = player_x
        self.rect.bottom = player_y
        self.speed = 5
        bullets.add(self)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

player = Player(player_img, 100, 100,  300, 300)

hp_text = font1.render(f"HP: {player.hp}", True, (255, 255, 255))
point_text = font1.render(F"Points: {player.points}", True, (255, 255, 255))
finish_text = font2.render("GAME OVER", True, (255, 0, 0))

finish = False
Enemy()
last_spawn_time = time.get_ticks()
spawn_interval = randint(1000, 5000)
last_spawn_asteroid = time.get_ticks()
spawn_interval_asteroid = randint(3000, 5000)
max_points = 0
max_point_text = font1.render(F"Max score: {max_points}", True, (255, 255, 255))
def save_max_points():
    with open("save.dat", "wb") as file:
        pickle.dump(max_points, file)

while True:
    #оброби подію «клік за кнопкою "Закрити вікно"
    for e in event.get():
        if e.type == QUIT:
            quit()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                quit()
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                player.fire()


    if not finish:
        now = time.get_ticks()
        if now - last_spawn_time > spawn_interval:
            Enemy()
            last_spawn_time = time.get_ticks()
            spawn_interval = randint(1000, 1500)

        if now - last_spawn_asteroid > spawn_interval_asteroid:
            Asteroid()
            last_spawn_asteroid = time.get_ticks()
            spawn_interval_asteroid = randint(3000, 5000)

        bullets_collide = sprite.groupcollide(bullets, enemys, True, True, sprite.collide_mask)
        for enemy in bullets_collide:
            player.points += 1
            point_text = font1.render(F"Points: {player.points}", True, (255, 255, 255))
            if player.points > max_points:
                max_points = player.points
                max_point_text = font1.render(F"Max score: {max_points}", True, (255, 255, 255))
                save_max_points()
        collide_list = sprite.spritecollide(player, enemys, False, sprite.collide_mask)
        sprites.update()

        for enemy in collide_list:
            player.hp -= 50
            hp_text = font1.render(f"HP: {player.hp}", True, (255, 255, 255))
            enemys.remove(enemy)

        collide_list = sprite.spritecollide(player, asteroids, False, sprite.collide_mask)
        bullets_collide = sprite.groupcollide(bullets, asteroids, True, False, sprite.collide_mask)
        for asteroid in collide_list:
            player.hp = 0
            hp_text = font1.render(f"HP: {player.hp}", True, (255, 255, 255))
            finish = True

        if player.hp <= 0:
            finish = True

        window.blit(bg, (0,bg_y1))
        window.blit(bg, (0,bg_y2))
        bg_y1 += player.bg_speed
        bg_y2 += player.bg_speed
        if bg_y1 > HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 > HEIGHT:
            bg_y2 = -HEIGHT
    sprites.draw(window)
    window.blit(hp_text, (10,10))
    window.blit(point_text, (WIDTH-200,10))
    if finish:
        window.blit (finish_text, (WIDTH/2-125, HEIGHT/2-50))
    display.update()
    clock.tick(FPS)