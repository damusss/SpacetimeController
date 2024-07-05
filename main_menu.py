import pygame
from consts import *
import support
import data
import random
import button


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)


class MainMenu:
    def __init__(self): ...

    def enter(self):
        self.make_bg()

        self.title_font = data.images.font(115)
        self.quit_font = data.images.font(32)
        self.play_font = data.images.font(65)
        self.other_font = data.images.font(35)

        self.title1 = self.title_font.render("SPACETIME", True, "white")
        self.title2 = self.title_font.render("CONTROLLER", True, "white")
        self.play_txt = self.play_font.render("PLAY", True, "white")
        self.quit_txt = self.quit_font.render("QUIT", True, "black")

        self.wh_size = WIDTH / 4
        self.play_static = pygame.transform.scale(
            data.images.get_weapon("worm_holeB"), (self.wh_size, self.wh_size)
        )
        self.play_angle = 0

        normtxt = self.other_font.render("NORMAL", True, "white")
        extremetxt = self.other_font.render("EXTREME", True, "white")
        self.buttons = [
            button.Button(
                self.other_font.render("EASY", True, "white"),
                (WIDTH / 5, HEIGHT / 2 + HEIGHT / 6),
                BTN_COLOR,
                BTN_HOVER,
                True,
                data="easy",
                fixed_size=normtxt.get_size(),
            ),
            button.Button(
                normtxt,
                (WIDTH / 5, HEIGHT / 2 + HEIGHT / 3.5),
                BTN_COLOR,
                BTN_HOVER,
                True,
                True,
                data="normal",
            ),
            button.Button(
                self.other_font.render("HARD", True, "white"),
                (WIDTH / 2 + WIDTH / 3.5, HEIGHT / 4),
                BTN_COLOR,
                BTN_HOVER,
                True,
                data="hard",
                fixed_size=extremetxt.get_size(),
            ),
            button.Button(
                extremetxt,
                (WIDTH / 2 + WIDTH / 3.5, HEIGHT / 4 + HEIGHT / 8),
                BTN_COLOR,
                BTN_HOVER,
                True,
                data="extreme",
            ),
        ]

    def make_bg(self):
        self.bg_objects = pygame.sprite.Group()

        for _ in range(MENU_STARS):
            image = data.images.get_star(
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
                data.images.get_dust(size, (*color,)),
                self.bg_objects,
            )

        bh_size = WIDTH / 3
        Sprite(
            (bh_size / 3, bh_size / 3),
            data.images.get_blackhole(bh_size),
            self.bg_objects,
        )

        bh_size = WIDTH / 2
        Sprite(
            (WIDTH - bh_size / 7, HEIGHT - bh_size / 7),
            pygame.transform.scale(
                data.images.get_weapon("purple_hole"), (bh_size, bh_size)
            ),
            self.bg_objects,
        )

        bh_size = WIDTH / 4.5
        Sprite(
            (WIDTH - bh_size / 12, bh_size / 12),
            pygame.transform.scale(
                data.images.get_weapon("white_hole"), (bh_size, bh_size)
            ),
            self.bg_objects,
        )
        self.quit_size = bh_size

    def event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            support.quit()

    def play(self):
        diff = "normal"
        for btn in self.buttons:
            if btn.selected:
                diff = btn.data
                break
        data.app.enter_game(diff)

    def update(self):
        mouse = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        if CENTER.distance_to(mpos) <= self.wh_size / 2:
            self.play_angle += data.dt * MENU_PLAY_SPEED
            if mouse[pygame.BUTTON_LEFT - 1]:
                self.play()

        if (
            pygame.Vector2(WIDTH, 0).distance_to(mpos) <= self.quit_size / 2
            and mouse[pygame.BUTTON_LEFT - 1]
        ):
            support.quit()

        for btn in self.buttons:
            if btn.update():
                for ob in self.buttons:
                    if ob is not btn:
                        ob.selected = False

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

        for btn in self.buttons:
            btn.draw()
