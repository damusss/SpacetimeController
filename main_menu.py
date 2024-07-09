import pygame
from consts import *
import support
import data
import random
import button
import os
import json


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)


class MainMenu:
    def __init__(self): ...

    def enter(self):
        self.title_font = data.assets.font(120)
        self.quit_font = data.assets.font(32)
        self.play_font = data.assets.font(65)
        self.other_font = data.assets.font(35)
        self.others_font = data.assets.font(24)
        self.time_font = data.assets.font(30)

        self.played = False
        self.completed = data.assets.get_completed()
        self.make_bg()
        self.make_btns()

        if not os.path.exists("data.json"):
            with open("data.json", "w") as file:
                json.dump({key: -1 for key in DIFFICULTIES.keys()}, file)

        with open("data.json", "r") as file:
            self.difficulty_data = json.load(file)
            if not isinstance(self.difficulty_data, dict):
                self.difficulty_data = {key: -1 for key in DIFFICULTIES.keys()}
            for diff in DIFFICULTIES.keys():
                if diff not in self.difficulty_data:
                    self.difficulty_data[diff] = -1

    def make_btns(self):
        self.title1 = self.title_font.render("SPACETIME", True, "white")
        self.title2 = self.title_font.render("CONTROLLER", True, "white")
        self.play_txt = self.play_font.render("PLAY", True, "white")
        self.quit_txt = self.quit_font.render("QUIT", True, "black")

        self.wh_size = WIDTH / 4
        self.play_static = pygame.transform.scale(
            data.assets.get_weapon("worm_holeB"), (self.wh_size, self.wh_size)
        )
        self.play_angle = 0

        normtxt = self.other_font.render("NORMAL", True, "white")
        extremetxt = self.other_font.render("EXTREME", True, "white")
        self.buttons = {
            "easy": button.Button(
                self.other_font.render("EASY", True, "white"),
                (WIDTH / 5, HEIGHT / 2 + HEIGHT / 6),
                BTN_COL,
                BTN_HOVER,
                True,
                fixed_size=normtxt.get_size(),
            ),
            "normal": button.Button(
                normtxt,
                (WIDTH / 5, HEIGHT / 2 + HEIGHT / 3.5),
                BTN_COL,
                BTN_HOVER,
                True,
                True,
            ),
            "hard": button.Button(
                self.other_font.render("HARD", True, "white"),
                (WIDTH / 2 + WIDTH / 3.5, HEIGHT / 4),
                BTN_COL,
                BTN_HOVER,
                True,
                fixed_size=extremetxt.get_size(),
            ),
            "extreme": button.Button(
                extremetxt,
                (WIDTH / 2 + WIDTH / 3.5, HEIGHT / 4 + HEIGHT / 8),
                BTN_COL,
                BTN_HOVER,
                True,
            ),
        }
        txt = self.others_font.render("MOBILE", True, "white")
        self.mobile_button = button.Button(
            txt,
            txt.get_rect(
                topleft=(UI_S * 25, self.title1.get_height() + UI_S * 5)
            ).center,
            BTN_COL,
            BTN_HOVER,
            True,
            False,
        )

    def make_bg(self):
        self.bg_objects = pygame.sprite.Group()

        for _ in range(MENU_STARS):
            image = data.assets.get_star(
                support.randrange(STAR_SIZE_RANGE), support.randcol(200)
            )
            Sprite(support.randpos(WINDOW_RECT), image, self.bg_objects)

        for _ in range(MENU_DUSTS):
            if random.randint(0, 100) < 50:
                color = DUST1_START.lerp(DUST1_END, random.uniform(0.0, 1.0))
            else:
                color = DUST2_START.lerp(DUST2_END, random.uniform(0.0, 1.0))
            color.a = 80
            size = random.randint(*DUST_SIZE_RANGE)
            Sprite(
                support.randpos(WINDOW_RECT),
                data.assets.get_dust(size, (*color,)),
                self.bg_objects,
            )

        bh_size = WIDTH / 3
        Sprite(
            (bh_size / 3, bh_size / 3),
            data.assets.get_blackhole(bh_size),
            self.bg_objects,
        )

        bh_size = WIDTH / 2
        Sprite(
            (WIDTH - bh_size / 7, HEIGHT - bh_size / 7),
            pygame.transform.scale(
                data.assets.get_weapon("purple_hole"), (bh_size, bh_size)
            ),
            self.bg_objects,
        )

        bh_size = WIDTH / 4.5
        Sprite(
            (WIDTH - bh_size / 12, bh_size / 12),
            pygame.transform.scale(
                data.assets.get_weapon("white_hole"), (bh_size, bh_size)
            ),
            self.bg_objects,
        )
        self.quit_size = bh_size

    def event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            support.quit()

    def play(self):
        diff = "normal"
        for d, btn in self.buttons.items():
            if btn.selected:
                diff = d
                break
        data.app.enter_game(diff, self.mobile_button.selected)

    def update(self):
        mouse = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        if CENTER.distance_to(mpos) <= self.wh_size / 2:
            self.play_angle += data.dt * MENU_PLAY_SPEED
            if mouse[pygame.BUTTON_LEFT - 1]:
                if not self.played:
                    data.assets.play("button_click")
                    self.played = True
                self.play()

        if (
            pygame.Vector2(WIDTH, 0).distance_to(mpos) <= self.quit_size / 2
            and mouse[pygame.BUTTON_LEFT - 1]
        ):
            if not self.played:
                data.assets.play("button_click")
                self.played = True
            support.quit()

        for btn in self.buttons.values():
            if btn.update():
                for ob in self.buttons.values():
                    if ob is not btn:
                        ob.selected = False
        self.mobile_button.update()

    def draw(self):
        self.bg_objects.draw(data.screen)

        img = pygame.transform.rotate(self.play_static, self.play_angle)
        data.screen.blit(img, img.get_rect(center=CENTER))
        data.screen.blit(self.play_txt, self.play_txt.get_rect(center=CENTER))
        data.screen.blit(self.title1, (UI_S * 10, 0))
        data.screen.blit(
            self.title2,
            self.title2.get_rect(bottomright=(WIDTH - UI_S * 10, HEIGHT + UI_S * 5)),
        )
        data.screen.blit(
            self.quit_txt, self.quit_txt.get_rect(topright=(WIDTH - UI_S * 2, -UI_S))
        )

        p = 0
        for diff, btn in self.buttons.items():
            btn.draw()
            best = self.difficulty_data[diff]
            if best != -1:
                if btn.selected:
                    time_txt = self.time_font.render(
                        f"BEST TIME: {int((best)/1000)} S", True, "white"
                    )
                    data.screen.blit(
                        time_txt,
                        time_txt.get_rect(
                            midtop=(WIDTH / 2, HEIGHT / 2 + HEIGHT / 3.5)
                        ),
                    )
                data.screen.blit(
                    self.completed,
                    self.completed.get_rect(
                        center=(
                            btn.rect.topleft if p in [0, 2] else btn.rect.bottomright
                        )
                    ),
                )
                if btn.color != MENU_COMPLETED_COL:
                    btn.color = MENU_COMPLETED_COL
                    btn.hover_color = MENU_COMPLETED_HOVER
            else:
                if btn.color != BTN_COL:
                    btn.color = BTN_COL
                    btn.hover_color = BTN_HOVER
            p += 1
        self.mobile_button.draw()
