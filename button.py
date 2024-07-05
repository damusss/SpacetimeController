import pygame
import support
import data
from consts import *


class Button:
    def __init__(
        self,
        text_img,
        center,
        color,
        hovercolor,
        can_select=False,
        selected=False,
        fixed_size=None,
        data=None,
        draw_outline=True,
    ):
        self.text_img = text_img
        self.color = color
        self.can_select = can_select
        self.hover_color = hovercolor
        self.data = data
        self.draw_outline = draw_outline
        if fixed_size is not None:
            self.rect = (
                pygame.Rect((0, 0), fixed_size).move_to(center=center).inflate(30, 30)
            )
        else:
            self.rect = self.text_img.get_rect(center=center).inflate(30, 30)
        self.selected = selected
        self.hovered = False
        self.clicked = False
        self.offset = 0

    def update(self) -> bool:
        mpos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()

        self.offset += data.dt * BUTTON_SPEED
        if self.offset >= BUTTON_SEGMENT * 2:
            self.offset = 0

        if self.rect.collidepoint(mpos):
            self.hovered = True
            if mouse[pygame.BUTTON_LEFT - 1]:
                if not self.clicked:
                    self.clicked = True
            else:
                if self.clicked:
                    self.clicked = False
                    if self.can_select:
                        self.selected = not self.selected
                    return True
        else:
            self.hovered = False
        return False

    def draw(self):
        data.screen.blit(self.text_img, self.text_img.get_rect(center=self.rect.center))
        if not self.draw_outline:
            return
        hover = self.hovered or self.selected
        color = self.hover_color if hover else self.color
        pygame.draw.circle(
            data.screen,
            color,
            (self.rect.left + BUTTON_R, self.rect.top + BUTTON_R),
            BUTTON_R,
            BUTTON_W if hover else BUTTON_WS,
            False,
            True,
            False,
            False,
        )
        pygame.draw.circle(
            data.screen,
            color,
            (self.rect.left + BUTTON_R, self.rect.bottom - BUTTON_R),
            BUTTON_R,
            BUTTON_W if hover else BUTTON_WS,
            False,
            False,
            True,
            False,
        )
        pygame.draw.circle(
            data.screen,
            color,
            (self.rect.right - BUTTON_R, self.rect.top + BUTTON_R),
            BUTTON_R,
            BUTTON_W if hover else BUTTON_WS,
            True,
            False,
            False,
            False,
        )
        pygame.draw.circle(
            data.screen,
            color,
            (self.rect.right - BUTTON_R, self.rect.bottom - BUTTON_R),
            BUTTON_R,
            BUTTON_W if hover else BUTTON_WS,
            False,
            False,
            False,
            True,
        )

        if not self.hovered and not self.selected:
            pygame.draw.line(
                data.screen,
                self.color,
                (self.rect.left + BUTTON_R, self.rect.top + BUTTON_WS / 2),
                (self.rect.right - BUTTON_R, self.rect.top + BUTTON_WS / 2),
                BUTTON_WS,
            )
            pygame.draw.line(
                data.screen,
                self.color,
                (self.rect.left + BUTTON_R, self.rect.bottom - BUTTON_WS / 2),
                (self.rect.right - BUTTON_R, self.rect.bottom - BUTTON_WS / 2),
                BUTTON_WS,
            )
            pygame.draw.line(
                data.screen,
                self.color,
                (self.rect.left + BUTTON_WS / 2, self.rect.top + BUTTON_R),
                (self.rect.left + BUTTON_WS / 2, self.rect.bottom - BUTTON_R),
                BUTTON_WS,
            )
            pygame.draw.line(
                data.screen,
                self.color,
                (self.rect.right - BUTTON_WS / 2, self.rect.top + BUTTON_R),
                (self.rect.right - BUTTON_WS / 2, self.rect.bottom - BUTTON_R),
                BUTTON_WS,
            )
            return

        x = self.rect.left + BUTTON_R + self.offset
        ox = self.rect.right - BUTTON_R - self.offset
        y_pos = [self.rect.top + BUTTON_W / 2, self.rect.bottom - BUTTON_W / 2]
        on = True
        if self.offset > BUTTON_SEGMENT:
            pygame.draw.line(
                data.screen,
                self.hover_color,
                (x - self.offset, y_pos[0]),
                (x - self.offset + (self.offset - BUTTON_SEGMENT), y_pos[0]),
                BUTTON_W,
            )
            pygame.draw.line(
                data.screen,
                self.hover_color,
                (ox + self.offset - (self.offset - BUTTON_SEGMENT), y_pos[1]),
                (ox + self.offset, y_pos[1]),
                BUTTON_W,
            )
        while True:
            if on:
                pygame.draw.line(
                    data.screen,
                    self.hover_color,
                    (x, y_pos[0]),
                    (min(self.rect.right - BUTTON_R, x + BUTTON_SEGMENT), y_pos[0]),
                    BUTTON_W,
                )
                pygame.draw.line(
                    data.screen,
                    self.hover_color,
                    (
                        max(
                            self.rect.left + BUTTON_R,
                            ox - BUTTON_SEGMENT,
                        ),
                        y_pos[1],
                    ),
                    (ox, y_pos[1]),
                    BUTTON_W,
                )
                on = False
            else:
                on = True
            x += BUTTON_SEGMENT
            ox -= BUTTON_SEGMENT
            if x >= self.rect.right - BUTTON_R:
                break

        y = self.rect.top + BUTTON_R + self.offset
        oy = self.rect.bottom - BUTTON_R - self.offset
        x_pos = [self.rect.left + BUTTON_W / 2, self.rect.right - BUTTON_W / 2]
        on = True
        if self.offset > BUTTON_SEGMENT:
            pygame.draw.line(
                data.screen,
                self.hover_color,
                (x_pos[1], y - self.offset),
                (x_pos[1], y - self.offset + (self.offset - BUTTON_SEGMENT)),
                BUTTON_W,
            )
            pygame.draw.line(
                data.screen,
                self.hover_color,
                (x_pos[0], oy + self.offset - (self.offset - BUTTON_SEGMENT)),
                (x_pos[0], oy + self.offset),
                BUTTON_W,
            )
        while True:
            if on:
                pygame.draw.line(
                    data.screen,
                    self.hover_color,
                    (x_pos[1], y),
                    (x_pos[1], min(self.rect.bottom - BUTTON_R, y + BUTTON_SEGMENT)),
                    BUTTON_W,
                )
                pygame.draw.line(
                    data.screen,
                    self.hover_color,
                    (x_pos[0], max(self.rect.top + BUTTON_R, oy - BUTTON_SEGMENT)),
                    (x_pos[0], oy),
                    BUTTON_W,
                )
                on = False
            else:
                on = True
            y += BUTTON_SEGMENT
            oy -= BUTTON_SEGMENT
            if y >= self.rect.bottom - BUTTON_R:
                break
