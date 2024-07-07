import pygame
import data
import support
import chunks
import particle
import random
from consts import *


class Weapon(chunks.Sprite):
    def __init__(self, pos, kind):
        self.radius = WEAPONS[kind][WEAPON_RADID]
        self.size = WEAPONS[kind][WEAPON_SIZEID]
        self.pos = pygame.Vector2(pos)
        self.duration = WEAPONS[kind][WEAPON_DURATIONID]
        self.born_time = data.ticks
        super().__init__(
            None, data.assets.get_weapon(kind), data.game.weapon_groups[kind], pos
        )

    def check_finish(self):
        if data.ticks - self.born_time >= self.duration:
            self.on_finish()
            self.kill()

    def on_finish(self): ...

    def update(self):
        self.check_finish()


class PurpleHole(Weapon):
    def __init__(self, pos):
        super().__init__(pos, "purple_hole")

    def collidesuck(self, pos):
        return self.pos.distance_to(pos) <= self.radius

    def collidecenter(self, pos):
        return self.pos.distance_to(pos) <= self.size / 4

    def on_finish(self):
        data.assets.play("suck")
        particle.GrowParticle(
            self.rect.center, self.rect.w, 2, WEAPON_DISAPPEAR_SPEED, self.image
        )


class WhiteHole(Weapon):
    def __init__(self, pos):
        self.last_particle = data.ticks
        super().__init__(pos, "white_hole")

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
            [data.game.enemy_damages],
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
        super().__init__(pos, "supernova")
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
        particle.SupernovaExplosion(self.pos, SUPERNOVA_COLORS[0])


class WormHole(Weapon):
    def __init__(self, pos):
        super().__init__(pos, "worm_hole")
        data.assets.play("worm_hole")
        data.game.wormhole = self
        self.teleport_pos = pygame.Vector2(support.randpos(UNIVERSE_RECT))
        self.static_image = self.image.copy()
        self.speed = 0
        self.angle = 0

    def on_finish(self):
        data.assets.play("small_explosion")
        data.game.wormhole = None
        data.player.rect.center = self.teleport_pos
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


WEAPON_CLASSES = {
    "purple_hole": PurpleHole,
    "white_hole": WhiteHole,
    "supernova": Supernova,
    "worm_hole": WormHole,
}
