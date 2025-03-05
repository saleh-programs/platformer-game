import  pygame
class transition():
    def __init__(self,player):
        self.surf = pygame.Surface((1600,900))
        self.surf.set_colorkey('white')
        self.display_surface = pygame.display.get_surface()

        self.key = 0
        self.direction = 1
        self.transitioning = False
        self.player = player

        self.surf2 = pygame.Surface((1600,900))
        self.surf2.fill('red')
        self.surf.set_colorkey('green')
        self.key2 = 150
        self.got_hit = False
    def play_trans(self,dt):
        if self.transitioning:
            self.surf.set_alpha(int(self.key))
            self.display_surface.blit(self.surf,(0,0))
            self.key += 1200 * self.direction * dt
            if self.key >= 500:
                self.direction = -1
            elif self.key >= 255:
                self.player.pos = pygame.math.Vector2((3240, 4200))
            elif self.key <= 0:
                self.transitioning = False
                self.key = 0
                self.direction = 1
    def play_hit(self,dt):
        self.surf2.set_alpha(self.key2)
        self.display_surface.blit(self.surf2,(0,0))
        self.key2 -= 700 * dt
        if self.key2 <= 0:
            self.key2 = 150
            self.got_hit = False

