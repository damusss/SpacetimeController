import pygame
import support
import data
from consts import *
import chunks
import random


class AsteroidResource(chunks.Sprite):
    def __init__(self, parent: "Asteroid", resource):
        self.parent = parent
        self.resource = resource
        size = support.randrange((parent.rect.w // 6, parent.rect.w // 3))
        self.color = support.alter_color(RESOURCES[resource][RESOURCE_COLID])
        image = data.assets.get_asteroid(size // 2, self.color, RESOURCE_POINTS_RANGE)
        direction = support.randvec(parent.rect.w // 4)
        self.rel_pos = direction
        self.dir = support.randvec()
        self.speed = support.randrange(FRAGMENT_SPEED_RANGE) / 2
        self.escape_time = 0
        self.can_destroy = True
        self.follow_offset = support.randvec(10)
        self.blackhole = None
        self.blackhole_pos = pygame.Vector2()
        self.blackhole_len = 0
        self.blackhole_angle = 0
        self.static_blackhole_pos = self.blackhole_pos.copy()
        self.rot_speed = support.randrange(RESOURCE_ROT_SPEED_RANGE)
        data.game.total_resources += 1
        super().__init__(
            None,
            image,
            [data.game.resources, parent.resources],
            parent.rect.center + direction,
        )

    def escape(self):
        self.escape_time = data.ticks - random.randint(500, 2000)
        self.can_destroy = True
        for bh in data.game.blackholes:
            if bh.collideextern(self.rect.center):
                data.game.collected_one_resource = True
                self.blackhole = bh
                self.can_destroy = False
                self.blackhole.resources.append(self)
                self.blackhole_pos = self.rect.center - bh.pos
                self.static_blackhole_pos = self.blackhole_pos.copy()
                self.blackhole_len = self.blackhole_pos.magnitude()
                break

    def collect(self):
        [
            AsteroidFragment(self.rect.center, self.color, FRAGMENT_COOLDOWN / 2)
            for _ in range(random.randint(2, 3))
        ]
        if data.game.collected_resources < data.game.resources_amount:
            data.game.collected_resources += 1
        elif not data.game.finished:
            data.game.win()
        prev_canbuy = {
            wn: data.game.inventory[WEAPONS[wn][WEAPON_RESOURCEID]]
            >= WEAPONS[wn][WEAPON_PRICEID]
            for wn in WEAPONS.keys()
        }
        data.game.inventory[self.resource] += 1
        canbuy = {
            wn: data.game.inventory[WEAPONS[wn][WEAPON_RESOURCEID]]
            >= WEAPONS[wn][WEAPON_PRICEID]
            for wn in WEAPONS.keys()
        }
        for wn, cb in canbuy.items():
            if cb != prev_canbuy[wn]:
                data.assets.play("power_unlock")
        data.player.heal(RESOURCES[self.resource][RESOURCE_HEALID])
        data.game.explosion(self.rect.center, self.rect.w * 2)
        data.assets.play("collect")
        self.kill()

    def update(self):
        if not self.parent.destroyed:
            return

        if self.blackhole is not None:
            self.blackhole_angle += self.rot_speed * data.dt
            self.blackhole_pos = self.static_blackhole_pos.rotate(self.blackhole_angle)
            self.blackhole_len -= RESOURCE_COLLECT_SPEED * data.dt
            self.blackhole_pos.scale_to_length(self.blackhole_len)
            self.rect.center = self.blackhole.pos + self.blackhole_pos
            if self.blackhole_len <= 10:
                self.collect()
            return

        if self.can_destroy:
            if self.rect.colliderect(UNIVERSE_RECT):
                self.rect.center += self.dir * self.speed * data.dt
        else:
            follow = data.player.get_follow_point() + self.follow_offset
            dir = follow - self.rect.center
            if dir.magnitude() <= 2:
                self.rect.center = follow
                return
            if dir.magnitude() != 0:
                dir.normalize_ip()
            self.rect.center += (
                dir
                * max(data.player.speed - data.player.speed / 15, PLAYER_SPEED / 2)
                * data.dt
            )


class AsteroidFragment(chunks.Sprite):
    def __init__(self, center, color, cooldown=FRAGMENT_COOLDOWN):
        self.cooldown = cooldown
        size = support.randrange(FRAGMENT_SIZE_RANGE)
        self.dir = support.randvec()
        self.speed = support.randrange(FRAGMENT_SPEED_RANGE)
        self.create_time = data.ticks - random.randint(300, 500)
        super().__init__(
            None,
            data.assets.get_asteroid(size // 2, color, RESOURCE_POINTS_RANGE),
            data.game.objects,
            center,
        )

    def update(self):
        if data.ticks - self.create_time >= self.cooldown:
            self.kill()
            return
        self.rect.center += self.dir * self.speed * data.dt


class Asteroid(chunks.Sprite):
    def __init__(self, center):
        size = support.randrange(ASTEROID_SIZE_RANGE)
        self.color = ASTEROID_COL1.lerp(ASTEROID_COL2, random.random())
        image = data.assets.get_asteroid(size // 2, self.color)
        self.amount = support.randrange(RESOURCE_AMOUNT_RANGE)
        self.health = self.amount
        self.resource = random.choice(RESOURCES_WEIGHTED)
        self.resources: list[AsteroidResource] = pygame.sprite.Group()
        self.destroyed = False
        self.dir = support.randvec()
        self.speed = support.randrange(ASTEROID_SPEED_RANGE)
        self.change_time = data.ticks
        self.is_hit = False
        self.hit_time = data.ticks
        super().__init__(None, image, data.game.asteroids, center)
        self.hitbox = pygame.FRect(0, 0, self.rect.w / 1.5, self.rect.h / 1.5)
        [AsteroidResource(self, self.resource) for _ in range(self.amount)]

    def hit(self):
        self.hit_time = data.ticks
        self.health -= 1
        self.is_hit = True
        [
            AsteroidFragment(self.rect.center, self.color)
            for _ in range(random.randint(3, 5))
        ]
        if self.health <= 0:
            self.destroy()
        else:
            data.assets.play("asteroid_hit")

    def destroy(self):
        data.game.explosion(self.rect.center, self.rect.w * 1.5)
        self.destroyed = True
        data.assets.play("small_explosion")
        self.kill()
        for res in self.resources:
            res.escape()

    def update(self):
        if self.destroyed:
            return
        in_universe = self.rect.colliderect(UNIVERSE_RECT)
        if data.ticks - self.hit_time >= ASTEROID_HIT_COOLDOWN:
            self.is_hit = False
        if not in_universe:
            self.dir = support.randvec()
            return
        if data.ticks - self.change_time >= 60000:
            self.dir = support.randvec()
            self.change_time = data.ticks

        self.rect.topleft += self.dir * self.speed * data.dt
        self.hitbox.center = self.rect.center
        for res in self.resources:
            res.rect.center = self.rect.center + res.rel_pos
