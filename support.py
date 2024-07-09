import pygame
import sys
import random
import math
from consts import *


def quit():
    if sys.platform in ("emscripten", "wasi"):
        return
    pygame.quit()
    sys.exit()


def randcol(min_value=0):
    return (
        random.randint(min_value, 255),
        random.randint(min_value, 255),
        random.randint(min_value, 255),
    )


def asteroid_points(
    npts: int = 16, radius: float | int = 100, radius_diff: float = 0.1
) -> list[tuple[int, int]]:
    pts = []
    min_rad = radius * (1 - radius_diff)

    for i in range(npts):
        angle = math.tau * (i / npts)
        rad = min_rad + random.random() * radius_diff * radius
        pts.append((int(math.sin(angle) * rad), int(math.cos(angle) * rad)))

    return pts


def randrange(range):
    return random.randint(*[int(v) for v in range])


def randpos(rect):
    return random.randint(int(rect.left), int(rect.right)), random.randint(
        int(rect.top), int(rect.bottom)
    )


def randsign():
    return random.choice([-1, 1])


def randvec(scale=1):
    vec = pygame.Vector2(random.random() * randsign(), random.random() * randsign())
    if vec.magnitude() != 0:
        vec.normalize_ip()
    return vec * scale


def alter_color(color, amount=10):
    return (
        pygame.math.clamp(color[0] + random.randint(-amount, amount), 0, 255),
        pygame.math.clamp(color[1] + random.randint(-amount, amount), 0, 255),
        pygame.math.clamp(color[2] + random.randint(-amount, amount), 0, 255),
    )


def project_map(pos, topleft):
    x, y = pos
    x, y = (
        ((x + UNIVERSE_INFLATED / 2) / UNIVERSE_INFLATED) * UI_MAP_SIZE,
        ((y + UNIVERSE_INFLATED / 2) / UNIVERSE_INFLATED) * UI_MAP_SIZE,
    )
    rx, ry = x + topleft[0], y + topleft[1]
    return pygame.math.clamp(rx, topleft[0], WIDTH), pygame.math.clamp(
        ry, topleft[1], HEIGHT
    )


def clamp_pos(pos, rect):
    return (
        pygame.math.clamp(pos[0], rect.left, rect.right),
        pygame.math.clamp(pos[1], rect.top, rect.bottom),
    )


def norm(vec: pygame.Vector2):
    if vec.magnitude() != 0:
        vec.normalize_ip()
    return vec


def lateral_points(pos, angle, n, dist):
    pos = pygame.Vector2(pos)
    angle = angle
    leftx = 0
    rightx = 0
    side = "right"
    points = []
    for _ in range(n):
        if side == "right":
            rightx += dist
            p = pygame.Vector2(rightx, 0)
            p.rotate_ip(angle)
            points.append(pos + p)
            side = "left"
        else:
            leftx -= dist
            p = pygame.Vector2(leftx, 0)
            p.rotate_ip(angle)
            points.append(pos + p)
            side = "right"
    return points


def volume_str(volume):
    if volume == 1:
        return "MAX"
    elif volume == 0:
        return "OFF"
    return str(round(volume, 1))
