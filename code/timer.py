import pygame

class Timer:
    def __init__(self,duration):
        self.active = False
        self.duration = duration
        self.start_time = 0
    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()
    def deactivate(self):
        self.active = False
        self.start_time = 0
    def timeis(self):
        return pygame.time.get_ticks() - self.start_time
    def update(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.start_time >= self.duration):
            self.deactivate()

