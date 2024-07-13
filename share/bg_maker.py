import pygame
import random
import sys

sys.path.append(".")
from consts import *
import support
import assets

win = pygame.Window("Spacetime Controller itch.io BG Maker", (WIDTH * 2, HEIGHT * 2))
WW, WH = win.size
screen = win.get_surface()
clock = pygame.Clock()

DUST1_START = pygame.Color(255, 150, 0, 255)
DUST1_END = pygame.Color(255, 0, 255, 255)
DUST2_START = pygame.Color(255, 50, 0, 255)
DUST2_END = pygame.Color(255, 20, 255, 255)

UNIT = 30

imgs = assets.Assets()
particle = imgs.dust_surf

surf = pygame.Surface(win.size)
surf.fill("black")

for _ in range(STARS_IN_CHUNK * 10):
    size = int(random.randint(*STAR_SIZE_RANGE) / 2)
    pygame.draw.circle(
        surf,
        support.randcol(200),
        (
            random.randint(size, WW - size),
            random.randint(size, WH - size),
        ),
        size,
    )

for _ in range(17):
    size = support.randrange((WW / 6, WW / 3))
    pos = support.randpos(screen.get_rect())
    if random.randint(0, 100) < 50:
        color = DUST1_START.lerp(DUST1_END, random.uniform(0.0, 1.0))
    else:
        color = DUST2_START.lerp(DUST2_END, random.uniform(0.0, 1.0))
    color.a = 50
    dust = imgs.get_dust(size, color, False)
    rect = dust.get_rect(center=pos)

    surf.blit(dust, rect)
    surf.blit(dust, rect.move(win.size[0], 0))
    surf.blit(dust, rect.move(0, win.size[1]))
    surf.blit(dust, rect.move(-win.size[0], 0))
    surf.blit(dust, rect.move(0, -win.size[1]))
    surf.blit(dust, rect.move(win.size[0], win.size[1]))
    surf.blit(dust, rect.move(win.size[0], -win.size[1]))
    surf.blit(dust, rect.move(-win.size[0], -win.size[1]))
    surf.blit(dust, rect.move(-win.size[0], win.size[1]))


while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_s:
            pygame.image.save(surf, "share/generated_itchio_bg.png")
            print("saved")

    screen.blit(pygame.transform.scale(surf, (WIDTH, HEIGHT)), (WIDTH / 2, HEIGHT / 2))
    win.flip()
    clock.tick(60)
