import pygame
from consts import *
import support
import data
import player
import chunks
import asteroid
import ui
import enemy
import random
import particle
import pause
import os
import json


class Game:
    def __init__(self): ...

    def enter(self, difficulty_name="normal", mobile=False):
        self.difficulty_name = difficulty_name
        self.mobile = mobile
        self.grabbed_one_resource = False
        self.collected_one_resource = False

        self.finished = False
        self.finish_reason = "none"
        self.finish_time = -9999

        self.paused = False
        self.start_time = data.ticks
        self.time_elapsed = -1
        self.is_best_time = False
        self.started = False
        self.pack_cooldown = ENEMY_PACK_COOLDOWN_START + ENEMY_PACK_COOLDOWN_DECREASE
        self.extra_enemies = 0

        self.resources_amount = DIFFICULTY_RESOURCES[difficulty_name]
        self.total_resources = 0
        self.collected_resources = 0
        self.inventory = dict.fromkeys(list(RESOURCES.keys()), 0)
        self.starter_inventory = list(RESOURCES.keys())

        self.check_tutorial_removal()
        self.pack_destroyed()

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
        self.shield = None

        self.weapon_groups = {
            "red_hole": [
                self.objects,
                self.enemy_damages,
                self.weapon_bodies,
            ],
            "shield": [self.objects],
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
            chunks.BlackHole(pos)

    def check_tutorial_removal(self):
        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                tdata = json.load(file)
                if isinstance(tdata, dict):
                    for k, v in tdata.items():
                        if v != -1:
                            self.grabbed_one_resource = True
                            self.collected_one_resource = True
                            break

    def restart(self):
        gor, cor = (
            self.grabbed_one_resource,
            self.collected_one_resource,
        )
        data.app.enter_game(self.difficulty_name, self.mobile)
        self.grabbed_one_resource = gor
        self.collected_one_resource = cor

    def pack_destroyed(self):
        self.last_pack = data.ticks
        self.pack = None
        self.pack_cooldown -= ENEMY_PACK_COOLDOWN_DECREASE
        self.pack_cooldown = max(self.pack_cooldown, ENEMY_PACK_COOLDOWN_MIN)
        self.extra_enemies += 1

    def gameover(self):
        self.explosion(data.player.rect.center, EXPLOSION_SIZE * 3)
        self.finish_reason = "gameover"
        self.finish()
        data.assets.play("gameover")

    def win(self):
        self.finish_reason = "win"
        self.finish()
        self.save_data()

    def finish(self):
        self.finished = True
        self.finish_time = data.ticks
        self.paused = False
        self.time_elapsed = self.finish_time - self.start_time

    def save_data(self):
        if not os.path.exists("data.json"):
            with open("data.json", "w") as file:
                json.dump({key: -1 for key in DIFFICULTIES.keys()}, file)
        newdata = None
        with open("data.json", "r") as file:
            curdata = json.load(file)
            if not isinstance(curdata, dict):
                curdata = {key: -1 for key in DIFFICULTIES.keys()}
            if self.difficulty_name not in curdata:
                curdata[self.difficulty_name] = -1
            if (
                self.time_elapsed < curdata[self.difficulty_name]
                or curdata[self.difficulty_name] < 0
            ):
                curdata[self.difficulty_name] = self.time_elapsed
                newdata = curdata
                self.is_best_time = True
        if newdata is not None:
            with open("data.json", "w") as file:
                json.dump(newdata, file)

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1:
                self.try_attack("red_hole")
            if e.key == pygame.K_2:
                self.try_attack("purple_hole")
            if e.key == pygame.K_3:
                self.try_attack("white_hole")
            if e.key == pygame.K_4:
                self.try_attack("worm_hole")
            if e.key == pygame.K_5:
                self.try_attack("supernova")
            if e.key == pygame.K_6:
                self.try_attack("shield")
            if e.key == pygame.K_TAB:
                self.grabbed_one_resource = True
                self.collected_one_resource = True
            if e.key == pygame.K_p:
                particle.EasterEgg(data.player.rect.center)
            if e.key == pygame.K_ESCAPE:
                if self.paused:
                    self.pause.unpause()
                else:
                    self.pause.pause()
        elif e.type == pygame.MOUSEBUTTONUP:
            for wr, kind in self.ui.weapon_rects:
                if wr.collidepoint(e.pos) and wr.collidepoint(data.app.start_click):
                    self.try_attack(kind)
                    break

    def try_attack(self, kind):
        if (
            (kind == "red_hole" and self.pack is None)
            or (kind == "shield" and self.shield is not None)
            or (kind == "worm_hole" and self.wormhole is not None)
        ):
            return
        price = WEAPONS[kind][WEAPON_PRICEID]
        resource = WEAPONS[kind][WEAPON_RESOURCEID]
        if self.inventory[resource] >= price or resource in self.starter_inventory:
            if resource in self.starter_inventory:
                self.starter_inventory = []
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
            data.assets.play("teleport")
            particle.GrowParticle(
                data.player.rect.center,
                1,
                WEAPONS["worm_hole"][WEAPON_SIZEID] * 1.6,
                700,
                data.assets.get_weapon("worm_holeB"),
                [self.objects],
            )
            self.started = True

    def explosion(self, pos, size=EXPLOSION_SIZE):
        particle.Explosion(pos, size)

    def draw(self):
        self.chunk_manager.draw()
        self.blackholes.draw()
        self.asteroids.draw()
        data.player.draw_early()
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
