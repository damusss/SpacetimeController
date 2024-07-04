import pygame
import support
from consts import *
import data
import math
import random


class ImageMaker:
    def __init__(self):
        self.stars_cache = {}
        self.dust_cache = {}
        self.make_explosions()
        self.make_dust()
        self.make_enemies()

    def font(self, size=20):
        return pygame.Font("assets/font.ttf", size)
    
    def make_explosions(self):
        self.explosions = [pygame.Surface((200, 200), pygame.SRCALPHA) for _ in range(2)]
        for exp, s in zip(self.explosions, (10, 2)):
            pygame.draw.circle(exp, "white", (100, 100), 100, s)
    
    def get_explosion(self, color, i):
        part = self.explosions[i].copy()
        part.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        return part

    def get_star(self, size, color):
        if (size, color) in self.stars_cache:
            return self.stars_cache[(size, color)]

        result = pygame.Surface((size, size), pygame.SRCALPHA)
        if size == 1:
            result.fill(color)
        else:
            pygame.draw.circle(result, color, (size // 2, size // 2), size // 2)

        self.stars_cache[(size, color)] = result
        return result

    def get_player(self):
        img = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
        w, h = PLAYER_SIZE
        cx = w / 10
        cyf = h / 3.2
        cyn = h / 5.2
        td = cx * 1.5
        tx = w / 16
        ty = h / 8
        tm = h / 3
        points = [
            # left wing
            (0, h - h / 5),
            # top pointy thing
            (w / 2 - cx, cyf),
            (w / 2 - cx, cyn),
            (w / 2, 0),
            (w / 2 + cx, cyn),
            (w / 2 + cx, cyf),
            # right wing
            (w, h - h / 5),
            # right thruster
            (w / 2 + td, h - tm),
            (w / 2 + td, h - tm + ty),
            (w / 2 + td - tx, h - tm + ty),
            (w / 2 + td - tx, h - tm),
            # midpoint
            (w / 2, h - h / 3),
            # left thruster
            (w / 2 - td + tx, h - tm),
            (w / 2 - td + tx, h - tm + ty),
            (w / 2 - td, h - tm + ty),
            (w / 2 - td, h - tm),
        ]
        pygame.draw.polygon(img, PLAYER_COL, points)
        return img

    def get_dust(self, size, color, cache=True):
        if (size, color) in self.dust_cache and cache:
            return self.dust_cache[(size, color)]

        result = pygame.transform.scale(self.dust_surf, (size, size))
        result.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

        if cache:
            self.dust_cache[(size, color)] = result
        return result

    def make_dust(self):
        s = 300
        self.dust_surf = pygame.Surface((s, s), pygame.SRCALPHA)
        for x in range(self.dust_surf.get_width()):
            for y in range(self.dust_surf.get_height()):
                dist = math.sqrt((x - s // 2) ** 2 + (y - s // 2) ** 2)
                self.dust_surf.set_at(
                    (x, y),
                    pygame.Color(
                        255,
                        255,
                        255,
                        max(0, min(255, int((1 - ((dist / (s // 2)) ** 1.2)) * 255))),
                    ),
                )

    def get_asteroid(self, radius, color, points_range=ASTEROID_POINTS_RANGE):
        points = support.asteroid_points(random.randint(*points_range), radius, 0.3)
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.polygon(
            surf, color, [(p[0] + radius, p[1] + radius) for p in points]
        )
        return surf

    def get_blackhole(self, size):
        dustsize = int(size * BLACKHOLE_MULT)
        result = pygame.Surface((dustsize, dustsize), pygame.SRCALPHA)
        circle = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(circle, "black", (size // 2, size // 2), size // 2)
        dust = self.get_dust(dustsize, (255, 220, 0), False)
        result.blit(dust, (0, 0))
        result.blit(
            circle, circle.get_rect().move_to(center=(dustsize / 2, dustsize / 2))
        )
        return result

    def get_enemy(self, type):
        return self.enemies[type]

    def make_enemy_green(self, w, h):
        return [
            (0, h),
            (w / 2, 0),
            (w, h),
        ]

    def make_enemy_pink(self, w, h):
        return [(0, h), (w / 2, 0), (w, h), (w / 2, h - h / 4)]

    def make_enemy_yellow(self, w, h):
        bw = w / 10
        return [
            (0, h),
            (w / 2 - bw / 2, h / 4),
            (w / 2, 0),
            (w / 2 + bw / 2, h / 4),
            (w, h),
            (w / 2, h - h / 4),
        ]

    def make_enemy_blue(self, w, h):
        tw = w / 3
        return [
            (0, h),
            (tw / 2, 0),
            (tw, h),
            (tw + tw / 2, 0),
            (tw * 2, h),
            (tw * 2 + tw / 2, 0),
            (w, h),
        ]

    def make_enemies(self):
        self.enemies = {}
        for enemy in ENEMIES:
            size, col = ENEMIES[enemy][ENEMY_SIZEID], ENEMIES[enemy][ENEMY_COLID]
            img = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.polygon(img, col, getattr(self, f"make_enemy_{enemy}")(*size))
            self.enemies[enemy] = img
