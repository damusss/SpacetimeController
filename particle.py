import pygame
import data
import support
import chunks
from consts import *


class EasterEgg(chunks.Sprite):
    def __init__(self, pos):
        super().__init__(None, data.assets.easteregg, [data.game.objects], pos)
        self.static_image = self.image.copy()
        self.angle = 0
        self.born_time = data.ticks

    def update(self):
        self.angle -= data.dt * 150
        self.image = pygame.transform.rotate(self.static_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if data.ticks - self.born_time >= 8000:
            self.kill()


class Trail:
    def __init__(self, speed, color):
        self.speed = speed
        self.color = color
        self.start_points = None
        self.points = []

    def set_start(self, points):
        self.start_points = points

    def add(self, points):
        self.points.append(points)

    def draw(self):
        points1 = []
        points2 = []
        newpoints = []
        for p1, p2 in self.points:
            d1 = support.norm(p1 - p2)
            d2 = support.norm(p2 - p1)
            p1 -= d1 * self.speed * data.dt
            p2 -= d2 * self.speed * data.dt
            if p1.distance_to(p2) > 1:
                newpoints.append((p1, p2))
                points1.append(CENTER + p1 - data.player.rect.center)
                points2.insert(0, CENTER + p2 - data.player.rect.center)

        if self.start_points is not None:
            points1.append(self.start_points[0] + CENTER - data.player.rect.center)
            points2.insert(0, self.start_points[1] + CENTER - data.player.rect.center)

        self.points = newpoints
        if len(points1) + len(points2) > 2:
            pygame.draw.polygon(data.screen, self.color, points1 + points2)


class GrowParticle(chunks.Sprite):
    def __init__(
        self,
        pos,
        start_size,
        end_size,
        time,
        image,
        groups=None,
        finish_func=None,
        follow_player=False,
    ):
        self.finish_func = finish_func
        self.follow_player = follow_player
        if groups is None:
            groups = []
        self.start_size = start_size
        self.end_size = end_size
        self.time = time
        self.start_time = data.ticks
        self.original_image = image
        self.size = self.start_size
        super().__init__(None, self.original_image, [data.game.objects] + groups, pos)
        self.update()

    def update(self):
        if self.start_size < self.end_size:
            self.size = (self.end_size * (data.ticks - self.start_time)) / self.time
        else:
            self.size = pygame.math.lerp(
                self.start_size,
                self.end_size,
                (data.ticks - self.start_time) / self.time,
            )
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.follow_player:
            self.rect.center = data.player.rect.center
        if (self.start_size < self.end_size and self.size >= self.end_size) or (
            self.start_size > self.end_size and self.size <= self.end_size
        ):
            self.kill()
            if self.finish_func:
                self.finish_func()
            return


class MoveParticle(chunks.Sprite):
    def __init__(self, pos, direction, speed, distance, image, groups):
        self.direction = support.norm(direction)
        self.speed = speed
        self.distance = distance
        self.start_pos = pygame.Vector2(pos)
        super().__init__(None, image, groups + [data.game.objects], pos)

    def collidecenter(self, pos):
        return pygame.Vector2(self.rect.center).distance_to(pos) <= self.rect.w / 2

    def update(self):
        self.rect.center += self.direction * self.speed * data.dt
        if self.start_pos.distance_to(self.rect.center) > self.distance:
            self.kill()


class Explosion(GrowParticle):
    def __init__(self, pos, size=EXPLOSION_SIZE, color=None, startsize=None):
        if color is None:
            color = EXPLOSION_COLS[0]
        if startsize is None:
            startsize = 1
        self.color = color
        self.spawned_section = False
        super().__init__(
            pos,
            startsize,
            size,
            EXPLOSION_TIME,
            data.assets.get_explosion(color, 1 if color == EXPLOSION_GRAY else 0),
        )
        if color != EXPLOSION_GRAY:
            Explosion(pos, size, EXPLOSION_GRAY, startsize / 2)

    def update(self):
        GrowParticle.update(self)
        if (
            self.size > self.end_size / 9
            and self.color != EXPLOSION_LAST
            and self.color != EXPLOSION_GRAY
            and not self.spawned_section
        ):
            Explosion(
                self.rect.center,
                self.end_size,
                EXPLOSION_COLS[EXPLOSION_COLS.index(self.color) + 1],
            )
            self.spawned_section = True


class SupernovaExplosion(GrowParticle):
    def __init__(self, pos, color):
        self.color = color
        self.spawned_section = False
        super().__init__(
            pos,
            WEAPONS["supernova"][WEAPON_SIZEID] / 2,
            WEAPONS["supernova"][WEAPON_RADID] * 2,
            SUPERNOVA_EXPLOSION_TIME,
            data.assets.get_explosion(color, 0),
            [data.game.enemy_damages, data.game.asteroid_damages],
        )

    def collidecenter(self, pos):
        return pygame.Vector2(self.rect.center).distance_to(pos) <= self.rect.w / 2

    def update(self):
        GrowParticle.update(self)
        if (
            self.size > self.end_size / 9
            and self.color != SUPERNOVA_LAST
            and not self.spawned_section
        ):
            SupernovaExplosion(
                self.rect.center,
                SUPERNOVA_COLS[SUPERNOVA_COLS.index(self.color) + 1],
            )
            self.spawned_section = True
