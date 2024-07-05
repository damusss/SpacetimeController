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

        data.images = assets.ImageMaker()
        self.scene = 0
        data.main_menu = main_menu.MainMenu()
        data.game = game.Game()

        self.scenes: list[main_menu.MainMenu] = [data.main_menu, data.game]
        self.scenes[self.scene].enter()

    def enter_menu(self):
        self.scene = 0
        self.scenes[self.scene].enter()

    def enter_game(self, difficulty="normal"):
        self.scene = 1
        self.scenes[self.scene].enter(difficulty)

    async def run(self):
        while True:
            data.ticks = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    support.quit()
                self.scenes[self.scene].event(event)

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
