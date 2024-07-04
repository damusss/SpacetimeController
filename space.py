import pygame
import data
import random
import support
import chunks
from consts import *


class BlackHole(chunks.Sprite):
    def __init__(self, pos):
        size = support.randrange(BLACKHOLE_SIZE_RANGE)
        self.size = size
        self.pos = pygame.Vector2(pos)
        self.resources = []
        super().__init__(
            None, data.images.get_blackhole(size), data.game.blackholes, pos
        )

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.size / 2

    def collideextern(self, pos):
        return self.pos.distance_to(pos) <= (self.size * BLACKHOLE_MULT) / 2
