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
import pause


class Game:
    def __init__(self): ...

    def enter(self, difficulty_name="normal"):
        self.difficulty_name = difficulty_name
        self.difficulty = DIFFICULTIES[difficulty_name]
        self.resources_amount = DIFFICULTY_RESOURCES[difficulty_name]
        self.total_resources = 0

        self.grabbed_one_resource = False
        self.collected_one_resource = False
        self.finished = False
        self.finish_reason = "none"
        self.finish_time = -9999
        self.paused = False

        data.player = player.Player()
        self.ui = ui.UI()
        self.pause = pause.Pause()

        self.chunk_manager = chunks.ChunkManager()
        self.asteroids = chunks.CameraRenderGroup()
        self.resources = chunks.CameraRenderGroup()
        self.objects = chunks.CameraRenderGroup()
        self.blackholes = chunks.CameraRenderGroup()

        self.purpleholes = pygame.sprite.Group()
        self.enemy_damages = pygame.sprite.Group()
        self.weapon_bodies = pygame.sprite.Group()
        self.wormhole = None

        self.weapon_groups = {
            "purple_hole": [
                self.purpleholes,
                self.objects,
                self.enemy_damages,
                self.weapon_bodies,
            ],
            "white_hole": [self.objects, self.weapon_bodies],
            "supernova": [self.objects, self.weapon_bodies],
            "worm_hole": self.objects,
        }

        for _ in range(ASTEROID_AMOUNT):
            pos = support.randpos(UNIVERSE_RECT)
            asteroid.Asteroid(pos)

        while self.total_resources < self.resources_amount:
            pos = support.randpos(UNIVERSE_RECT)
            asteroid.Asteroid(pos)

        for _ in range(BLACKHOLE_AMOUNT):
            pos = support.randpos(UNIVERSE_RECT)
            space.BlackHole(pos)

        self.collected_resources = 0
        self.inventory = dict.fromkeys(list(RESOURCES.keys()), 0)
        self.starter_inventory = list(RESOURCES.keys())

        self.pack_destroyed()
        self.started = False

    def pack_destroyed(self):
        self.last_pack = data.ticks
        self.pack = None
        self.pack_cooldown = support.randrange(ENEMY_PACK_COOLDOWN_RANGE)

    def gameover(self):
        self.explosion(data.player.rect.center, EXPLOSION_SIZE * 3)
        self.finished = True
        self.finish_reason = "gameover"
        self.finish_time = data.ticks
        self.paused = False

    def win(self):
        self.finished = True
        self.finish_reason = "win"
        self.finish_time = data.ticks
        self.paused = False

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1:
                self.try_attack("purple_hole")
            if e.key == pygame.K_2:
                self.try_attack("white_hole")
            if e.key == pygame.K_3:
                self.try_attack("supernova")
            if e.key == pygame.K_4:
                self.try_attack("worm_hole")
            if e.key == pygame.K_TAB:
                self.grabbed_one_resource = True
                self.collected_one_resource = True
            if e.key == pygame.K_ESCAPE:
                if self.paused:
                    self.pause.unpause()
                else:
                    self.pause.pause()

    def try_attack(self, kind):
        price = WEAPONS[kind][WEAPON_PRICEID]
        resource = WEAPONS[kind][WEAPON_RESOURCEID]
        if self.inventory[resource] >= price or resource in self.starter_inventory:
            if resource in self.starter_inventory:
                self.starter_inventory.remove(resource)
            else:
                self.inventory[resource] -= price
            data.player.attack(kind)

    def update(self):
        if self.paused:
            self.pause.update()
            return
        self.chunk_manager.update()
        self.asteroids.update()
        self.resources.update()
        self.objects.update()
        self.ui.update()
        if self.finished:
            return
        data.player.update()

        if self.pack is not None:
            self.pack.update()
        else:
            if data.ticks - self.last_pack >= self.pack_cooldown:
                pos = support.clamp_pos(
                    pygame.Vector2(data.player.rect.center)
                    + support.randvec(
                        support.randrange((CHUNK_SIZE * 4, CHUNK_SIZE * 6))
                    ),
                    UNIVERSE_RECT,
                )
                self.pack = enemy.EnemyPack(pos, random.choice(list(ENEMIES.keys())))

        if not self.started:
            particle.GrowParticle(
                data.player.rect.center,
                1,
                WEAPONS["worm_hole"][WEAPON_SIZEID] * 1.6,
                700,
                data.images.get_weapon("worm_holeB"),
                [self.objects],
            )
            self.started = True

    def explosion(self, pos, size=EXPLOSION_SIZE):
        particle.Explosion(pos, size)

    def draw(self):
        self.chunk_manager.draw()
        self.blackholes.draw()
        self.asteroids.draw()
        self.resources.draw()
        self.objects.draw()
        if self.finished:
            self.ui.draw_finish()
            return
        if self.pack is not None:
            self.pack.draw()
        data.player.draw()
        self.ui.draw()
        if self.paused:
            self.pause.draw()
