import pygame
import data
import support
import button
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
        self.info_font = data.images.font(10)
        self.help_font = data.images.font(16)
        self.resources_help = self.help_font.render("E / RMB", True, "white")
        self.fps_font = data.images.font(14)
        self.giga_font = data.images.font(150)
        self.subgiga_font = data.images.font(60)
        self.big_font = data.images.font(40)
        self.btn_font = data.images.font(35)
        self.help_font_s = data.images.font(14)

        self.inventory_images = {
            kind: data.images.get_asteroid(
                UI_RESOURCE_SIZE / 2,
                RESOURCES[kind][RESOURCE_COLID],
                RESOURCE_POINTS_RANGE,
            )
            for kind in RESOURCES.keys()
        }
        self.weapon_images = {
            kind: pygame.transform.scale(
                data.images.get_weapon(kind, True), (UI_WEAPON_SIZE, UI_WEAPON_SIZE)
            )
            for kind in WEAPONS.keys()
        }
        self.number_images = [
            self.help_font.render(f"{i+1}", True, "white") for i in range(len(WEAPONS))
        ]
        self.number_offset = self.number_images[0].get_width() * 1.5

        self.gameover_txt = self.giga_font.render("GAME OVER", True, UI_BAD_COL)
        self.gameover_subtitle = self.subgiga_font.render(
            "YOU EXPLODED", True, UI_BAD_COL
        )
        self.win_txt = self.giga_font.render("VICTORY", True, UI_OK_COL)
        self.win_subtitle = self.subgiga_font.render(
            "ALL RESOURCES COLLECTED", True, UI_OK_COL
        )
        self.difficulty_txt = self.big_font.render(
            f"MODE: {data.game.difficulty_name.upper()}", True, "white"
        )
        for txt in [
            self.gameover_txt,
            self.gameover_subtitle,
            self.win_subtitle,
            self.win_txt,
            self.difficulty_txt,
        ]:
            txt.set_alpha(0)
        self.overlay = data.images.get_overlay().copy()
        self.help_font_s.align = pygame.FONT_CENTER
        self.help_grab = self.help_font_s.render(
            "CRASH IN TO THE ASTEROIDS UNTIL THEY BREAK AND GRAB THE RESOURCES (1/2)\nTAB TO SKIP",
            True,
            "white",
        )
        self.help_collect = self.help_font_s.render(
            "DROP THE RESOURCES IN A BLACK HOLE TO COLLECT THEM (2/2)\nTAB TO SKIP",
            True,
            "white",
        )

        self.finish_alpha = 0
        self.overlay_alpha = 0

        self.restart_button = button.Button(
            self.btn_font.render("RESTART", True, "white"),
            (WIDTH / 2, HEIGHT / 2 + HEIGHT / 8),
            BTN_COLOR,
            BTN_HOVER,
        )
        self.menu_button = button.Button(
            self.btn_font.render("MENU", True, "white"),
            (WIDTH / 2, HEIGHT / 2 + HEIGHT / 4),
            BTN_COLOR,
            BTN_HOVER,
            fixed_size=self.restart_button.text_img.get_size(),
        )
        txt = data.images.font(30).render("| |", True, (160, 160, 160))
        self.pause_button = button.Button(
            txt,
            txt.get_rect(
                topright=(WIDTH - UI_RESOURCE_SIZE - UI_S * 6, UI_S * 2)
            ).center,
            (120, 120, 120),
            (200, 200, 200),
            draw_outline=False,
        )

    def update(self):
        if self.pause_button.update():
            if data.game.paused:
                data.game.pause.unpause()
            else:
                data.game.pause.pause()
        if data.game.finished:
            if self.restart_button.update():
                data.app.enter_game(data.game.difficulty_name)
            if self.menu_button.update():
                data.app.enter_menu()

    def draw_finish(self):
        self.finish_alpha += data.dt * UI_FINISH_SPEED
        self.overlay_alpha += data.dt * UI_FINISH_SPEED * 2
        if self.finish_alpha >= 255:
            self.finish_alpha = 255
        else:
            for txt in [
                self.gameover_txt,
                self.gameover_subtitle,
                self.win_subtitle,
                self.win_txt,
                self.difficulty_txt,
            ]:
                txt.set_alpha(self.finish_alpha)
        if self.overlay_alpha >= UI_OVERLAY_ALPHA:
            self.overlay_alpha = UI_OVERLAY_ALPHA
        else:
            self.overlay.set_alpha(self.overlay_alpha)
        data.screen.blit(self.overlay, (0, 0))
        self.draw_resources_amount()
        if data.game.finish_reason == "gameover":
            self.draw_gameover()
        else:
            self.draw_win()
        if data.ticks - data.game.finish_time >= 2500:
            self.restart_button.draw()
            self.menu_button.draw()

    def draw_gameover(self):
        self.draw_generic_finish(self.gameover_txt, self.gameover_subtitle)

    def draw_win(self):
        self.draw_generic_finish(self.win_txt, self.win_subtitle)

    def draw_generic_finish(self, title, subtitle):
        title_rect = title.get_rect(midtop=(WIDTH / 2, HEIGHT / 8))
        data.screen.blit(title, title_rect)
        subtitle_rect = subtitle.get_rect(midtop=(WIDTH / 2, title_rect.bottom))
        data.screen.blit(subtitle, subtitle_rect)
        data.screen.blit(
            self.difficulty_txt,
            self.difficulty_txt.get_rect(midbottom=(WIDTH / 2, HEIGHT)),
        )

    def draw(self):
        self.draw_resources()
        self.draw_map()
        self.draw_health()
        self.draw_weapons()
        self.draw_help()
        self.pause_button.draw()

        if WEB:
            txt = self.info_font.render(
                "GRAPHICS REDUCED FOR WEB", True, (120, 120, 120)
            )
            data.screen.blit(txt, txt.get_rect(bottomleft=(0, HEIGHT)))

    def draw_help(self):
        midbottom = (WIDTH / 2, HEIGHT - UI_S * 3)
        if not data.game.grabbed_one_resource:
            data.screen.blit(
                self.help_grab, self.help_grab.get_rect(midbottom=midbottom)
            )
            return
        if not data.game.collected_one_resource:
            data.screen.blit(
                self.help_collect, self.help_collect.get_rect(midbottom=midbottom)
            )

    def draw_weapons(self):
        y = UI_HEALTH_SIZE[1] + UI_S
        for i, kind in enumerate(list(WEAPONS.keys())):
            price = WEAPONS[kind][WEAPON_PRICEID]
            resource = WEAPONS[kind][WEAPON_RESOURCEID]
            current = data.game.inventory[resource]
            color = (
                UI_OK_COL
                if current >= price or resource in data.game.starter_inventory
                else UI_BAD_COL
            )
            weapon_img = self.weapon_images[kind]
            res_img = self.inventory_images[resource]
            number_img = self.number_images[i]
            text = (
                f"{current}/{price}"
                if resource not in data.game.starter_inventory
                else "FREE"
            )
            amount_img = self.resources_font.render(text, True, color)
            weapon_rect = weapon_img.get_rect(topleft=(0, y))
            number_rect = number_img.get_rect(midleft=(UI_S, weapon_rect.centery))
            data.screen.blit(number_img, number_rect)
            weapon_rect.midleft = (self.number_offset + UI_S, number_rect.centery)
            data.screen.blit(weapon_img, weapon_rect)
            amount_rect = amount_img.get_rect(
                midleft=(weapon_rect.right + UI_S, weapon_rect.centery)
            )
            data.screen.blit(amount_img, amount_rect)
            data.screen.blit(
                res_img,
                res_img.get_rect(
                    midleft=(amount_rect.right + UI_S, amount_rect.centery)
                ),
            )
            y += UI_S + weapon_rect.h

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
        self.draw_resources_amount()

        if data.player.hovering_resources:
            mpos = pygame.mouse.get_pos()
            data.screen.blit(
                self.resources_help,
                self.resources_help.get_rect(topleft=(mpos[0] + 10, mpos[1] + 10)),
            )

    def draw_resources_amount(self):
        txt = self.resources_font.render(
            f"RESOURCES {data.game.collected_resources}/{data.game.resources_amount}",
            True,
            "white",
        )
        data.screen.blit(txt, txt.get_rect(midtop=(WIDTH / 2, 0)))

    def draw_map(self):
        map_rect = pygame.Rect(0, 0, UI_MAP_SIZE, UI_MAP_SIZE).move_to(
            bottomright=(WIDTH, HEIGHT)
        )
        pygame.draw.rect(data.screen, (10, 10, 20), map_rect, 0, UI_BR, UI_BR, 0, 0, 0)

        res = data.game.resources.sprites()
        for i in range(
            min(len(data.game.resources), (UI_MAX_RESOURCES if data.fps > 60 else 50))
        ):
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
        txt = self.fps_font.render(f"{int(data.fps)} FPS", True, (120, 120, 120))
        data.screen.blit(txt, txt.get_rect(bottomright=map_rect.topright))
