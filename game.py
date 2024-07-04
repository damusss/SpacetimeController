import pygame
from consts import *
import support
import data
import player
import chunks
import asteroid
import space
import ui
import enemy
import random
import particle


class Game:
    def __init__(self): ...

    def enter(self, difficulty=1):
        self.difficulty = difficulty
        self.total_resources = 0

        data.player = player.Player()
        self.chunk_manager = chunks.ChunkManager()
        self.asteroids = chunks.CameraRenderGroup()
        self.resources = chunks.CameraRenderGroup()
        self.objects = chunks.CameraRenderGroup()
        self.blackholes = chunks.CameraRenderGroup()
        self.ui = ui.UI()

        for _ in range(ASTEROID_AMOUNT):
            pos = support.randpos(UNIVERSE_RECT)
            asteroid.Asteroid(pos)

        for _ in range(BLACKHOLE_AMOUNT):
            pos = support.randpos(UNIVERSE_RECT)
            space.BlackHole(pos)

        self.resources_amount = self.total_resources // (
            MAX_DIFFICULTY - self.difficulty
        )
        self.collected_resources = 0

        self.pack_destroyed()

    def pack_destroyed(self):
        self.last_pack = data.ticks
        self.pack = None
        self.pack_cooldown = support.randrange(ENEMY_PACK_COOLDOWN_RANGE)

    def gameover(self, reason="dead"): ...

    def win(self): ...

    def event(self, e): ...

    def update(self):
        data.player.update()
        self.chunk_manager.update()
        self.asteroids.update()
        self.resources.update()
        self.objects.update()
        self.ui.update()

        if self.pack is not None:
            self.pack.update()
        else:
            if data.ticks - self.last_pack >= self.pack_cooldown:
                pos = pygame.Vector2(data.player.rect.center) + support.randvec(
                    support.randrange((CHUNK_SIZE * 4, CHUNK_SIZE * 6))
                )
                self.pack = enemy.EnemyPack(pos, random.choice(list(ENEMIES.keys())))
                
    def explosion(self, pos, size=EXPLOSION_SIZE):
        particle.Explosion(pos, size)

    def draw(self):
        self.chunk_manager.draw()
        self.blackholes.draw()
        self.asteroids.draw()
        self.resources.draw()
        self.objects.draw()
        if self.pack is not None:
            self.pack.draw()
        data.player.draw()
        self.ui.draw()
