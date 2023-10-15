import random
import os

from Rule import Rule
from alpha_beta_pruning import AlphaBetaPruning
from common import BG_COLOR, BLACK, WINDOW_SIZE, Stone, GRID_NUM, GRID_SIZE

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa: E402


fps = 60
fps_clock = pygame.time.Clock()


class GameLogic:
    def __init__(self) -> None:
        self.board = [[Stone.EMPTY for _ in range(GRID_NUM)] for _ in range(GRID_NUM)]
        self.rule = Rule(self.board)
        self.id = 1
        self.is_game_over = False
        self.current_player = Stone.BLACK
        self.coords = []
        self.all_coords = [
            (x * GRID_SIZE + 25, y * GRID_SIZE + 25)
            for x in range(GRID_NUM)
            for y in range(GRID_NUM)
        ]
        self.winner_stone = Stone.EMPTY

    def player_append_stone(self, coord):
        x, y = self.get_point(coord)
        self.coords.append(coord)
        self.board[y][x] = self.current_player
        self.id += 1
        if self.is_game_over:
            self.winner_stone = Stone.BLACK
        self.current_player = Stone.WHITE

    def append_stone(self, coord):
        x, y = self.get_point(coord)
        self.coords.append(coord)
        self.board[y][x] = self.current_player
        self.id += 1
        if self.check_game_over((x, y), self.current_player):
            self.is_game_over = True
            self.winner_stone = (
                Stone.BLACK if self.current_player == Stone.BLACK else Stone.WHITE
            )
        self.current_player = (
            Stone.BLACK if self.current_player == Stone.WHITE else Stone.WHITE
        )

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

    @staticmethod
    def get_coord(x, y):
        x = x * GRID_SIZE + 25
        y = y * GRID_SIZE + 25
        return x, y

    def is_board_full(self):
        return self.id > GRID_NUM * GRID_NUM

    def check_game_over(self, point, stone):
        x, y = point
        return self.is_board_full() or self.rule.is_game_over(x, y, stone)

    def make_move(self, move):
        x, y = move
        if not Rule.is_invalid(x, y):
            self.board[y][x] = self.current_player
            self.current_player = (
                Stone.BLACK if self.current_player == Stone.WHITE else Stone.WHITE
            )  # 플레이어 교체
            return True
        else:
            return False

    def is_valid_move(self, coord):
        x, y = self.get_point(coord)
        return not Rule.is_invalid(x, y) and self.board[y][x] == Stone.EMPTY

    def generate_legal_moves(self):
        legal_moves = []
        for x in range(GRID_NUM):
            for y in range(GRID_NUM):
                coord = self.get_coord(x, y)
                if self.is_valid_move(coord):
                    legal_moves.append((x, y))
        random.shuffle(legal_moves)  # 가능한 움직임을 무작위로 섞음
        return legal_moves

    def make_copy(self):
        copied_board = GameLogic()
        copied_board.board = [row[:] for row in self.board]
        copied_board.current_player = self.current_player
        return copied_board


class Graphics:
    def __init__(self) -> None:
        pygame.display.set_caption("Omok game")
        self.surface = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.font = pygame.font.Font("NotoSans-Regular.ttf", 20)
        black_img = pygame.image.load("image/black.png")
        white_img = pygame.image.load("image/white.png")
        self.images = {
            "board": pygame.image.load("image/board.png"),
            "black": pygame.transform.scale(black_img, (GRID_SIZE, GRID_SIZE)),
            "white": pygame.transform.scale(white_img, (GRID_SIZE, GRID_SIZE)),
        }
        self.surface.blit(self.images["board"], (0, 0))

    def draw_stone(self, coords: tuple[Stone, Stone] | None):
        """바둑돌 한쌍 그리기"""
        if coords:
            self.surface.blit(self.images["black"], coords[0])
            self.surface.blit(self.images["white"], coords[1])

    def make_text(self, text, left, top):
        surf = self.font.render(text, False, BLACK, BG_COLOR)
        rect = surf.get_rect()
        rect.center = (left, top)
        self.surface.blit(surf, rect)

    def show_winner_msg(self, game_logic: GameLogic):
        stone = game_logic.winner_stone
        messages = {
            stone.EMPTY: "",
            stone.BLACK: "Black Win!!",
            stone.WHITE: "White Win!!",
        }
        message = messages[stone]
        center_x = WINDOW_SIZE // 2

        for _ in range(3):
            self.make_text(message, center_x, 30)
            pygame.display.update()
            pygame.time.delay(200)
            self.make_text(message, center_x, 30)
            pygame.display.update()
            pygame.time.delay(200)
        self.make_text(message, center_x, 30)

    def draw_and_update(self, game_logic: GameLogic, alpha_beta: AlphaBetaPruning):
        coords = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                player_coord = game_logic.get_coord_contain_position(event.pos)
                if player_coord and game_logic.is_valid_move(player_coord):
                    game_logic.append_stone(player_coord)

                ai_point = alpha_beta.alpha_beta_search(game_logic)
                ai_coord = game_logic.get_coord(*ai_point)
                game_logic.append_stone(ai_coord)
                coords = (player_coord, ai_coord)

        self.draw_stone(coords)

        if game_logic.is_game_over:
            self.show_winner_msg(game_logic=game_logic)
            pygame.quit()

        pygame.display.update()
        fps_clock.tick(fps)


def main():
    pygame.init()
    alpha_beta = AlphaBetaPruning(depth=1, maximizing_player=True)
    game_logic = GameLogic()
    graphics = Graphics()

    while True:
        graphics.draw_and_update(game_logic=game_logic, alpha_beta=alpha_beta)


if __name__ == "__main__":
    main()
