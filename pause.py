import pygame
import data
import support
import button
from consts import *


class Pause:
    def __init__(self):
        self.pause_time = 0
        self.overlay = data.images.get_overlay().copy()
        self.overlay.set_alpha(UI_OVERLAY_ALPHA)

        self.title_font = data.images.font(100)
        self.btn_font = data.images.font(35)

        self.title_txt = self.title_font.render("PAUSED", True, "white")
        self.resume_txt = self.btn_font.render("RESUME", True, "white")
        self.menu_txt = self.btn_font.render("MENU", True, "white")
        self.quit_txt = self.btn_font.render("QUIT", True, "white")

        self.title_rect = self.title_txt.get_rect(midtop=(WIDTH / 2, HEIGHT / 6))
        self.resume_btn = button.Button(
            self.resume_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 7),
            BTN_COLOR,
            BTN_HOVER,
        )
        self.menu_btn = button.Button(
            self.menu_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 4),
            BTN_COLOR,
            BTN_HOVER,
            fixed_size=self.resume_txt.get_size(),
        )
        self.quit_btn = button.Button(
            self.quit_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 2),
            BTN_COLOR,
            BTN_HOVER,
            fixed_size=self.resume_txt.get_size(),
        )

    def pause(self):
        if data.game.finished:
            return
        data.game.paused = True
        self.pause_time = data.ticks

    def unpause(self):
        data.game.paused = False
        data.game.last_pack += data.ticks - self.pause_time

    def update(self):
        if self.resume_btn.update():
            data.game.pause.unpause()
        if self.menu_btn.update():
            data.app.enter_menu()
        if self.quit_btn.update():
            support.quit()

    def draw(self):
        data.screen.blit(self.overlay, (0, 0))
        data.screen.blit(self.title_txt, self.title_rect)
        self.resume_btn.draw()
        self.menu_btn.draw()
        self.quit_btn.draw()
