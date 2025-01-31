import pygame
import data
import support
import chunks
import particle
import random
import functools
from consts import *


class Weapon(chunks.Sprite):
    def __init__(self, pos, kind, groups):
        self.radius = WEAPONS[kind][WEAPON_RADID]
        self.size = WEAPONS[kind][WEAPON_SIZEID]
        self.pos = pygame.Vector2(pos)
        self.duration = WEAPONS[kind][WEAPON_DURATIONID]
        self.born_time = data.ticks
        super().__init__(None, data.assets.get_weapon(kind), groups, pos)

    def check_finish(self):
        if data.ticks - self.born_time >= self.duration:
            self.on_finish()
            self.kill()

    def on_finish(self): ...

    def update(self):
        self.check_finish()


class PurpleHole(Weapon):
    def __init__(self, pos):
        super().__init__(
            pos,
            "purple_hole",
            [
                data.game.purpleholes,
                data.game.objects,
                data.game.enemy_damages,
                data.game.weapon_bodies,
                data.game.asteroid_damages,
            ],
        )
        self.sucked = set()

    def collidesuck(self, pos):
        return self.pos.distance_to(pos) <= self.radius

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.size / 4

    def on_finish(self):
        data.assets.play("suck")
        particle.GrowParticle(
            self.rect.center, self.rect.w, 2, WEAPON_DISAPPEAR_SPEED, self.image
        )


class RedHoleClone(Weapon):
    def __init__(self, pos):
        super().__init__(
            pos,
            "red_hole",
            [
                data.game.objects,
                data.game.enemy_damages,
                data.game.weapon_bodies,
                data.game.asteroid_damages,
            ],
        )
        self.duration += random.randint(500, 1200)

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.radius / 2

    def on_finish(self):
        data.assets.play("suck")
        particle.GrowParticle(
            self.rect.center, self.rect.w, 2, WEAPON_DISAPPEAR_SPEED, self.image
        )


class WhiteHole(Weapon):
    def __init__(self, pos):
        self.last_particle = data.ticks
        super().__init__(
            pos, "white_hole", [data.game.objects, data.game.weapon_bodies]
        )

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.size / 4

    def shoot(self):
        # if random.randint(0, 100) < 30:
        data.assets.play("wh_attack")
        particle.MoveParticle(
            self.pos,
            support.randvec(),
            WHITEHOLE_PARTICLE_SPEED,
            self.radius,
            data.assets.get_particle(),
            [data.game.enemy_damages, data.game.asteroid_damages],
        )

    def on_finish(self):
        data.assets.play("suck")
        particle.GrowParticle(
            self.rect.center, self.rect.w, 2, WEAPON_DISAPPEAR_SPEED, self.image
        )

    def update(self):
        if data.ticks - self.last_particle >= WHITEHOLE_SHOOT_COOLDOWN:
            self.shoot()
            self.last_particle = data.ticks
        self.check_finish()


class Supernova(Weapon):
    def __init__(self, pos):
        super().__init__(pos, "supernova", [data.game.objects, data.game.weapon_bodies])
        self.original_image = self.image
        data.assets.play("supernova")

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.size / (1.4 * 2)

    def update(self):
        self.check_finish()
        self.image = self.original_image.copy()
        color = SUPERNOVA_START.lerp(
            SUPRNOVA_END,
            pygame.math.clamp((data.ticks - self.born_time) / self.duration, 0, 1),
        )
        self.image.fill(color, special_flags=pygame.BLEND_RGB_MULT)

    def on_finish(self):
        data.assets.play("big_explosion")
        particle.SupernovaExplosion(self.pos, SUPERNOVA_COLS[0])


class WormHole(Weapon):
    def __init__(self, pos):
        super().__init__(pos, "worm_hole", [data.game.objects])
        data.assets.play("worm_hole")
        data.game.wormhole = self
        self.teleport_pos = pygame.Vector2(support.randpos(UNIVERSE_RECT))
        self.static_image = self.image.copy()
        self.speed = 0
        self.angle = 0

    def on_finish(self):
        data.assets.play("teleport")
        data.game.wormhole = None
        data.player.rect.center = self.teleport_pos
        for res in data.player.resources:
            res.rect.center = self.teleport_pos
        particle.GrowParticle(
            self.teleport_pos,
            1,
            self.rect.w * 1.5,
            700,
            data.assets.get_weapon("worm_holeB"),
            [data.game.objects],
        )

    def update(self):
        self.check_finish()
        self.speed += data.dt * WORMHOLE_ACC
        self.angle += data.dt * self.speed
        self.image = pygame.transform.rotate(self.static_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


def RedHole():
    for enemy in data.game.pack.enemies:
        pos = enemy.rect.center
        particle.GrowParticle(
            pos,
            2,
            WEAPONS["red_hole"][WEAPON_SIZEID],
            random.randint(150, 250),
            data.assets.get_weapon("red_hole"),
            finish_func=functools.partial(RedHoleClone, pos),
        )


class Shield(Weapon):
    def __init__(self, *_):
        super().__init__(data.player.rect.center, "shield", [data.game.objects])
        self.static_image = self.image
        self.angle = 0
        data.game.shield = self
        data.assets.play("shield")

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.radius

    def on_finish(self):
        data.game.shield = None
        data.assets.play("suck")
        particle.GrowParticle(
            self.rect.center, self.rect.w, 2, WEAPON_DISAPPEAR_SPEED, self.image
        )

    def update(self):
        self.check_finish()
        self.angle += data.dt * SHIELD_ROT_SPEED
        self.image = pygame.transform.rotate(self.static_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = data.player.rect.center
        self.pos = pygame.Vector2(self.rect.center)


WEAPON_CLASSES = {
    "red_hole": RedHole,
    "purple_hole": PurpleHole,
    "white_hole": WhiteHole,
    "supernova": Supernova,
    "worm_hole": WormHole,
    "shield": Shield,
}
