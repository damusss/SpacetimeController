# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pygame-ce",
# ]
# ///
# pygbag .

# TODO: sounds
# TODO: volume settings

import pygame
from consts import *
import data
import asyncio
import support
import main_menu
import game
import assets


class Main:
    def __init__(self):
        data.app = self
        data.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        self.clock = pygame.Clock()
        self.start_click = pygame.Vector2()
        self.music_vol = 0.5
        self.fx_vol = 1

        data.assets = assets.Assets()
        self.scene = 0
        data.main_menu = main_menu.MainMenu()
        data.game = game.Game()

        self.scenes: list[main_menu.MainMenu] = [data.main_menu, data.game]
        self.scenes[self.scene].enter()

        data.assets.music_play("game_music")
        data.assets.update_volumes()

    def enter_menu(self):
        self.scene = 0
        self.scenes[self.scene].enter()

    def enter_game(self, difficulty="normal", mobile=False):
        self.scene = 1
        self.scenes[self.scene].enter(difficulty, mobile)

    async def run(self):
        while True:
            data.ticks = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    support.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.start_click = pygame.Vector2(event.pos)
                self.scenes[self.scene].event(event)

            keys = pygame.key.get_pressed()
            mousedir = pygame.Vector2()
            if keys[pygame.K_i]:
                mousedir.y -= 1
            if keys[pygame.K_j]:
                mousedir.x -= 1
            if keys[pygame.K_l]:
                mousedir.x += 1
            if keys[pygame.K_k]:
                mousedir.y += 1
            if mousedir.magnitude() != 0:
                mousedir.normalize_ip()
                mousedir *= MOUSE_SPEED * data.dt
                newmpos = pygame.mouse.get_pos() + mousedir
                if WINDOW_RECT.collidepoint(newmpos):
                    pygame.mouse.set_pos(newmpos)

            data.screen.fill(0)
            self.scenes[self.scene].update()
            self.scenes[self.scene].draw()
            pygame.display.flip()
            data.fps = self.clock.get_fps()
            pygame.display.set_caption(TITLE + f" {int(data.fps)}")
            data.dt = self.clock.tick(FPS) / 1000

            await asyncio.sleep(0)


if __name__ == "__main__":
    app = Main()
    asyncio.run(app.run())
