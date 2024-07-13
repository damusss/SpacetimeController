import pygame
import random
import sys

sys.path.append(".")
from consts import *
import support
import assets

IW, IH = 630, 500

win = pygame.Window("Spacetime Controller itch.io Icon Maker", (IW, IH))
screen = win.get_surface()
clock = pygame.Clock()

assets = assets.Assets()

for _ in range(STARS_IN_CHUNK * 2):
    size = int(random.randint(*STAR_SIZE_RANGE) / 2)
    pygame.draw.circle(
        screen,
        support.randcol(200),
        support.randpos(screen.get_rect()),
        size,
    )

for _ in range(4):
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

blackhole = assets.get_weapon("purple_hole")
blackhole = pygame.transform.scale(blackhole, (IH, IH))
player = pygame.transform.scale_by(assets.get_player(), 1.5)

screen.blit(blackhole, blackhole.get_rect(center=(IW / 2, IH / 2)))
screen.blit(player, player.get_rect(center=(IW / 2, IH / 2)))

tyd = 18
twd = 10
pygame.draw.polygon(
    screen,
    PLAYER_TRAIL_COL,
    [
        (IW / 2 - twd, IH / 2 + tyd),
        (IW / 2 + twd, IH / 2 + tyd),
        (IW / 2, IH / 2 + 110),
    ],
)

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_s:
            pygame.image.save(screen, "share/generated_itchio_icon.png")
            print("saved")

    win.flip()
    clock.tick(60)
