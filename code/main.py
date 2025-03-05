import pygame
import pytmx
import os
from Camera import CameraGroup
from sys import exit
from all_sprites import Generic, Boss, animated, text_bubble,Player, baba, fly, man, spike, slime
from pygame.image import load as load
from os import walk
from support import import_folder,import_list
import cProfile, pstats
from Settings import *
import openai
from transition import *

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((width,height))

        self.clock = pygame.time.Clock()

        # imports
        self.imports()

        # loads individual surfaces instead of positions on the map
        self.tmxdata = pytmx.util_pygame.load_pygame('../tiled/map_info.tmx')

        # groups
        self.all_sprites = CameraGroup()
        self.collide_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Collidables
        self.obj_collidable_tiles = []
        for layer in self.tmxdata.get_layer_by_name('Geometries'):
            if layer.name == 'baba':
                baba([self.all_sprites, self.enemy_sprites], (layer.x, layer.y), self.assets['baba'], self.collide_sprites)
            elif layer.name == 'fly':
                fly([self.all_sprites, self.enemy_sprites], (layer.x, layer.y), self.assets['fly'], self.collide_sprites)
            elif layer.name == 'man':
                man([self.all_sprites, self.enemy_sprites], (layer.x, layer.y), self.assets['man'])
            elif layer.name == 'slime':
                slime([self.all_sprites, self.enemy_sprites], (layer.x, layer.y), self.assets['slime'],self.assets['slimeChange'],self.collide_sprites)
            elif layer.name == 'spike':
                spike([self.all_sprites, self.enemy_sprites], (layer.x, layer.y), self.assets['spike'])
            else:
                Generic(self.collide_sprites, (layer.x, layer.y), pygame.Surface((layer.width, layer.height)))
        # player
        self.player = Player((3240, 4200),self.all_sprites,self.collide_sprites, self.assets['player'],self.assets['explosion'])

        self.trans = transition(self.player)

        # self.bubble = text_bubble(self.all_sprites,(2700,4200),self.assets['bubble'])
        # animated(self.all_sprites,(2100,4380),self.assets['dude'])
        # animated(self.all_sprites, (2750, 4215), self.assets['boss'])
        Boss([self.all_sprites,self.enemy_sprites],self.collide_sprites,(4180,2080),self.assets['boss'])



    def imports(self):
        self.assets = {
        'player': {folder: import_folder(f'../graphics/player/{folder}') for folder in list(walk('../graphics/player'))[0][1]},
        'baba': {folder: import_folder(f'../graphics/enemies/baba/{folder}') for folder in list(walk('../graphics/enemies/baba'))[0][1]},
        'man': {folder: import_folder(f'../graphics/enemies/man/{folder}') for folder in list(walk('../graphics/enemies/man'))[0][1]},
        'fly': import_folder('../graphics/enemies/fly'),
        'slime': import_folder('../graphics/enemies/slime'),
        'slimeChange': {folder: import_folder(f'../graphics/enemies/slimeChange/{folder}') for folder in list(walk('../graphics/enemies/slimeChange'))[0][1]},
        'spike': import_folder('../graphics/enemies/spike'),
        'bubble':pygame.image.load('../graphics/items/textbubble/bubble.png'),
        'dude': import_folder('../graphics/dude'),
        'explosion': {folder: import_folder(f'../graphics/items/explosion/{folder}') for folder in list(walk('../graphics/items/explosion'))[0][1]},
        'boss':{folder: import_folder(f'../graphics/enemies/boss/{folder}') for folder in list(walk('../graphics/enemies/boss'))[0][1]}
        }
    def give_player_pos(self):
        for sprite in self.all_sprites:
            sprite.player = self.player
    def hit(self):
        if self.player.attack_rect:
            for sprite in self.enemy_sprites:
                if self.player.attack_rect.colliderect(sprite.hitbox):
                    sprite.hurt()
    def get_damage(self):
        for sprite in self.enemy_sprites:
            if sprite.attack_rect and self.player.hitbox.colliderect(sprite.attack_rect):
                self.player.hurt(self.trans)
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
    def run(self):
        dt = self.clock.tick() / 1000
        while True:
            dt = self.clock.tick() / 1000
            self.event_loop()
            self.give_player_pos()
            self.hit()
            self.get_damage()
            self.display_surface.fill('beige')

            self.collide_sprites.update()



            self.all_sprites.draw(self.player,dt)
            self.all_sprites.update(dt)
            self.trans.play_trans(dt)

            pygame.display.update()




if '__main__':
    Game = Main()
    Game.run()
