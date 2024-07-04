import pygame
import data
import support
import chunks
from consts import *

class GrowParticle(chunks.Sprite):
    def __init__(self, pos, start_size, end_size, time, image):
        self.start_size = start_size
        self.end_size = end_size
        self.time = time
        self.start_time = data.ticks
        self.original_image = image
        self.size = self.start_size
        super().__init__(None, self.original_image, data.game.objects, pos)
        self.update()
        
    def update(self):
        self.size = (self.end_size*(data.ticks-self.start_time))/self.time
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.size > self.end_size:
            self.kill()
            return
        
class Explosion(GrowParticle):
    def __init__(self, pos, size=EXPLOSION_SIZE, color=None, startsize=None):
        if color is None:
            color = EXPLOSION_COLORS[0]
        if startsize is None:
            startsize = 1
        self.color = color
        self.spawned_section = False
        super().__init__(pos, startsize, size, EXPLOSION_TIME, data.images.get_explosion(color, 1 if color == EXPLOSION_GRAY else 0))
        if color != EXPLOSION_GRAY:
            Explosion(pos, size, EXPLOSION_GRAY, startsize/2)
            
    def update(self):
        GrowParticle.update(self)
        if self.size > self.end_size/9 and self.color != EXPLOSION_LAST and self.color != EXPLOSION_GRAY and not self.spawned_section:
            Explosion(self.rect.center, self.end_size, EXPLOSION_COLORS[EXPLOSION_COLORS.index(self.color)+1])
            self.spawned_section = True
