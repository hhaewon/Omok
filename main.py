import pygame
from pygame.locals import *

from Rule import Rule
from common import *

fps = 60
fps_clock = pygame.time.Clock()


class Omok:
    def __init__(self, surface):
        self.board = [[Stone.EMPTY for _ in range(GRID_NUM)] for _ in range(GRID_NUM)]
        self.rule = Rule(self.board)
        self.surface = surface
        self.id = 1
        self.is_game_over = False
        self.turn = Stone.BLACK
        self.coords = []
        self.images = {}
        self.all_coords = [
            (x * GRID_SIZE + 25, y * GRID_SIZE + 25)
            for x in range(GRID_NUM)
            for y in range(GRID_NUM)
        ]
        self.font = pygame.font.Font("NotoSans-Regular.ttf", 20)

        self.set_images()
        self.surface.blit(self.images["board"], (0, 0))

    def set_images(self):
        """이미지 저장"""
        black_img = pygame.image.load("image/black.png")
        white_img = pygame.image.load("image/white.png")
        self.images = {
            "board": pygame.image.load("image/board.png"),
            "black": pygame.transform.scale(black_img, (GRID_SIZE, GRID_SIZE)),
            "white": pygame.transform.scale(white_img, (GRID_SIZE, GRID_SIZE)),
        }

    def draw_stone(self, stone, x, y):
        """바둑돌 하나 그리기"""
        match stone:
            case Stone.BLACK:
                self.surface.blit(self.images["black"], (x, y))
            case Stone.WHITE:
                self.surface.blit(self.images["white"], (x, y))

    def draw_stones(self):
        """바둑돌 여러개 그리기"""
        for i, (x, y) in enumerate(self.coords):
            match i % 2 + 1:
                case Stone.BLACK.value:
                    self.draw_stone(Stone.BLACK, x, y)
                case Stone.WHITE.value:
                    self.draw_stone(Stone.WHITE, x, y)

    def append_stone(self, position):
        coord = self.get_coord_contain_position(position)
        x, y = self.get_point(coord)
        self.coords.append(coord)
        self.board[y][x] = self.turn
        self.id += 1
        if self.check_game_over(coord, self.turn):
            self.is_game_over = True
        self.turn = Stone.BLACK if self.turn == Stone.WHITE else Stone.WHITE

    def get_coord_contain_position(self, position):
        for coord in self.all_coords:
            x, y = coord
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if rect.collidepoint(position):
                return coord
        return None

    @staticmethod
    def get_point(coord):
        x, y = coord
        x = (x - 25) // GRID_SIZE
        y = (y - 25) // GRID_SIZE
        return x, y

    def is_position_invalid(self, position):
        coord = self.get_coord_contain_position(position)
        if not coord:
            return True
        else:
            return False

    def is_position_empty(self, position):
        position = self.get_coord_contain_position(position)
        x, y = Omok.get_point(position)
        return self.board[y][x] == Stone.EMPTY

    def is_board_full(self):
        return self.id > GRID_NUM * GRID_NUM

    def check_game_over(self, position, stone):
        x, y = self.get_point(self.get_coord_contain_position(position))
        if self.is_board_full():
            self.show_winner_msg(stone)
            return True
        elif self.rule.is_game_over(x, y, stone):
            self.show_winner_msg(stone)
            return True
        return False

    def make_text(self, text, left, top):
        surf = self.font.render(text, False, BLACK, BG_COLOR)
        rect = surf.get_rect()
        rect.center = (left, top)
        self.surface.blit(surf, rect)

    def show_winner_msg(self, stone):
        msg = {
            stone.EMPTY: "",
            stone.BLACK: "Black Win!!",
            stone.WHITE: "White Win!!",
        }
        center_x = WINDOW_SIZE // 2

        for i in range(3):
            self.make_text(msg[stone], center_x, 30)
            pygame.display.update()
            pygame.time.delay(200)
            self.make_text(msg[stone], center_x, 30)
            pygame.display.update()
            pygame.time.delay(200)
        self.make_text(msg[stone], center_x, 30)


def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Omok game")
    surface.fill(BG_COLOR)

    omok = Omok(surface)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == MOUSEBUTTONUP:
                if not omok.is_position_invalid(event.pos) and omok.is_position_empty(
                    event.pos
                ):
                    omok.append_stone(event.pos)

        if omok.is_game_over:
            pygame.quit()

        omok.draw_stones()
        pygame.display.update()
        fps_clock.tick(fps)


if __name__ == "__main__":
    main()
