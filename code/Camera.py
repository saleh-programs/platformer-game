import pygame
from pygame.math import Vector2 as vector
from Settings import *
from support import import_list
from random import randint
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()

        #margins
        self.left_margin = 100
        self.right_margin = width - 100
        self.leftwall = 0

        self.top_margin = 100
        self.bottom_margin = height - 100
        self.topwall = 0

        #background
        self.hor_center = 4170
        self.ver_center = 1900
        self.test_scale = 1
        self.back = [pygame.image.load('../graphics/hills/Level1dark.png').convert_alpha(),
                pygame.image.load('../graphics/hills/Level2dark.png').convert_alpha(),
                pygame.image.load('../graphics/hills/Level3dark.png').convert_alpha(),
                pygame.image.load('../graphics/hills/Level4dark.png').convert_alpha(),
                pygame.image.load('../graphics/hills/mist1.png').convert_alpha(),
                pygame.image.load('../graphics/hills/mist2.png').convert_alpha(),
                pygame.image.load('../graphics/hills/mist3.png').convert_alpha()]
        # self.leftwall = 3600
        # self.topwall = 1500

        self.map = pygame.image.load('../tiled/map.png').convert_alpha()
        self.img = pygame.image.load('../graphics/items/light3.png').convert_alpha()
        #self.img = pygame.image.load('../graphics/items/untitled.png').convert_alpha()

        # mist
        self.mistx = [-300,-300,-300]
        self.misty = self.topwall
        self.direction = 1

        #cam


    def draw_hills(self,dt):
        x = self.hor_center - width / 2
        y = self.ver_center - height / 2
        self.display_surface.blit(self.back[0],(x * -.03, y * -.04))
        self.display_surface.blit(self.back[1],(x * -.04, y * -.05 + 411))
        self.display_surface.blit(self.back[2],(x * -.05, y * -.06 + 430))
        self.display_surface.blit(self.back[3],(x * -.06, y * -.07 + 443))

        # mit
        self.display_surface.blit(self.back[4], (self.mistx[0],y * -.09 + 170))
        self.display_surface.blit(self.back[5], (self.mistx[1], y * -.10 + 170))
        self.display_surface.blit(self.back[6], (self.mistx[2], y * -.11 + 170))

        self.mistx[0] += 20 * self.direction * dt
        self.mistx[1] += 30 * self.direction * dt
        self.mistx[2] += 40 * self.direction * dt
        self.misty = self.topwall
        if self.mistx[1] > 500:
            self.direction = -1
    def draw(self, player,dt):
        # box camera
        # use old pos
        # old_pos = vector(player.rect.center)
        # if old_pos.x <= self.leftwall + self.left_margin:
        #     self.leftwall = old_pos.x - self.left_margin
        #     self.hor_center = self.leftwall + width/2
        #
        #     self.offset.x = old_pos.x - self.left_margin
        # elif old_pos.x >= self.leftwall + self.right_margin:
        #     self.leftwall = old_pos.x - self.right_margin
        #     self.hor_center = self.leftwall + width/2
        #
        #     self.offset.x = old_pos.x - self.right_margin
        # else:
        #     self.offset.x = self.hor_center - width / 2
        # if old_pos.y <= self.topwall + self.top_margin:
        #     self.topwall = old_pos.y - self.top_margin
        #     self.ver_center = self.topwall + height/2
        #
        #     self.offset.y = old_pos.y - self.top_margin
        # elif old_pos.y >= self.topwall + self.bottom_margin:
        #     self.topwall = old_pos.y - self.bottom_margin
        #     self.ver_center = self.topwall + height/2
        #
        #     self.offset.y = old_pos.y - self.bottom_margin
        # else:
        #     self.offset.y = self.ver_center - height / 2
        #
        if player.rect.centerx <= self.leftwall + self.left_margin:
            self.leftwall = player.rect.centerx - self.left_margin
            self.hor_center = self.leftwall + width/2
        elif player.rect.centerx >= self.leftwall + self.right_margin:
            self.leftwall = player.rect.centerx - self.right_margin
            self.hor_center = self.leftwall + width/2
        if player.rect.centery <= self.topwall + self.top_margin:
            self.topwall = player.rect.centery - self.top_margin

            self.ver_center = self.topwall + height/2
        elif player.rect.centery >= self.topwall + self.bottom_margin:
            self.topwall = player.rect.centery - self.bottom_margin
            self.ver_center = self.topwall + height/2


        self.offset.x += (player.rect.centerx - (self.offset.x + width / 2)) * 4 * dt
        self.offset.y += (player.rect.centery - (self.offset.y + height / 2)) * 4 * dt


        if player.shoot and int(player.frame_index) == 3:
            self.offset.x += randint(-20,20)
            self.offset.y += randint(-20,20)

        # draw hills and map
        self.draw_hills(dt)
        self.display_surface.blit(self.map, (0, 0) - self.offset)



        # draw player
        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)
            if sprite.attack_rect:
                temp = sprite.attack_rect.move(-self.offset.x,-self.offset.y)
                pygame.draw.rect(self.display_surface, 'red', temp, 1)
            #pygame.draw.line(self.display_surface,'red',(sprite.rect.center) - self.offset, (sprite.rect.centerx + 300,sprite.rect.centery) - self.offset)
        self.display_surface.blit(player.health.image,(10,10))
        #     if sprite.hitbox:
        #         temp = sprite.hitbox.move(-self.offset.x, -self.offset.y)
        #         pygame.draw.rect(self.display_surface, 'red', temp, 1)
        temp = vector(self.img.get_width()/2,self.img.get_height() /2)

        #self.display_surface.blit(self.img,player.rect.center - self.offset - temp)


        # pygame.draw.line(self.display_surface,'black',(player.rect.centerx,player.rect.centery) - self.offset,(player.hook.rect.x,player.hook.rect.y) - self.offset)
        # if player.grappling:
        #     self.copycat = pygame.Rect(player.hook.pos.x - self.offset.x,player.hook.pos.y-self.offset.y,10,10)
        #     pygame.draw.rect(self.display_surface, 'red',self.copycat,1)
        # if player.aim:
        #     # self.copycat = pygame.Rect(player.reticle.x - self.offset.x,player.reticle.y-self.offset.y,10,10)
        #     # pygame.draw.rect(self.display_surface, 'red',self.copycat,1)
        #
        #     self.imagetemp = pygame.image.load('../graphics/items/hook.png')
        #     self.display_surface.blit(self.imagetemp,(player.reticle.x - self.offset.x,player.reticle.y - self.offset.y))

        #bubble.draw_words(dt, self.offset)


