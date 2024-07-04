import pygame
import data
import support
from consts import *


class UI:
    def __init__(self):
        self.resource_images = [
            data.images.get_asteroid(
                UI_RESOURCE_SIZE / 2, UI_RESOURCE_DEFAULT, RESOURCE_POINTS_RANGE
            )
            for _ in range(PLAYER_MAX_RESOURCES)
        ]
        self.resources_font = data.images.font(18)
        self.info_font = data.images.font(8)
        self.help_font = data.images.font(16)
        self.resources_help = self.help_font.render("E / RMB", True, "white")

    def update(self): ...

    def draw(self):
        self.draw_resources()
        self.draw_map()
        self.draw_health()
        
        if WEB:
            txt = self.info_font.render("GRAPHICS REDUCED FOR WEB", True, (120, 120, 120))
            data.screen.blit(txt, txt.get_rect(bottomleft=(0, HEIGHT)))

    def draw_health(self):
        rect = ((0, 0), UI_HEALTH_SIZE)
        br = UI_BR * 3, 0, 0, 0, UI_BR * 3
        pygame.draw.rect(data.screen, UI_HEALTH_BG, rect, 0, *br)
        pygame.draw.rect(
            data.screen,
            UI_HEALTH_FILL,
            (
                0,
                0,
                UI_HEALTH_SIZE[0] * data.player.health / PLAYER_HEALTH,
                UI_HEALTH_SIZE[1],
            ),
            0,
            *br,
        )
        pygame.draw.rect(data.screen, UI_HEALTH_OUTLINE, rect, 1, *br)

    def draw_resources(self):
        bg_rect = (
            WIDTH - UI_S * 2 - UI_RESOURCE_SIZE,
            0,
            UI_S * 2 + UI_RESOURCE_SIZE,
            UI_RESOURCE_SIZE * PLAYER_MAX_RESOURCES + UI_S * (PLAYER_MAX_RESOURCES + 1),
        )
        pygame.draw.rect(
            data.screen,
            UI_BG
            if data.ticks - data.player.pickup_fail_time >= 1000
            else (200, 0, 40),
            bg_rect,
            0,
            UI_BR,
            0,
            0,
            UI_BR,
            0,
        )
        pygame.draw.rect(data.screen, UI_OUTLINE, bg_rect, 1, UI_BR, 0, 0, UI_BR, 0)
        y = UI_S
        for i in range(PLAYER_MAX_RESOURCES):
            if len(data.player.resources) - 1 >= i:
                image = pygame.transform.scale(
                    data.player.resources[i].image, (UI_RESOURCE_SIZE, UI_RESOURCE_SIZE)
                )
            else:
                image = self.resource_images[i]
            data.screen.blit(image, (WIDTH - UI_S - UI_RESOURCE_SIZE, y))
            y += UI_S + UI_RESOURCE_SIZE
        txt = self.resources_font.render(
            f"RESOURCES {data.game.collected_resources}/{data.game.resources_amount}",
            True,
            "white",
        )
        data.screen.blit(txt, txt.get_rect(midtop=(WIDTH / 2, 0)))
        
        if data.player.hovering_resources:
            mpos = pygame.mouse.get_pos()
            data.screen.blit(self.resources_help, self.resources_help.get_rect(topleft=(mpos[0]+10, mpos[1]+10)))

    def draw_map(self):
        map_rect = pygame.Rect(0, 0, UI_MAP_SIZE, UI_MAP_SIZE).move_to(
            bottomright=(WIDTH, HEIGHT)
        )
        pygame.draw.rect(data.screen, (10, 10, 20), map_rect, 0, UI_BR, UI_BR, 0, 0, 0)

        res = data.game.resources.sprites()
        for i in range(min(len(data.game.resources), (UI_MAX_RESOURCES if data.fps > 60 else 50))):
            data.screen.set_at(
                (support.project_map(res[i].rect.center, map_rect.topleft)), "blue"
            )
        for bh in data.game.blackholes:
            pygame.draw.circle(
                data.screen, "yellow", support.project_map(bh.pos, map_rect.topleft), 3
            )
        if data.game.pack is not None:
            for enemy in data.game.pack.enemies:
                pygame.draw.circle(
                    data.screen,
                    "green",
                    support.project_map(enemy.rect.center, map_rect.topleft),
                    2,
                )
        pygame.draw.circle(
            data.screen,
            "red",
            support.project_map(data.player.rect.center, map_rect.topleft),
            2,
        )

        pygame.draw.rect(data.screen, UI_BG, map_rect, 1, UI_BR, UI_BR, 0, 0, 0)
