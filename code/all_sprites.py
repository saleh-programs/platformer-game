import pygame
from pygame.math import Vector2 as vector
from Settings import *
from random import choice,randint
from timer import Timer
from support import *
from math import sqrt
from transition import *
# blocks
class Generic(pygame.sprite.Sprite):
    def __init__(self, group,pos,surf):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
class animated(Generic):
    def __init__(self, group,pos,surf,killable = False):
        super().__init__(group,pos,surf[0])
        self.image = surf[0]
        self.rect = self.image.get_rect(midbottom = pos)

        # animation
        self.frame_index = 0
        self.frames = surf
        self.pos = vector(pos)
        self.killable = killable
        self.go = False
        self.hitbox = False
        self.attack_rect = None
    def move(self,dt):
        keys = pygame.key.get_pressed()
        if int(self.frame_index) >= 11:
            self.pos.x += 330 * dt
            self.rect.centerx = round(self.pos.x)
    def animate(self,dt):
        self.frame_index += 23 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            self.go = False
            if self.killable:
                self.kill()
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=self.pos)

    def update(self,dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.go = True
        if self.go:
            self.animate(dt)
        #self.move(dt)
class text_bubble(Generic):
    def __init__(self, group,pos,graphics):
        super().__init__(group,pos,graphics)

        # animation
        self.frames = graphics
        self.frame_index = 0

        self.iters = 0

        self.display_surface = pygame.display.get_surface()
        self.txt_file = '../hello.txt'

        # store text (kinda static)
        txt = open(self.txt_file, 'r')
        self.var = txt.read()
        txt.close()

        self.list = import_list('../graphics/text2')

        self.startx, self.x = pos[0] + 30, pos[0] + 30
        self.starty, self.y = pos[1] + 10, pos[1] + 10

    def draw_words(self,dt,offset):

        self.x = self.startx
        self.y = self.starty
        for i in range(round(self.iters)):

            if self.var[i] != ' ':
                self.display_surface.blit(self.list[self.var[i]], (self.x, self.y) - offset)
                self.x += self.list[self.var[i]].get_width()+1

                #self.display_surface.blit(self.list[var[i]], (self.startx, self.starty) - offset)
            else:
                self.x += 6

            if (self.x > self.startx + self.rect.width - 70) and self.var[i] == ' ':
                self.x = self.startx
                self.y += 8
            if self.y > self.starty + self.rect.height - 10:
                self.y = self.starty

        self.iters += 10 * dt

        if self.iters > len(self.var):
            self.iters = 0
            self.x = self.startx
            self.y = self.starty
class Grappling_Hook(Generic):
    def __init__(self,group,collision_group,pos):
        self.frames = import_list('../graphics/items/hook')
        super().__init__(group,pos,self.frames['0'])
        self.pos = vector(pos)
        self.rect = self.image.get_rect(midbottom = pos)
        self.collision_group = collision_group
        self.hitbox = False
        self.attack_rect = None
        self.degree = 0
    def rotate(self):
        percent_of_rotation = ((self.player.reticle.x - self.player.rect.centerx) / 50) * -90
        self.degree = percent_of_rotation - (percent_of_rotation % 15)
        self.image = self.frames[f'{round(self.degree)}']



    def grapple(self,dt,player):
        self.pos.x += player.slope.x * dt * 40
        self.rect.x = round(self.pos.x)
        self.pos.y -= player.slope.y * dt * 40
        self.rect.y = round(self.pos.y)
        for sprite in self.collision_group:
            if not player.grapple_timer.active:
                player.grappling = False
            if sprite.rect.collidepoint(self.pos):
                player.grappling = False
                player.rope_length = (vector(player.rect.center).distance_to(self.pos)) ** 2
                player.swing_speed = 800
                player.swinging = False if player.rope_length < 8000 else True
                break

# player
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group,collision_group,graphics,explode_graphic):  # ,jump_sound):
        super().__init__(group)
        # class attributes
        self.collision_group = collision_group
        self.group = group
        self.explode_graphic = explode_graphic

        # animation
        self.frames = graphics
        self.frame_index = 0
        self.orientation = 'right'
        self.status = 'idle'
        self.image = self.frames[f'{self.status}_{self.orientation}'][int(self.frame_index)]
        self.rect = self.image.get_rect(center=pos)

        # hitbox
        self.hitbox = self.rect.inflate(-10, 0)

        self.mask = pygame.mask.from_surface(self.image)

        # bike
        foo = pygame.image.load('../graphics/items/bike.png')
        # self.bike = Bike(group,foo)

        # movement
        self.speed = 400
        self.direction = vector()
        self.gravity = 4
        self.pos = vector(self.rect.center)

        # attack
        self.attack_rect = None

        self.health = Player_Health()
        self.trans = transition(self)

        # grapple
        self.slope = vector(1,1)
        self.hook = Grappling_Hook(group,collision_group,(0,0))
        self.hook_pos = vector()
        self.rope_length = 0
        self.grapple_direction = 1
        self.swing_speed = 400
        self.swing_timer = Timer(200)
        self.dir = 1
        self.reticle = vector(self.rect.center)
        self.grapple_timer = Timer(1000)
        self.hit_timer = Timer(700)

        #for camera follow effect
        self.old_pos = vector((3200, 4030))

        # boolean checks
        self.on_floor = False
        self.attack = False
        self.shoot = False
        self.grappling = False
        self.swinging = False
        self.aim = True
        self.check = False
        self.trigger_oldx = True
        self.trigger_oldy = True
        self.mounting = False
    def apply_gravity(self, dt):
        self.direction.y += self.gravity * dt
    def input(self,dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            if self.orientation == 'left':
                self.reticle.x -= 2 * (self.reticle.x - self.rect.centerx)
            self.direction.x = 1
            self.orientation = 'right'
        elif keys[pygame.K_LEFT]:
            if self.orientation == 'right':
                self.reticle.x -= 2 * (self.reticle.x - self.rect.centerx)
            self.direction.x = -1
            self.orientation = 'left'
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE]:
            self.direction.y = -2
        elif keys[pygame.K_SLASH]:
            if not self.swinging and not self.swing_timer.active:
                self.grapple_timer.activate()
                self.grappling = True
                #self.aim = False
                self.hook.pos = vector(self.reticle)
            else:
                self.swinging = False
                self.swing_timer.activate()
        elif keys[pygame.K_RETURN]:
            self.frame_index = 0
            self.attack = True
        elif keys[pygame.K_RSHIFT]:
            self.frame_index = 0
            self.shoot = True
            # self.notYet = True

        # dist = self.pos.distance_to(self.bike.pos)
        # if keys[pygame.K_UP] and dist < 100:
        #     self.mounting = True
    def check_on_floor(self):
        floor_rect = pygame.Rect((self.hitbox.left + 3, self.hitbox.bottom), (self.hitbox.width - 6, 2))
        floor_sprites = [sprite for sprite in self.collision_group if sprite.rect.colliderect(floor_rect)]
        self.on_floor = True if floor_sprites else False
    def move(self,dt):
        # for camera
        if self.trigger_oldx:
            self.old_pos.x = self.rect.centerx
        elif self.trigger_oldy:
            self.old_pos.x = self.rect.centery
        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collisions('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collisions('vertical')
    def collisions(self,type):
        for sprite in self.collision_group:
            if self.hitbox.colliderect(sprite.rect):
                if type == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                if type == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom
                    self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
                    self.direction.y = 0
    def get_status(self):
        if self.on_floor and self.direction.x == 0:
            self.status = 'idle'
        elif self.on_floor:
            self.status = 'run'
        elif self.direction.y < 0:
            self.status = 'jump'
        else:
            self.status = 'fall'

        if self.attack:
            self.status = 'attack'
        elif self.shoot:
            self.status = 'shoot'
        if self.mounting:
            self.status = 'bike'
    def hurt(self,trans):
        if not self.hit_timer.active:
            self.hit_timer.activate()
            self.trans.got_hit = True
            self.health.reduce(trans)
    def attacks(self):
        if self.attack:
            self.attack_rect = pygame.Rect(self.hitbox.right, self.hitbox.top, 110, 64) if self.orientation == 'right' else pygame.Rect(self.hitbox.right - self.hitbox.width - 110, self.hitbox.top, 110, 64)
        if self.shoot:
            self.attack_rect = pygame.Rect(self.hitbox.right, self.hitbox.top, 400, 64) if self.orientation == 'right' else pygame.Rect(self.hitbox.right - self.hitbox.width - 400, self.hitbox.top, 400, 64)
            # explosion
            if int(self.frame_index) == 3:
                animated(self.group,(self.hitbox.right+30,self.hitbox.bottom),self.explode_graphic['right'],True) if self.orientation == 'right' else animated(self.group,(self.hitbox.left - 30,self.hitbox.bottom),self.explode_graphic['left'],True)
    def swing(self,dt):
        # aim
        if self.aim:
            keys = pygame.key.get_pressed()
            self.reticle.x += self.direction.x * self.speed * dt if not self.swinging else self.reticle.x
            if self.orientation == 'right':
                if self.reticle.x - self.rect.centerx <= 0:
                    self.reticle.x = self.rect.centerx
                elif self.reticle.x - self.rect.centerx > 49:
                    self.reticle.x = self.rect.centerx + 49
                if keys[pygame.K_UP]:
                    self.reticle.x -= .8
                if keys[pygame.K_DOWN]:
                    self.reticle.x += .8
            else:
                if self.reticle.x - self.rect.centerx < -49:
                    self.reticle.x = self.rect.centerx - 49
                elif self.reticle.x - self.rect.centerx >= 0:
                    self.reticle.x = self.rect.centerx
                if keys[pygame.K_UP]:
                    self.reticle.x += .8
                if keys[pygame.K_DOWN]:
                    self.reticle.x -= .8
            y = sqrt(2500 - (self.reticle.x - self.rect.centerx) ** 2)*-1 + self.rect.centery
            self.reticle.y = y
            self.slope.x = self.reticle.x - self.rect.centerx
            self.slope.y = (self.reticle.y - self.rect.centery) * -1
            if not self.grappling and not self.swinging:
                self.hook.pos.x = self.reticle.x
                self.hook.rect.x = round(self.hook.pos.x)
                self.hook.pos.y = self.reticle.y
                self.hook.rect.y = round(self.hook.pos.y)
                self.hook.rotate()

        # grapple
        if self.grappling:
            self.hook.grapple(dt,self)
            self.check = False
        # swing
        if self.swinging:
           # update the x
            increase = self.swing_speed * dt * self.grapple_direction
            self.swing_speed -= 50 * dt if self.swing_speed > 0 else 0
            if self.check:
                self.swing_speed -=  350 * dt if self.swing_speed > 0 else 0
            self.pos.x += increase
            self.rect.centerx = round(self.pos.x)
            limit = sqrt(self.rope_length) - ((self.swing_speed / 800) * sqrt(self.rope_length))

            if self.rect.centerx >= self.hook.pos.x + (sqrt(self.rope_length)) - limit:
                self.pos.x = self.hook.pos.x + (sqrt(self.rope_length)) - limit
                self.grapple_direction *= -1
            elif self.rect.centerx <= self.hook.pos.x - (sqrt(self.rope_length)) + limit:
                self.pos.x = self.hook.pos.x - (sqrt(self.rope_length)) + limit
                self.grapple_direction *= -1

            # translate position onto function
            if self.rect.centerx <= self.hook.pos.x - sqrt(self.rope_length):
                self.pos.x += 20
                self.rect.centerx = round(self.pos.x)
            elif self.rect.centerx >= self.hook.pos.x + sqrt(self.rope_length):
                self.check = True
                self.pos.x += 20
                self.rect.centerx = round(self.pos.x)

            y = sqrt(self.rope_length -(self.rect.centerx-self.hook.pos.x)**2) + self.hook.pos.y

            # Just update position
            self.pos.y = y
            self.rect.centery =  round(self.pos.y)

            self.hitbox.centerx,self.hitbox.centery = self.rect.centerx, self.rect.centery
            self.momentum = ((self.rect.centerx - self.hook.pos.x) / (sqrt(self.rope_length))) * -3
            self.direction.y = self.momentum
            print(self.direction.y)
    def animate(self,dt):
        current_animation = self.frames[f'{self.status}_{self.orientation}']
        self.frame_index += PLAYER_ANIMATION[f'{self.status}'] * dt
        if self.frame_index >= len(current_animation)-0.5:
            self.frame_index = 0
            # cancel attack
            self.attack = False
            self.shoot = False
            self.attack_rect = None
        self.image = current_animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        if self.hit_timer.active:
            surf = self.mask.to_surface()
            surf.set_colorkey('black')
            self.image = surf
    def update(self, dt):
        self.hit_timer.update()
        self.swing_timer.update()
        self.grapple_timer.update()
        if self.trans.got_hit:
            self.trans.play_hit(dt)
        self.apply_gravity(dt)
        self.input(dt)
        self.check_on_floor()
        if not self.mounting:
            self.move(dt)
        else:
            self.bike.move(dt)
        self.get_status()
        self.attacks()
        self.swing(dt)
        self.animate(dt)
class Player_Health():
    def __init__(self):
        super().__init__()
        self.frames = import_folder('../graphics/items/Health')
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
    def reduce(self,trans):
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
            trans.transitioning = True
        self.image = self.frames[self.frame_index]

# Bike
class Bike(pygame.sprite.Sprite):
    def __init__(self,group,surf):
        super().__init__(group)

        self.pos = vector((0, 0))
        self.speed = 300

        self.image = surf
        self.rect = self.image.get_rect(midbottom = (3240,4200))
        self.attack_rect = None
        self.direction = vector((1,0))
        self.balance = 1
        self.reward = 0
        self.side1 = True
        self.side2 = False
    def input(self,dt):
        keys = pygame.key.get_pressed()
        if self.side1:
            if keys[pygame.K_UP]:
                self.reward = .2 * dt
            else:
                self.reward = -.2 * dt

        elif self.side2:
            if keys[pygame.K_UP]:
                self.reward = -.2 * dt
            else:
                self.reward = .2 * dt

        if self.balance >= 1:
            self.side1 = True if self.side2 == True else False
            self.side2 = True if self.side1 == False else False
            self.balance = .9
    def move(self, dt):
        self.input(dt)
        self.balance += self.reward
        print(self.balance)
        self.player.pos.x += self.balance * self.direction.x * self.speed * dt
        self.player.rect.centerx = round(self.player.pos.x)
        self.player.rect.bottom = round(self.player.pos.y)
        if self.balance <= 0:
            self.player.mounting = False

# Boss
class Boss(pygame.sprite.Sprite):
    def __init__(self,group,collision_group,pos,surf):
        super().__init__(group)
        self.collision_group = collision_group


        # animation
        self.frames = surf
        self.frame_index = 0
        self.status = 'jump'
        self.orientation = 'right'

        # movement
        self.speed = 100
        self.direction = vector()
        self.gravity = 30
        self.pos = vector(pos)

        self.image = self.frames[self.status][0]
        self.rect = self.image.get_rect(midbottom = self.pos)
        self.hitbox = self.rect.inflate(-10,0)
        self.last_rect = self.rect.right
        self.on_floor = False
        self.hit_wall = True
        self.attack_rect = None
        self.mask = pygame.mask.from_surface(self.image)
        # timers
        self.walk_timer = Timer(1000)
        self.sword_timer = Timer(1000)
        self.kick_timer = Timer(5000)
        self.jump_timer = Timer(3000)
        self.idle_timer = Timer(500)
        self.hit_timer = Timer(1000)

        self.attack_timer = Timer(5000)
    def move(self,dt):
        # apply gravity
        self.direction.y += self.gravity * dt

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collisions('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.bottom = round(self.pos.y)
        self.rect.bottom = self.hitbox.bottom
        self.collisions('vertical')
    def collisions(self,type):
        for sprite in self.collision_group:
            if self.hitbox.colliderect(sprite.rect):
                if type == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                        self.hit_wall = True
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                        self.hit_wall = True
                    self.rect.centerx, self.pos.x = self.hitbox.centerx,self.hitbox.centerx
                if type == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom
                    self.direction.y = 0
                    self.rect.bottom, self.pos.y = self.hitbox.bottom,self.hitbox.bottom
    def get_status(self):
        if self.frame_index == 0:
            x = randint(1,10)
            distance = self.player.pos.distance_to(self.pos)
            if self.status == 'jump' and not self.check_on_floor():
                self.status = 'jump'
            elif self.status == 'idle' and self.idle_timer.active:
                self.status = 'idle'
            elif self.status == 'attack' and not self.hit_wall:
                self.status = 'attack'
            elif self.status == 'walk' and self.walk_timer.active:
                self.status = 'walk'

            else:
                if (distance > 150 and x < 5):
                    self.status = 'walk'
                    self.direction.x = 1 if self.player.pos.x - self.pos.x > 0 else -1
                    self.orientation = 'right' if self.direction.x == 1 else 'left'
                    self.walk_timer.activate() if not self.walk_timer.active else None
                elif distance < 300 and x < 7 and not self.sword_timer.active:
                    self.status = 'sword'
                    self.direction.x = 0
                    self.orientation = 'right' if self.player.pos.x - self.pos.x > 0 else 'left'
                    self.sword_timer.activate()
                elif distance > 150 and x == 8 and not self.kick_timer.activate():
                    self.status = 'attack'
                    self.direction.x = 1 if self.player.pos.x - self.pos.x > 0 else -1
                    self.orientation = 'right' if self.direction.x == 1 else 'left'
                    self.hit_wall = False
                    self.kick_timer.activate()
                elif distance > 150  and x < 9 and not self.jump_timer.active:
                    self.status = 'jump'
                    self.direction.x = 4 if self.player.pos.x - self.pos.x > 0 else -4
                    self.direction.y = -15
                    self.jump_timer.activate()
                else:
                    self.status = 'idle'
                    self.direction.x = 0
                    self.idle_timer.activate()
    def check_on_floor(self):
        floor_rect = pygame.Rect((self.rect.left + 3, self.rect.bottom), (self.rect.width - 6, 2))
        floor_sprites = [sprite for sprite in self.collision_group if sprite.rect.colliderect(floor_rect)]
        return True if floor_sprites else False
    def behaviors(self,dt):
        if self.status == 'walk':
            # if int(self.frame_index) >= 5:
            #     self.direction.x = 0
            self.speed = 200
        elif self.status == 'attack':
            if int(self.frame_index) == len(self.frames[self.status]) - 1:
                self.speed = 500
            else:
                self.speed = 100
        elif self.status == 'sword':
            self.attack_rect = pygame.Rect(self.hitbox.right, self.hitbox.top, 250, 180) if self.orientation == 'right' else pygame.Rect(self.hitbox.right - self.hitbox.width - 250, self.hitbox.top, 250, 180)
        else:
            self.speed = 100
    def hurt(self):
        if not self.hit_timer.active:
            self.hit_timer.activate()
    def animate(self,dt):
        current_animation = self.frames[self.status]
        self.frame_index += BOSS_ANIMATION[self.status] * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            self.attack_rect = None
            if self.status == 'attack' and not self.hit_wall:
                self.frame_index = len(current_animation)-1
        self.image = current_animation[int(self.frame_index)]
        if self.orientation == 'left':
            self.image = pygame.transform.flip(current_animation[int(self.frame_index)],True,False)
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        if self.hit_timer.active:
            surf = self.mask.to_surface()
            surf.set_colorkey('black')
            self.image = surf
    def update(self,dt):
        self.hit_timer.update()
        self.sword_timer.update()
        self.jump_timer.update()
        self.kick_timer.update()
        self.walk_timer.update()
        self.idle_timer.update()

        self.get_status()
        self.behaviors(dt)
        self.move(dt)
        self.animate(dt)

# enemies
class baba(Generic):
    def __init__(self, group, pos, graphics, collision_group):
        # animation
        self.frames = graphics
        self.frame_index = 0

        # movement
        self.speed = 100
        self.direction = vector(choice((1,-1)),0)
        self.pos = vector(pos)
        self.orientation = 'right' if self.direction.x == 1 else 'left'
        self.status = 'run'

        super().__init__(group, pos, self.frames[f'run_{self.orientation}'][self.frame_index])

    def animate(self,dt):
        current_animation = self.frames[f'{self.status}_{self.orientation}']
        self.frame_index += 11 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0

        self.image = current_animation[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=self.pos)
    def update(self,dt):
        self.animate(dt)
class fly(Generic):
    def __init__(self, group, pos, graphics,collision_group):
        # animation
        self.frames = graphics.copy()
        for i in range(len(self.frames)):
            self.frames[i] = pygame.transform.scale_by(self.frames[i],0.2)
        self.frame_index = 0

        # movement
        self.speed = vector(90,90)
        self.direction = vector(1,0)
        self.pos = vector(pos)
        self.gravity = 4

        # random movement
        self.xTarget_frame = 0
        self.yTarget_frame = 0
        self.xTarget = 0
        self.yTarget = 0
        self.frame_index = 0

        # timers
        self.speed_timer = Timer(500)

        # attributes
        self.was_on = False
        super().__init__(group, pos, self.frames[int(self.frame_index)])
    def detect_playerpos(self,dt):
        xTarget_options = [self.player.rect.centerx, self.player.rect.right, self.player.rect.left ]
        yTarget_options = [self.player.rect.centery, self.player.rect.bottom, self.player.rect.top]

        if self.xTarget_frame > 2:
            self.xTarget_frame = 0
        if self.yTarget_frame > 2:
            self.yTarget_frame = 0

        self.xTarget = xTarget_options[self.xTarget_frame]
        self.yTarget = yTarget_options[self.yTarget_frame]

        if self.xTarget > self.rect.x:
            self.direction.x += self.gravity * dt
        elif self.xTarget < self.rect.x:
            self.direction.x -= self.gravity * dt
        else:
            self.direction.x = 0
            self.xTarget_frame += 1

        if self.yTarget > self.rect.y:
            self.direction.y += self.gravity * dt
        elif self.yTarget < self.rect.y:
            self.direction.y -= self.gravity * dt
        else:
            self.direction.y = 0
            self.yTarget_frame += 1
    def change_speed(self):
        if self.speed_timer.active and not self.was_on:
            self.speed.x = randint(50, 130)
            self.speed.y = randint(50, 130)
            self.was_on = True
        else:
            self.was_on = False if not self.speed_timer.active else True
            self.speed_timer.activate() if not self.speed_timer.active else self.speed_timer
    def move(self, dt):
        if self.direction.x > 1:
            self.direction.x -= self.gravity * dt
        elif self.direction.x < -1:
            self.direction.x += self.gravity * dt
        self.pos.x += self.direction.x * self.speed.x * dt
        self.rect.x = round(self.pos.x)
        # self.check_collisions('horizontal')

        if self.direction.y > 1:
            self.direction.y -= self.gravity * dt
        elif self.direction.y < -1:
            self.direction.y += self.gravity * dt
        self.pos.y += self.direction.y * self.speed.y * dt
        self.rect.y = round(self.pos.y)
        # self.check_collisions('vertical')
    def animate(self,dt):
        self.frame_index += 26 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    def update(self,dt):
        self.speed_timer.update()
        self.detect_playerpos(dt)
        self.change_speed()
        self.move(dt)
        self.animate(dt)
class man(Generic):
    def __init__(self, group, pos, graphics):
        # animation
        self.frames = graphics
        self.frame_index = 0
        self.status = 'idle'
        self.pos = pos

        super().__init__(group, pos, self.frames[self.status][self.frame_index])

    def animate(self,dt):
        current_animation = self.frames[self.status]
        self.frame_index += 25 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
        self.image = current_animation[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom = self.pos)
    def update(self,dt):
        self.animate(dt)
class slime(Generic):
    def __init__(self, group, pos, graphics,change_graphics, collision_group):
        super().__init__(group, pos, graphics[0])

        # animation
        self.frames = graphics
        self.frame_index = 0
        self.change_frames = change_graphics

        # moving
        self.speed = 70
        self.direction = vector(choice((-1,1)),0)
        self.pos = vector(pos)
        self.orientation = 'right' if self.direction.x == 1 else 'left'
        self.mode = 'top'
        self.rect = self.image.get_rect(midbottom = self.pos)

        # collisions
        self.check = vector(0, 10)
        self.last_sprite = None

        # timers
        self.changed = Timer(900)

        # attributes
        self.collision_group = collision_group
        self.was_active = False
    def move(self,dt):
        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
    def cliff(self):
        d = {'right':self.rect.midleft + vector((-10,0)),'left':self.rect.midright + vector((10,0)),'bottom':self.rect.midtop + vector((0,-10)),'top':self.rect.midbottom + vector((0,10))}
        self.on = d[self.mode]

        sprite_list = []
        for sprite in self.collision_group:
            if sprite.rect.collidepoint(self.on):
                sprite_list.append(sprite)
                self.last_sprite = sprite
        print(self.rect.bottom)
        #exit()
        if not sprite_list:
            if self.direction.x:
                if self.mode == 'bottom':
                    if self.orientation == 'right':
                        self.rect.midright = self.last_sprite.rect.bottomleft
                        self.rect.x -= 1
                        self.rect.y -= 1
                    else:
                        self.rect.midleft = self.last_sprite.rect.bottomright
                        self.rect.x += 1
                        self.rect.y -= 1

                    self.pos.x = self.rect.x
                    self.pos.y = self.rect.y
                    self.direction.x = 0
                    self.direction.y = -1 #if self.orientation == 'right' else 1
                    self.mode = 'left' if self.orientation == 'right' else 'right'

                    self.changed.activate()
                    self.store = self.pos
                    #self.storex, self.storey = self.pos.x, self.pos.y
                    self.frame_index = 0
                elif self.mode == 'top':
                    if self.orientation == 'right':
                        self.rect.midleft = self.last_sprite.rect.topright
                        self.rect.x+=1
                        self.rect.y += 1
                    else:
                        self.rect.midright = self.last_sprite.rect.topleft
                        self.rect.x -= 1
                        self.rect.y += 1

                    self.pos.x, self.pos.y = self.rect.x, self.rect.y

                    self.direction.x = 0
                    self.direction.y = 1 #if self.orientation == 'right' else -1
                    self.mode = 'right' if self.orientation == 'right' else 'left'

                    self.changed.activate()
                    self.store = self.pos
                    #self.storex, self.storey = self.pos.x, self.pos.y
                    self.frame_index = 0
            elif self.direction.y:
                if self.mode == 'right':
                    if self.orientation == 'right':
                        self.rect.midtop = self.last_sprite.rect.bottomright
                        self.rect.x-=1
                        self.rect.y+=1
                    else:
                        self.rect.midbottom = self.last_sprite.rect.topright
                        self.rect.x -=1
                        self.rect.y-=1

                    self.pos.x, self.pos.y = self.rect.x, self.rect.y
                    self.direction.y = 0
                    self.direction.x = -1 #if self.orientation == 'right' else 1
                    self.mode = 'bottom' if self.orientation == 'right' else 'top'

                    self.changed.activate()
                    self.store = self.pos
                    #self.storex, self.storey = self.pos.x, self.pos.y
                    self.frame_index = 0
                elif self.mode == 'left':
                    if self.orientation == 'right':
                        self.rect.midbottom = self.last_sprite.rect.topleft
                        self.rect.x += 1
                        self.rect.y -= 1
                    else:
                        self.rect.midtop = self.last_sprite.rect.bottomleft
                        self.rect.x += 1
                        self.rect.y += 1
                    self.pos.x, self.pos.y = self.rect.x, self.rect.y
                    self.direction.y = 0
                    self.direction.x = 1 #if self.orientation == 'right' else -1
                    self.mode = 'top' if self.orientation == 'right' else 'bottom'

                    self.changed.activate()
                    self.store = self.pos
                    #self.storex, self.storey = self.pos.x, self.pos.y
                    self.frame_index = 0

    def collisions(self):
        for sprite in self.collision_group:
            if sprite.rect.colliderect(self.rect):
                if self.direction.x > 0:
                    self.mode = 'left'
                    self.rect.right = sprite.rect.left
                    self.pos.x = self.rect.x
                    self.direction.x = 0
                    self.direction.y = -1 if self.orientation == 'right' else 1
                elif self.direction.x < 0:
                    self.mode = 'right'
                    self.rect.left = sprite.rect.right
                    self.pos.x = self.rect.x
                    self.direction.x = 0
                    self.direction.y = 1 if self.orientation == 'right' else -1
                elif self.direction.y > 0:
                    self.mode = 'top'
                    self.rect.bottom = sprite.rect.top
                    self.pos.y = self.rect.y
                    self.direction.y = 0
                    self.direction.x = 1 if self.orientation == 'right' else -1
                elif self.direction.y < 0:
                    self.mode = 'bottom'
                    self.rect.top = sprite.rect.bottom
                    self.pos.y = self.rect.y
                    self.direction.y = 0
                    self.direction.x = -1 if self.orientation == 'right' else 1
    def animate(self,dt):
        self.frame_index += 3 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        if self.orientation == 'left':
            self.image = pygame.transform.flip(self.image,True,False)

        #rotate image accordingly, set appropriate frames, and move rect to show changed graphic
        if self.changed.active:
            self.image = self.change_frames[self.orientation][int(self.frame_index)]
            if self.mode == 'bottom':
                if self.orientation == 'right':
                    self.rect.topleft = self.last_sprite.rect.center
                    self.image = pygame.transform.rotate(self.image, 270)
                else:
                    self.rect.topright = self.last_sprite.rect.center
                    self.image = pygame.transform.rotate(self.image, 180)
            elif self.mode == 'left':
                if self.orientation == 'right':
                    self.rect.topright = self.last_sprite.rect.center
                    self.image = pygame.transform.rotate(self.image, 180)
                else:
                    self.rect.bottomright = self.last_sprite.rect.center
                    self.image = pygame.transform.rotate(self.image, 90)
            elif self.mode == 'right':
                if self.orientation == 'right':
                    self.rect.bottomleft = self.last_sprite.rect.center
                else:
                    self.rect.topleft = self.last_sprite.rect.center
                    self.image = pygame.transform.rotate(self.image, 270)
            elif self.mode == 'top':
                if self.orientation == 'right':
                    self.rect.bottomright = self.last_sprite.rect.center
                    self.image = pygame.transform.rotate(self.image, 90)
                else:
                    self.rect.bottomleft = self.last_sprite.rect.center
            self.was_active = True
        # Otherwise, rotate image accordingly
        else:
            if self.mode == 'bottom':
                self.image = pygame.transform.rotate(self.image,180)
            elif self.mode == 'left':
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.mode == 'right':
                self.image = pygame.transform.rotate(self.image, 270)

        # if the "changed" graphic JUST ended, restore position so movement can continue
        if not self.changed.active and self.was_active:
            self.pos = self.store
            self.was_active = False

    def update(self,dt):
        self.changed.update()

        if not self.changed.active:
            self.move(dt)
            self.collisions()
            self.cliff()

        self.animate(dt)
# class Slime(Generic):
#     def __init__(self,surf,changesurf,pos,group,collision_sprites):
#         self.frames = surf
#         self.change_frames = changesurf
#         # for frames in surf:
#         #     x = pygame.transform.scale(frames,(32,32))
#         #     self.frames.append(x)
#
#         super().__init__(pos,self.frames[0],group)
#         self.mask = pygame.mask.from_surface(self.image)
#         self.hit_timer = Timer(250)
#
#         # attributes
#         self.collision_sprites = collision_sprites
#
#         # animation
#         #self.frames = surf
#         self.frame_index = 0
#
#         # moving
#         self.pos = vector(pos)
#         self.direction = vector(choice((-1,1)),0)
#         self.speed = 70
#         self.orientation = 'right' if self.direction.x == 1 else 'left'
#         self.check = vector(0,10)
#         self.mode = 'top'
#         self.last_sprite = None
#         self.tester = False
#         self.changed = Timer(900)
#
#         self.store = self.pos
#         self.health_bar = HealthBar(self.rect.width,3,self.rect.topleft,self.groups()[0])
#
#         self.was_active = False
#
#     def hit(self):
#         if not self.hit_timer.active:
#             self.health_bar.reduce(10)
#             self.hit_timer.activate()
#
#         if not self.health_bar.exists:
#             self.kill()
#     # gets status
#     def collisions(self):
#         for sprite in self.collision_sprites:
#             if sprite.rect.colliderect(self.rect):
#                 if self.direction.x > 0:
#                     self.mode = 'left'
#                     self.rect.right = sprite.rect.left
#                     self.pos.x = self.rect.x
#                     self.direction.x = 0
#                     self.direction.y = -1 if self.orientation == 'right' else 1
#
#                     print(1)
#                 elif self.direction.x < 0:
#                     self.mode = 'right'
#                     self.rect.left = sprite.rect.right
#                     self.pos.x = self.rect.x
#                     self.direction.x = 0
#                     self.direction.y = 1 if self.orientation == 'right' else -1
#                     print(2)
#                 elif self.direction.y > 0:
#                     self.mode = 'top'
#                     self.rect.bottom = sprite.rect.top
#                     self.pos.y = self.rect.y
#                     self.direction.y = 0
#                     self.direction.x = 1 if self.orientation == 'right' else -1
#                     print(3)
#                 elif self.direction.y < 0:
#                     self.mode = 'bottom'
#                     self.rect.top = sprite.rect.bottom
#                     self.pos.y = self.rect.y
#                     self.direction.y = 0
#                     self.direction.x = -1 if self.orientation == 'right' else 1
#                     print(4)
#     def cliff(self):
#         d = {'right':self.rect.midleft + vector((-10,0)),'left':self.rect.midright + vector((10,0)),'bottom':self.rect.midtop + vector((0,-10)),'top':self.rect.midbottom + vector((0,10))}
#         #d2 = {'right':vector((-10,0)),'left':vector((10,0)),'bottom':vector((0,-10)),'top':vector((0,10))}
#         self.on = d[self.mode]
#         #self.key = d2[self.mode]
#
#
#         sprite_list = []
#         for sprite in self.collision_sprites:
#             if sprite.rect.collidepoint(self.on):
#                 sprite_list.append(sprite)
#                 self.last_sprite = sprite
#         # if self.mode == 'top':
#         #     time.sleep(5)
#         if not sprite_list:
#             if self.direction.x:
#                 if self.mode == 'bottom':
#                     if self.orientation == 'right':
#                         self.rect.midright = self.last_sprite.rect.bottomleft
#                         self.rect.x -= 1
#                         self.rect.y -= 1
#                     else:
#                         self.rect.midleft = self.last_sprite.rect.bottomright
#                         self.rect.x += 1
#                         self.rect.y -= 1
#
#                     self.pos.x = self.rect.x
#                     self.pos.y = self.rect.y
#                     self.direction.x = 0
#                     self.direction.y = -1 #if self.orientation == 'right' else 1
#                     self.mode = 'left' if self.orientation == 'right' else 'right'
#
#                     self.changed.activate()
#                     self.store = self.pos
#                     #self.storex, self.storey = self.pos.x, self.pos.y
#                     self.frame_index = 0
#                     print('bottom')
#                 elif self.mode == 'top':
#                     if self.orientation == 'right':
#                         self.rect.midleft = self.last_sprite.rect.topright
#                         self.rect.x+=1
#                         self.rect.y += 1
#                     else:
#                         self.rect.midright = self.last_sprite.rect.topleft
#                         self.rect.x -= 1
#                         self.rect.y += 1
#
#                     self.pos.x, self.pos.y = self.rect.x, self.rect.y
#
#                     self.direction.x = 0
#                     self.direction.y = 1 #if self.orientation == 'right' else -1
#                     self.mode = 'right' if self.orientation == 'right' else 'left'
#
#                     self.changed.activate()
#                     self.store = self.pos
#                     #self.storex, self.storey = self.pos.x, self.pos.y
#                     self.frame_index = 0
#                     print('top')
#             elif self.direction.y:
#                 if self.mode == 'right':
#                     if self.orientation == 'right':
#                         self.rect.midtop = self.last_sprite.rect.bottomright
#                         self.rect.x-=1
#                         self.rect.y+=1
#                     else:
#                         self.rect.midbottom = self.last_sprite.rect.topright
#                         self.rect.x -=1
#                         self.rect.y-=1
#
#                     self.pos.x, self.pos.y = self.rect.x, self.rect.y
#                     self.direction.y = 0
#                     self.direction.x = -1 #if self.orientation == 'right' else 1
#                     self.mode = 'bottom' if self.orientation == 'right' else 'top'
#
#                     self.changed.activate()
#                     self.store = self.pos
#                     #self.storex, self.storey = self.pos.x, self.pos.y
#                     self.frame_index = 0
#                     print('right')
#                 elif self.mode == 'left':
#                     if self.orientation == 'right':
#                         self.rect.midbottom = self.last_sprite.rect.topleft
#                         self.rect.x += 1
#                         self.rect.y -= 1
#                     else:
#                         self.rect.midtop = self.last_sprite.rect.bottomleft
#                         self.rect.x += 1
#                         self.rect.y += 1
#                     self.pos.x, self.pos.y = self.rect.x, self.rect.y
#                     self.direction.y = 0
#                     self.direction.x = 1 #if self.orientation == 'right' else -1
#                     self.mode = 'top' if self.orientation == 'right' else 'bottom'
#
#                     self.changed.activate()
#                     self.store = self.pos
#                     #self.storex, self.storey = self.pos.x, self.pos.y
#                     self.frame_index = 0
#                     print('left')
#
#             #self.orientation = 'right' if self.orientation == 'left' else 'left'
#
#             # if self.direction.x:
#             #     self.direction.x *= -1
#             # if self.direction.y:
#             #     self.direction.y *= -1
#             #
#             # self.orientation = 'right' if self.orientation == 'left' else 'left'
#     def move(self,dt):
#         self.pos.x += self.direction.x * self.speed * dt
#         self.pos.y += self.direction.y * self.speed * dt
#         self.rect.x = round(self.pos.x)
#         self.rect.y = round(self.pos.y)
#         self.health_bar.move(pos = (self.rect.x,self.rect.y))
#         #self.key = 1
#         #bottom = {1:self.rect.bottom,2:self.rect.left,3:self.rect.top,4:self.rect.right}
#         # if not [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(vector(bottom[self.key]) + self.check)]:
#         #     if self.orientation == 'right':
#         #         self.key = 2
#         #         self.check = vector(-10,0)
#         #         if self.mode == 'vertical':
#         #             self.key = 3
#         #             self.check = vector(0, 0)
#     def animate(self,dt):
#         self.frame_index += 3 * dt
#         if self.frame_index >= len(self.frames):
#             self.frame_index = 0
#         self.image = self.frames[int(self.frame_index)]
#
#         if self.orientation == 'left':
#             self.image = pygame.transform.flip(self.image,True,False)
#
#         # rotate image accordingly, set appropriate frames, and move rect to show changed graphic
#         if self.changed.active:
#             self.image = self.change_frames[self.orientation][int(self.frame_index)]
#             if self.mode == 'bottom':
#                 if self.orientation == 'right':
#                     self.rect.topleft = self.last_sprite.rect.center
#                     self.image = pygame.transform.rotate(self.image, 270)
#                 else:
#                     self.rect.topright = self.last_sprite.rect.center
#                     self.image = pygame.transform.rotate(self.image, 180)
#             elif self.mode == 'left':
#                 if self.orientation == 'right':
#                     self.rect.topright = self.last_sprite.rect.center
#                     self.image = pygame.transform.rotate(self.image, 180)
#                 else:
#                     self.rect.bottomright = self.last_sprite.rect.center
#                     self.image = pygame.transform.rotate(self.image, 90)
#             elif self.mode == 'right':
#                 if self.orientation == 'right':
#                     self.rect.bottomleft = self.last_sprite.rect.center
#                 else:
#                     self.rect.topleft = self.last_sprite.rect.center
#                     self.image = pygame.transform.rotate(self.image, 270)
#             elif self.mode == 'top':
#                 if self.orientation == 'right':
#                     self.rect.bottomright = self.last_sprite.rect.center
#                     self.image = pygame.transform.rotate(self.image, 90)
#                 else:
#                     self.rect.bottomleft = self.last_sprite.rect.center
#             self.was_active = True
#             self.health_bar.move(pos=(self.rect.x, self.rect.y))
#         # Otherwise, rotate image accordingly
#         else:
#             if self.mode == 'bottom':
#                 self.image = pygame.transform.rotate(self.image,180)
#             elif self.mode == 'left':
#                 self.image = pygame.transform.rotate(self.image, 90)
#             elif self.mode == 'right':
#                 self.image = pygame.transform.rotate(self.image, 270)
#
#         # if the "changed" graphic JUST ended, restore position so movement can continue
#         if not self.changed.active and self.was_active:
#             self.pos = self.store
#             # self.pos.x = self.storex
#             # self.pos.y = self.storey
#             self.was_active = False
#
#         # for hurt visual
#         if self.hit_timer.active:
#             surf = pygame.transform.flip(self.mask.to_surface(),True,False)
#             surf.set_colorkey('black')
#             self.image = surf
#     def update(self,dt):
#         self.hit_timer.update()
#         self.changed.update()
#
#         if not self.changed.active:
#             self.move(dt)
#             self.collisions()
#             self.cliff()
#
#         self.animate(dt)
class spike(Generic):
    def __init__(self, group, pos, graphics):
        super().__init__(group, pos, graphics[0])

        # animation
        self.frames = graphics
        self.rect = self.image.get_rect(midbottom = pos)

        # attributes









