import pygame
import data
import support
import random
from consts import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, topleft, image, groups, center=None):
        super().__init__(groups)
        self.image = image
        if topleft is None:
            topleft = (
                center[0] - self.image.get_width() / 2,
                center[1] - self.image.get_height() / 2,
            )
        self.rect = pygame.FRect(topleft, self.image.get_size())


class Chunk:
    def __init__(self, topleft, str_pos):
        self.str_pos = str_pos
        self.chunk_pos = pygame.Vector2(topleft)
        self.rect = pygame.Rect(
            (topleft[0] * CHUNK_SIZE, topleft[1] * CHUNK_SIZE), (CHUNK_SIZE, CHUNK_SIZE)
        )
        self.stars = CameraRenderGroup()
        self.dusts = CameraRenderGroup()

        for _ in range(STARS_IN_CHUNK):
            pos = pygame.Vector2(
                random.randint(self.rect.left, self.rect.right),
                random.randint(self.rect.top, self.rect.bottom),
            )
            size = random.randint(*STAR_SIZE_RANGE)
            color = support.randcol(200)
            Sprite(pos, data.images.get_star(size, color), self.stars)

        clipped = self.rect.clip(UNIVERSE_RECT)
        if clipped.w <= CHUNK_SIZE // 100 or clipped.h <= CHUNK_SIZE // 100:
            for _ in range(DUSTS_IN_FAR_CHUNK):
                size = random.randint(*DUST_FAR_CHUNK_SIZE_RANGE)
                pos = pygame.Vector2(
                    random.randint(self.rect.left - size, self.rect.right),
                    random.randint(self.rect.top - size, self.rect.bottom),
                )
                if random.randint(0, 100) < 50:
                    color = DUST1_START.lerp(DUST1_END, random.uniform(0.0, 1.0))
                else:
                    color = DUST2_START.lerp(DUST2_END, random.uniform(0.0, 1.0))
                color.a = 80
                Sprite(pos, data.images.get_dust(size, (*color,)), self.dusts)
        else:
            if random.randint(0, 100) < (DUST_CHANCE if not WEB else DUST_CHANCE/3):
                size = random.randint(*DUST_SIZE_RANGE)
                pos = pygame.Vector2(
                    random.randint(self.rect.left - size, self.rect.right),
                    random.randint(self.rect.top - size, self.rect.bottom),
                )
                if random.randint(0, 100) < 50:
                    color = DUST1_START.lerp(DUST1_END, random.uniform(0.0, 1.0))
                else:
                    color = DUST2_START.lerp(DUST2_END, random.uniform(0.0, 1.0))
                color.a = 50
                Sprite(pos, data.images.get_dust(size, (*color,)), self.dusts)

    def update(self): ...

    def draw(self):
        self.stars.draw()
        self.dusts.draw()


class CameraRenderGroup(pygame.sprite.Group):
    def draw(self):
        data.screen.fblits(
            [
                (sprite.image, CENTER + sprite.rect.topleft - data.player.rect.center)
                for sprite in self.spritedict
            ]
        )


class ChunkManager:
    def __init__(self):
        self.chunks: dict[str, Chunk] = {}
        self.visible_chunks: list[Chunk] = []

    def update(self):
        self.visible_chunks = []

        needed_x = (WIDTH // CHUNK_SIZE) + 2
        needed_y = (HEIGHT // CHUNK_SIZE) + 2

        for xi in range(int(-needed_x // 2 - 1), int(needed_x // 2 + 2)):
            for yi in range(int(-needed_y // 2 - 1), int(needed_y // 2 + 2)):
                cx, cy = (
                    int(data.player.rect.centerx // CHUNK_SIZE + xi),
                    int(data.player.rect.centery // CHUNK_SIZE + yi),
                )
                str_pos = f"{cx};{cy}"
                if str_pos not in self.chunks:
                    new = Chunk((cx, cy), str_pos)
                    self.chunks[str_pos] = new
                    self.visible_chunks.append(new)
                else:
                    self.visible_chunks.append(self.chunks[str_pos])

        for chunk in self.visible_chunks:
            chunk.update()

    def draw(self):
        for chunk in self.visible_chunks:
            chunk.draw()
