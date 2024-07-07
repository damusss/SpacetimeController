import pygame
import support
import data
import math
import weapon
import particle
import functools
from consts import *


class Player:
    def __init__(self):
        self.rect = pygame.FRect((0, 0), PLAYER_SIZE).move_to(center=(0, 0))
        self.dir = pygame.Vector2()
        self.push_dir = pygame.Vector2()
        self.prev_dir = self.dir.copy()
        self.speed = 0
        self.static_image = data.assets.get_player()
        self.image = self.static_image
        self.static_rect = self.rect.copy()
        self.angle = 0
        self.ret_speed = 0
        self.push_speed = 0
        self.pickup_fail_time = data.ticks - 9999
        self.resources = []
        self.health = PLAYER_HEALTH
        self.hitbox = self.rect.inflate(self.rect.w / 3, self.rect.h / 3)
        self.hovering_resources = False
        self.trail = particle.Trail(PLAYER_TRAIL_SPEED, PLAYER_TRAIL_COL)
        self.last_trail = data.ticks
        self.damage_time = -9999

    def damage(self, amount=1):
        self.health -= amount
        self.damage_time = data.ticks
        data.assets.play("player_damage")
        if self.health <= 0:
            self.health = 0
            data.game.gameover()

    def heal(self, amount=1):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

    def attack(self, kind):
        if kind != "worm_hole":
            pos = self.rect.center - (
                self.dir * WEAPONS["purple_hole"][WEAPON_SIZEID] / 3
            )
        else:
            pos = self.rect.center
        img = data.assets.get_weapon(kind, True)
        data.assets.play("suck")
        p = particle.GrowParticle(
            pos,
            2,
            img.get_width(),
            150,
            img,
            finish_func=functools.partial(self.finish_attack, kind, pos),
        )
        if kind == "worm_hole":
            data.game.wormhole = p

    def finish_attack(self, kind, pos):
        weapon.WEAPON_CLASSES[kind](pos)

    def get_follow_point(self):
        return self.rect.center - self.dir * (self.rect.h * 1.5)

    def update(self):
        self.update_directions()
        in_universe = UNIVERSE_RECT.contains(self.rect)
        self.collided_object = False

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        dir_angle = self.dir.angle_to(self.prev_dir)

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
            or mouse[pygame.BUTTON_LEFT - 1]
        ):
            self.speed += PLAYER_ACC * data.dt
            self.speed -= dir_angle * 4
        else:
            if self.speed > 0:
                self.speed -= PLAYER_FRICTION * data.dt
        if not in_universe:
            self.ret_speed += data.dt * PLAYER_ACC * 2
        else:
            self.ret_speed -= data.dt * PLAYER_ACC * 2

        self.resource_collisions()
        self.asteroid_collisions()
        self.blackhole_collisions()
        self.weapon_collisions()

        if not self.collided_object:
            self.push_speed -= PLAYER_ACC * 3 * data.dt

        self.update_position()

        self.image = pygame.transform.rotate(self.static_image, self.angle)
        self.static_rect = self.image.get_rect(center=CENTER)
        self.hitbox = self.rect.inflate(self.rect.w / 4, self.rect.h / 4)

        if not WEB:
            points = (
                self.rect.center
                - ((self.dir * self.rect.h).rotate(90) * 0.2)
                + (-self.dir * 12),
                self.rect.center
                - ((self.dir * self.rect.h).rotate(-90) * 0.2)
                + (-self.dir * 12),
            )
            self.trail.set_start(points)
            if (
                data.ticks - self.last_trail >= PLAYER_TRAIL_COOLDOWN
                and self.speed > 0
                and data.game.wormhole is None
            ):
                self.last_trail = data.ticks
                self.trail.add(points)
            if data.ticks - self.damage_time < 1000:
                self.trail.color = (255, 0, 50)
            else:
                self.trail.color = PLAYER_TRAIL_COL

    def update_directions(self):
        self.dir = pygame.Vector2(pygame.mouse.get_pos()) - CENTER
        self.ret_dir = -pygame.Vector2(self.rect.center)

        support.norm(self.dir)
        support.norm(self.ret_dir)

        prev_angle = math.degrees(math.atan2(-self.prev_dir.y, self.prev_dir.x)) - 90
        angle = math.degrees(math.atan2(-self.dir.y, self.dir.x)) - 90

        if (prev_angle < 0 and angle > 0 and self.angle < 0) or (
            prev_angle > 0 and angle < 0 and self.angle > 0
        ):
            self.angle = angle
        self.angle = pygame.math.lerp(self.angle, angle, data.dt * PLAYER_ROT_SPEED)

    def resource_collisions(self):
        self.hovering_resources = False
        mouse = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        hovered = []
        for res in data.game.resources:
            if res.can_destroy and res.parent.destroyed:
                if res.rect.colliderect(self.rect):
                    hovered.append(res)
                    self.hovering_resources = True
        if (mouse[pygame.BUTTON_RIGHT - 1] or keys[pygame.K_e]) or (
            data.game.mobile and data.game.ui.grab_button.selected
        ):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            for res in hovered:
                if len(self.resources) < PLAYER_MAX_RESOURCES:
                    res.can_destroy = False
                    self.resources.append(res)
                    data.assets.play("grab")
                    data.game.grabbed_one_resource = True
                else:
                    self.pickup_fail_time = pygame.time.get_ticks()
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            for res in self.resources:
                res.escape()
            self.resources = []

    def asteroid_collisions(self):
        for ast in data.game.asteroids:
            if ast.hitbox.colliderect(self.rect):
                if not ast.is_hit and self.speed >= ASTEROID_HIT_SPEED:
                    ast.hit()
                self.collided_object = True
                self.push_speed += PLAYER_ACC * 3 * data.dt
                self.push_dir = pygame.Vector2(self.rect.center) - ast.rect.center
                support.norm(self.push_dir)
                break

    def blackhole_collisions(self):
        for bh in data.game.blackholes:
            if bh.collidecenter(self.rect.center):
                self.collided_object = True
                self.push_speed += PLAYER_ACC * 3 * data.dt
                self.push_dir = pygame.Vector2(self.rect.center) - bh.pos
                support.norm(self.push_dir)
                break

    def weapon_collisions(self):
        for wb in data.game.weapon_bodies:
            if wb.collidecenter(self.rect.center):
                self.collided_object = True
                self.push_speed += PLAYER_ACC * 3 * data.dt
                self.push_dir = pygame.Vector2(self.rect.center) - wb.pos
                support.norm(self.push_dir)

    def update_position(self):
        if data.game.wormhole is not None:
            return

        self.speed = pygame.math.clamp(self.speed, 0, PLAYER_SPEED)
        self.ret_speed = pygame.math.clamp(self.ret_speed, 0, PLAYER_SPEED * 2)
        self.push_speed = pygame.math.clamp(self.push_speed, 0, PLAYER_SPEED)

        self.rect.topleft += (
            self.dir * self.speed * data.dt
            + self.ret_dir * self.ret_speed * data.dt
            + self.push_dir * self.push_speed * data.dt
        )
        self.prev_dir = self.dir.copy()

    def draw(self):
        data.screen.blit(self.image, self.static_rect)
        if not WEB:
            self.trail.draw()
