# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pygame-ce",
# ]
# ///
# pygbag .

# TODO: victory sound

import pygame
from consts import *
import data
import asyncio
import support
import main_menu
import game
import assets
import json
import os


class Main:
    def __init__(self):
        print("CONSOLE OPEN BECAUSE WINDOWS THINKS IT'S A VIRUS OTHERWISE")

        data.app = self
        data.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        self.clock = pygame.Clock()
        self.start_click = pygame.Vector2()
        self.music_vol = 0.5
        self.fx_vol = 1
        self.load_volumes()

        data.assets = assets.Assets()
        self.scene = 0
        data.main_menu = main_menu.MainMenu()
        data.game = game.Game()

        self.scenes: list[main_menu.MainMenu] = [data.main_menu, data.game]
        self.scenes[self.scene].enter()

        pygame.display.set_icon(data.assets.get_player())
        data.assets.music_play("game_music")
        data.assets.update_volumes()

    def load_volumes(self):
        if os.path.exists("volume.json"):
            with open("volume.json", "r") as file:
                obj = json.load(file)
                if isinstance(obj, dict):
                    if "music" in obj:
                        self.music_vol = obj["music"]
                    if "fx" in obj:
                        self.fx_vol = obj["fx"]

    def enter_menu(self):
        self.scene = 0
        data.assets.music_resume()
        self.scenes[self.scene].enter()

    def enter_game(self, difficulty="normal", mobile=False):
        self.scene = 1
        data.assets.music_resume()
        self.scenes[self.scene].enter(difficulty, mobile)

    def accessibility_mouse(self):
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

    async def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    support.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.start_click = pygame.Vector2(event.pos)
                self.scenes[self.scene].event(event)

            data.ticks = pygame.time.get_ticks()
            self.accessibility_mouse()
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
