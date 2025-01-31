import typing
import pygame

if typing.TYPE_CHECKING:
    from .main import Main
    from .main_menu import MainMenu
    from .game import Game
    from .assets import Assets
    from .player import Player

app: "Main" = None
screen: pygame.Surface = None
main_menu: "MainMenu" = None
game: "Game" = None
dt: float = 0
assets: "Assets" = None
player: "Player" = None
ticks: int = 0
fps: float = 0
