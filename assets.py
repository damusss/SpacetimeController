import pygame
import support
from consts import *
import data
import math
import json
import random


class Assets:
    def __init__(self):
        self.stars_cache = {}
        self.dust_cache = {}
        self.black_overlay = pygame.Surface((WIDTH, HEIGHT))
        self.easteregg = pygame.transform.scale_by(
            pygame.image.load("assets/ee.png").convert_alpha(), 0.5
        )
        self.completed = self.make_completed()
        self.make_dust()
        self.make_explosions()
        self.make_weapons()
        self.make_enemies()
        self.load_sounds()

    def load_sound(self, name, vol=1):
        sound = pygame.mixer.Sound(f"assets/sfx/{name}.ogg")
        sound.set_volume(vol)
        return {name: {"obj": sound, "vol": vol}}

    def load_sounds(self):
        sound = self.load_sound
        self.sounds = {
            **sound("asteroid_hit", 0.4),  # FINAL
            **sound("power_unlock", 0.7),  # FINAL
            **sound("big_explosion", 1),  # FINAL
            **sound("grab", 0.32),  # FINAL ##
            **sound("button_click", 0.8),  # FINAL #
            **sound("button_hover", 0.8),  # FINAL ##
            **sound("collect", 0.2),  # FINAL
            **sound("player_damage", 1),  # FINAL
            **sound("small_explosion", 1.2),  # FINAL
            **sound("suck", 0.8),  # FINAL
            **sound("wh_attack", 1),  # FINAL
            **sound("gameover", 1),  # FINAL
            **sound("supernova", 0.5),  # FINAL
            **sound("teleport", 0.8),  # FINAL #
            **sound("worm_hole", 0.5),  # FINAL
        }

    def play(self, name):
        self.sounds[name]["obj"].play()

    def music_play(self, name):
        pygame.mixer.music.unload()
        pygame.mixer.music.load(f"assets/{name}.ogg")
        pygame.mixer.music.play(-1, 0, 1000)

    def music_pause(self):
        pygame.mixer.music.pause()

    def music_resume(self):
        pygame.mixer.music.unpause()

    def update_volumes(self):
        pygame.mixer.music.set_volume(data.app.music_vol)
        for s in self.sounds.values():
            s["obj"].set_volume(s["vol"] * data.app.fx_vol)
        with open("volume.json", "w") as file:
            json.dump({"music": data.app.music_vol, "fx": data.app.fx_vol}, file)

    def get_completed(self):
        return self.completed.copy()

    def make_completed(self):
        font = self.font(12)
        txt = font.render("VICTORY", True, "green")
        w = txt.get_width() + SCALE_RES(10)
        base = pygame.Surface((w, w), pygame.SRCALPHA)
        txt = pygame.transform.rotate(txt, 30)
        pygame.draw.circle(base, (0, 20, 0), (w / 2, w / 2), w / 2)
        pygame.draw.circle(base, "green", (w / 2, w / 2), w / 2, 3)
        base.blit(txt, txt.get_rect(center=(w / 2, w / 2)))
        return base

    def get_overlay(self):
        return self.black_overlay

    def font(self, size=20):
        return pygame.Font("assets/font.ttf", SCALE_RES(size))

    def get_weapon(self, kind, color_supernova=False):
        res = self.weapons[kind].copy()
        if kind == "supernova" and color_supernova:
            res.fill((255, 200, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return res

    def get_particle(self):
        return self.wh_particle

    def get_wormhole(self, whsize, whw=15):
        wh = pygame.Surface((whsize, whsize), pygame.SRCALPHA)
        whrad, who = whsize / 2 - whsize / 6, whsize / 10
        pygame.draw.circle(
            wh,
            "green",
            (who + whrad, who + whrad),
            whrad,
            whw,
            False,
            True,
            False,
            False,
        )
        pygame.draw.circle(
            wh,
            "green",
            (whsize - whrad - who, who + whrad),
            whrad,
            whw,
            True,
            False,
            False,
            False,
        )
        pygame.draw.circle(
            wh,
            "green",
            (whrad + who, whsize - whrad - who),
            whrad,
            whw,
            False,
            False,
            True,
            False,
        )
        pygame.draw.circle(
            wh,
            "green",
            (whsize - whrad - who, whsize - whrad - who),
            whrad,
            whw,
            False,
            False,
            False,
            True,
        )
        wh.blit(self.get_dust(whsize, (0, 255, 0, 150), False), (0, 0))
        return wh

    def get_shield(self):
        w = WEAPONS["shield"][WEAPON_SIZEID]
        cw = w / SHIELD_MULT
        surf = pygame.Surface((w, w), pygame.SRCALPHA)
        mask_surf = pygame.Surface((w, w), pygame.SRCALPHA)
        pygame.draw.circle(mask_surf, "white", (w / 2, w / 2), cw / 2)
        segment = int(cw / 24)
        on = True
        color = RESOURCES["quartz"][RESOURCE_COLID]
        x = w / 2 - cw / 2
        while x < w / 2 + cw / 2:
            if on:
                pygame.draw.line(
                    surf,
                    color,
                    (x, w / 2 - cw / 2),
                    (x, w / 2 + cw / 2),
                    segment,
                )
                x += segment
            else:
                x += segment * 2
            on = not on
        y = w / 2 - cw / 2
        on = True
        while y < w / 2 + cw / 2:
            if on:
                pygame.draw.line(
                    surf,
                    color,
                    (w / 2 - cw / 2, y),
                    (w / 2 + cw / 2, y),
                    segment,
                )
                y += segment
            else:
                y += segment * 2
            on = not on
        surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.circle(surf, color, (w / 2, w / 2), cw / 2, int(segment / 1.5))
        surf.blit(self.get_dust(w, color, False), (0, 0))
        return surf

    def make_weapons(self):
        self.wh_particle = self.get_dust(WHITEHOLE_PARTICLE_SIZE, (0, 100, 200, 150))
        self.weapons = {
            "red_hole": self.get_blackhole(
                WEAPONS["red_hole"][WEAPON_SIZEID] / 2, (255, 0, 0), mult=1.8
            ),
            "shield": self.get_shield(),
            "purple_hole": self.get_blackhole(
                WEAPONS["purple_hole"][WEAPON_SIZEID] / 2, (120, 0, 255), mult=2
            ),
            "white_hole": self.get_blackhole(
                WEAPONS["white_hole"][WEAPON_SIZEID] / 2, (0, 100, 255), "white", 2
            ),
            "supernova": self.get_blackhole(
                WEAPONS["supernova"][WEAPON_SIZEID],
                (255, 255, 255),
                (255, 255, 255),
                1.4,
            ),
            "worm_hole": self.get_wormhole(WEAPONS["worm_hole"][WEAPON_SIZEID]),
            "worm_holeB": self.get_wormhole(
                WEAPONS["worm_hole"][WEAPON_SIZEID] * 2, 15 * 2
            ),
        }

    def make_explosions(self):
        self.explosions = [
            pygame.Surface(((200), (200)), pygame.SRCALPHA) for _ in range(2)
        ]
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
        s = SCALE_RES(300)
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

    def get_blackhole(
        self, size, color=(255, 220, 0), centercolor="black", mult=BLACKHOLE_MULT
    ):
        dustsize = int(size * mult)
        result = pygame.Surface((dustsize, dustsize), pygame.SRCALPHA)
        circle = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(circle, centercolor, (size // 2, size // 2), size // 2)
        dust = self.get_dust(dustsize, color, False)
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
        tw = w / 2.5
        tl, tr = w / 2 - tw / 2, w / 2 + tw / 2
        sth = h - h / 1.8
        tm = h - h / 3
        return [
            (0, h),
            (tl / 2, sth),
            (tl, tm),
            (w / 2, 0),
            (tr, tm),
            (tr + tl / 2, sth),
            (w, h),
            (w / 2, h - h / 6),
        ]

    def make_enemies(self):
        self.enemies = {}
        for enemy in ENEMIES:
            size, col = ENEMIES[enemy][ENEMY_SIZEID], ENEMIES[enemy][ENEMY_COLID]
            img = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.polygon(img, col, getattr(self, f"make_enemy_{enemy}")(*size))
            self.enemies[enemy] = img
