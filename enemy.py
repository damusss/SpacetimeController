import pygame
import data
import support
import random
import chunks
import math
from consts import *


class Enemy(chunks.Sprite):
    def __init__(self, pos, enemy_type, pack: "EnemyPack"):
        self.damage = ENEMIES[enemy_type][ENEMY_DAMAGEID]
        self.target_pos = pygame.Vector2()
        self.speed = ENEMIES[enemy_type][ENEMY_SPEEDID]
        self.dir = pygame.Vector2()
        self.prev_dir = pygame.Vector2()
        self.push_dir = pygame.Vector2()
        self.pushing = False
        self.green_offset = support.randvec(random.randint(100, 300))
        self.blue_offset = support.randvec(random.randint(300, 800))
        self.angle = 0
        self.push_speed = self.speed / 10
        self.sucked = False

        super().__init__(None, data.assets.get_enemy(enemy_type), pack.enemies, pos)
        self.hitbox = self.rect.inflate(self.rect.w / 3, self.rect.h / 3)
        self.static_image = self.image

    def update(self):
        self.update_collisions()
        self.dir = self.target_pos - self.rect.center
        if self.weapon_collisions():
            return
        support.norm(self.dir)
        support.norm(self.push_dir)
        self.rect.center += (
            self.dir * self.speed * data.dt
            + (self.push_dir * (self.push_speed) * data.dt) * self.pushing
        )

        angle = math.degrees(math.atan2(-self.dir.y, self.dir.x)) - 90
        if angle >= -270 and angle < -270 + 80 and self.angle <= 90 and self.angle > 10:
            self.angle = -270 - (90 - self.angle)
        elif (
            angle <= 90 and angle > 10 and self.angle >= -270 and self.angle < -270 + 80
        ):
            self.angle = 90 + (270 + self.angle)
        self.angle = pygame.math.lerp(self.angle, angle, data.dt * ENEMY_ROT_SPEED)
        self.image = pygame.transform.rotate(self.static_image, self.angle)
        self.hitbox = self.rect.inflate(self.rect.w / 4, self.rect.h / 4)
        self.prev_dir = self.dir.copy()

        if self.hitbox.colliderect(data.player.hitbox):
            self.hit()

    def hit(self):
        data.player.damage(self.damage)
        self.destroy()

    def destroy(self):
        data.assets.play("small_explosion")
        data.game.explosion(self.rect.center, self.rect.w * 1.5)
        self.kill()

    def update_collisions(self):
        self.pushing = False
        self.push_speed = self.speed / 10
        if data.fps > 60:
            for ast in data.game.asteroids:
                if ast.rect.colliderect(self.rect):
                    self.pushing = True
                    self.push_dir = pygame.Vector2(self.rect.center) - ast.rect.center

            for bh in data.game.blackholes:
                if bh.collidecenter(self.rect.center):
                    self.pushing = True
                    self.push_dir = pygame.Vector2(self.rect.center) - bh.pos

    def weapon_collisions(self):
        for wb in data.game.enemy_damages:
            if wb.collidecenter(self.rect.center):
                self.destroy()
                return True
        for ph in data.game.purpleholes:
            if ph.collidesuck(self.rect.center):
                self.pushing = True
                self.push_dir = ph.pos - self.rect.center
                self.push_speed = PURPLEHOLE_SUCK_SPEED
                if not self.sucked:
                    self.sucked = True
                    data.assets.play("suck")
        if data.game.shield is not None:
            if data.game.shield.collidecenter(self.rect.center):
                self.pushing = True
                self.push_dir = -data.game.shield.pos + self.rect.center
                self.push_speed = SHIELD_PUSH_SPEED

    def get_behind(self, dist=3):
        return self.rect.center - (self.dir * self.rect.h * dist)


class EnemyPack:
    def __init__(self, center, type):
        self.enemy_type = type
        self.enemies: list[Enemy] | chunks.CameraRenderGroup = (
            chunks.CameraRenderGroup()
        )

        self.formation_func = getattr(self, f"formation_{self.enemy_type}")
        ps1, ps2 = ENEMIES[self.enemy_type][ENEMY_PACKSIZEID]
        ps1 = pygame.math.clamp(ps1 + data.game.extra_enemies, ps1, ps2)
        for _ in range(support.randrange((int(ps1), int(ps2)))):
            Enemy(center, self.enemy_type, self)

    def get_boss(self, ppos):
        closer = None
        closer_dist = float("inf")
        for enemy in self.enemies:
            dist = ppos.distance_to(enemy.rect.center)
            if dist < closer_dist:
                closer_dist = dist
                closer = enemy
        return closer

    def update(self):
        if len(self.enemies) <= 0:
            data.game.pack_destroyed()
            return

        ppos = pygame.Vector2(data.player.rect.center)
        boss: Enemy = self.get_boss(ppos)
        if boss is None:
            return
        boss.target_pos = ppos

        self.formation_func(boss)
        self.enemies.update()

    def formation_green(self, boss: Enemy):
        for enemy in self.enemies:
            if enemy is boss:
                continue
            enemy.target_pos = enemy.green_offset + boss.rect.center

    def formation_pink(self, boss: Enemy):
        prev = boss
        for i in range(len(self.enemies)):
            enemy: Enemy = self.enemies.sprites()[i]
            if enemy is boss:
                continue
            enemy.target_pos = prev.get_behind()
            prev = enemy

    def formation_yellow(self, boss: Enemy):
        if len(self.enemies) == 1:
            return
        points = support.lateral_points(
            boss.rect.center, boss.angle, len(self.enemies) - 1, boss.rect.w * 1.5
        )
        for i, enemy in enumerate(self.enemies):
            if enemy is boss:
                continue
            if i > len(points) - 1:
                i -= 1
            enemy.target_pos = points[i]

    def formation_blue(self, boss: Enemy):
        for enemy in self.enemies:
            if enemy is boss:
                continue
            enemy.target_pos = enemy.blue_offset + boss.rect.center

    def draw(self):
        self.enemies.draw()
