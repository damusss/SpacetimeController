import pygame
import data
import support
import button
from consts import *


class Pause:
    def __init__(self):
        self.pause_time = 0
        self.overlay = data.assets.get_overlay().copy()
        self.overlay.set_alpha(UI_OVERLAY_ALPHA)

        self.title_font = data.assets.font(100)
        self.btn_font = data.assets.font(35)

        self.title_txt = self.title_font.render("PAUSED", True, "white")
        self.resume_txt = self.btn_font.render("RESUME", True, "white")
        self.menu_txt = self.btn_font.render("MENU", True, "white")
        self.quit_txt = self.btn_font.render("QUIT", True, "white")
        self.restart_txt = self.btn_font.render("RESTART", True, "white")

        self.title_rect = self.title_txt.get_rect(midtop=(WIDTH / 2, HEIGHT / 8))
        self.resume_btn = button.Button(
            self.resume_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 7),
            BTN_COL,
            BTN_HOVER,
            fixed_size=self.restart_txt.get_size(),
        )
        self.menu_btn = button.Button(
            self.menu_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 4),
            BTN_COL,
            BTN_HOVER,
            fixed_size=self.restart_txt.get_size(),
        )
        self.restart_btn = button.Button(
            self.restart_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 2.79),
            BTN_COL,
            BTN_HOVER,
            fixed_size=self.restart_txt.get_size(),
        )
        self.quit_btn = button.Button(
            self.quit_txt,
            (WIDTH / 2, self.title_rect.bottom + HEIGHT / 1.7),
            BTN_COL,
            BTN_HOVER,
            fixed_size=self.restart_txt.get_size(),
        )

        self.leftx, self.y = (WIDTH / 6, self.menu_btn.rect.bottom)
        self.rightx = WIDTH - WIDTH / 6
        plus = self.btn_font.render("+", True, "white")
        minus = self.btn_font.render("-", True, "white")
        fixedsize = (plus.get_height() / 2, plus.get_height() / 2)

        self.left_plus = button.Button(
            plus,
            (self.leftx, self.y - UI_PAUSE_INCREASE),
            BTN_COL,
            BTN_HOVER,
            fixed_size=fixedsize,
            animate=False,
        )
        self.left_minus = button.Button(
            minus,
            (self.leftx, self.y + UI_PAUSE_INCREASE),
            BTN_COL,
            BTN_HOVER,
            fixed_size=fixedsize,
            animate=False,
        )
        self.right_plus = button.Button(
            plus,
            (self.rightx, self.y - UI_PAUSE_INCREASE),
            BTN_COL,
            BTN_HOVER,
            fixed_size=fixedsize,
            animate=False,
        )
        self.right_minus = button.Button(
            minus,
            (self.rightx, self.y + UI_PAUSE_INCREASE),
            BTN_COL,
            BTN_HOVER,
            fixed_size=fixedsize,
            animate=False,
        )

        self.buttons = [
            self.left_plus,
            self.left_minus,
            self.right_plus,
            self.right_minus,
        ]

    def pause(self):
        if data.game.finished:
            return
        data.game.paused = True
        self.pause_time = data.ticks
        data.assets.music_pause()

    def unpause(self):
        data.game.paused = False
        pause_time = data.ticks - self.pause_time
        data.game.last_pack += pause_time
        data.game.start_time += pause_time
        data.assets.music_resume()

    def update(self):
        if self.resume_btn.update():
            data.game.pause.unpause()
        if self.menu_btn.update():
            data.app.enter_menu()
        if self.quit_btn.update():
            support.quit()
        if self.restart_btn.update():
            data.game.restart()

        if self.left_plus.update():
            data.app.change_volume(1, "music_vol")
        if self.left_minus.update():
            data.app.change_volume(-1, "music_vol")
        if self.right_plus.update():
            data.app.change_volume(1, "fx_vol")
        if self.right_minus.update():
            data.app.change_volume(-1, "fx_vol")

    def draw(self):
        data.screen.blit(self.overlay, (0, 0))
        data.screen.blit(self.title_txt, self.title_rect)
        self.resume_btn.draw()
        self.restart_btn.draw()
        self.menu_btn.draw()
        self.quit_btn.draw()

        txt = self.btn_font.render(
            f"MUSIC: {support.volume_str(data.app.music_vol)}", True, "white"
        )
        data.screen.blit(txt, txt.get_rect(center=(self.leftx, self.y)))

        txt = self.btn_font.render(
            f"SOUNDS: {support.volume_str(data.app.fx_vol)}", True, "white"
        )
        data.screen.blit(txt, txt.get_rect(center=(self.rightx, self.y)))

        for btn in self.buttons:
            btn.draw()
