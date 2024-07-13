import pygame
import random
import sys

sys.path.append(".")
from consts import *
import support
import assets

IW, IH = 960, 960 // 4

win = pygame.Window("Spacetime Controller itch.io Banner Maker", (IW, IH))
screen = win.get_surface()
surf = pygame.Surface(screen.size, pygame.SRCALPHA)
clock = pygame.Clock()

assets = assets.Assets()

if False:
    for _ in range(STARS_IN_CHUNK * 2):
        size = int(random.randint(*STAR_SIZE_RANGE) / 2)
        pygame.draw.circle(
            surf,
            support.randcol(200),
            support.randpos(screen.get_rect()),
            size,
        )

    for _ in range(5):
        size = support.randrange((IW / 2, IW / 1))
        pos = support.randpos(screen.get_rect())
        if random.randint(0, 100) < 50:
            color = DUST1_START.lerp(DUST1_END, random.uniform(0.0, 1.0))
        else:
            color = DUST2_START.lerp(DUST2_END, random.uniform(0.0, 1.0))
        color.a = 30
        dust = assets.get_dust(size, color, False)
        rect = dust.get_rect(center=pos)
        screen.blit(dust, rect)

    blackhole = assets.get_blackhole(IH)
    surf.blit(blackhole, blackhole.get_rect(topleft=(-IH / 2, -IH / 2)))

font = assets.font(120)
spacetime = font.render("SPACETIME", True, "white")
controller = font.render("CONTROLLER", True, "white")

surf.blit(spacetime, spacetime.get_rect(topleft=(0, -0)))
surf.blit(controller, controller.get_rect(bottomright=(IW - 0, IH + 20)))

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_s:
            pygame.image.save(surf, "share/generated_itchio_banner.png")
            print("saved")

    screen.blit(surf, (0, 0))
    win.flip()
    clock.tick(60)
