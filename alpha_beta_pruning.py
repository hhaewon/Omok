import random
import multiprocessing

import pygame
from pygame.locals import *

from Rule import Rule
from common import Stone, GRID_NUM, GRID_SIZE, BLACK, BG_COLOR, WINDOW_SIZE


class AlphaBetaPruning:
    def __init__(self, depth, maximizing_player):
        self.depth = depth
        self.maximizing_player = maximizing_player
        self.best_move = None

    def alpha_beta_search(self, board):
        self.best_move = None
        if self.maximizing_player:
            value = float('-inf')
            legal_moves = board.generate_legal_moves()

            # 병렬 처리를 위한 프로세스 풀 생성
            pool = multiprocessing.Pool()

            results = pool.map(self.min_value,
                               [(board.make_copy(), move, self.depth, float('-inf'), float('inf')) for move in
                                legal_moves])

            pool.close()
            pool.join()

            for move, result in zip(legal_moves, results):
                if result > value:
                    value = result
                    self.best_move = move
        else:
            value = float('inf')
            legal_moves = board.generate_legal_moves()

            # 병렬 처리를 위한 프로세스 풀 생성
            pool = multiprocessing.Pool()

            results = pool.map(self.max_value,
                               [(board.make_copy(), move, self.depth, float('-inf'), float('inf')) for move in
                                legal_moves])

            pool.close()
            pool.join()

            for move, result in zip(legal_moves, results):
                if result < value:
                    value = result
                    self.best_move = move
        return self.best_move

    def max_value(self, args):
        board, move, depth, alpha, beta = args
        if depth == 0 or board.is_game_over:
            return AlphaBetaPruning.evaluate(board)
        value = float('-inf')
        board.make_move(move)
        legal_moves = board.generate_legal_moves()
        for next_move in legal_moves:
            value = max(value, self.min_value((board.make_copy(), next_move, depth - 1, alpha, beta)))
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

    def min_value(self, args):
        board, move, depth, alpha, beta = args
        if depth == 0 or board.is_game_over:
            return AlphaBetaPruning.evaluate(board)
        value = float('inf')
        board.make_move(move)
        legal_moves = board.generate_legal_moves()
        for next_move in legal_moves:
            value = min(value, self.max_value((board.make_copy(), next_move, depth - 1, alpha, beta)))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    @staticmethod
    def evaluate(board):
        dir_x = [-1, 1, -1, 1, 0, 0, 1, -1]
        dir_y = [0, 0, -1, 1, -1, 1, -1, 1]
        ai_weight = 0
        player_weight = 0

        for x in range(15):
            for y in range(15):
                if board[y][x] == Stone.EMPTY:
                    continue

                cur_stone = board[y][x]

                for k in range(0, 8, 2):
                    if board.rule.is_fit_five(x, y, k):
                        continue

                    nx, ny = x, y
                    stone_cnt = 1
                    flag = False
                    is_one_space = False

                    is_one_side_block = False

                    if k != 0 and (x == 0 or y == 0 or x == 14 or y == 14):
                        is_one_side_block = True

                    for i in range(4):
                        nx += dir_x[k]
                        ny += dir_y[k]

                        if Rule.is_invalid(nx, ny):
                            break

                        if board[ny][nx] == Stone.EMPTY and is_one_space:
                            break
                        if board[ny][nx] == cur_stone:
                            stone_cnt += 1
                            if flag:
                                is_one_space = True
                                flag = False
                            if nx == 0 or ny == 0 or nx == 14 or ny == 14:
                                is_one_side_block = True
                        elif board[ny][nx] == Stone.EMPTY and not flag:
                            flag = True
                        else:
                            if not flag:
                                is_one_side_block = True
                            break

                    nx, ny = x, y
                    flag = False

                    for i in range(4):
                        nx += dir_x[k + 1]
                        ny += dir_y[k + 1]

                        if Rule.is_invalid(nx, ny):
                            break

                        if board[ny][nx] == Stone.EMPTY and is_one_space:
                            break

                        if board[ny][nx] == cur_stone:
                            stone_cnt += 1
                            if flag:
                                is_one_space = True
                                flag = False
                            if nx == 0 or ny == 0 or nx == 14 or ny == 14:
                                is_one_side_block = True
                        elif board[ny][nx] == Stone.EMPTY and not flag:
                            flag = True
                        else:
                            if not flag:
                                is_one_side_block = True
                            break

                    weight_sum = 0

                    if stone_cnt == 1:
                        if is_one_side_block and not is_one_space:
                            weight_sum += 5
                        elif not is_one_side_block and not is_one_space:
                            weight_sum += 10
                    elif stone_cnt == 2:
                        if is_one_side_block and not is_one_space:
                            weight_sum += 30
                        elif is_one_side_block and is_one_space:
                            weight_sum += 15
                        elif not is_one_side_block and not is_one_space:
                            weight_sum += 40
                        else:
                            weight_sum += 30
                    elif stone_cnt == 3:
                        if is_one_side_block and not is_one_space:
                            weight_sum += 60
                        elif is_one_side_block and is_one_space:
                            weight_sum += 120
                        elif not is_one_side_block and not is_one_space:
                            weight_sum += 400
                        else:
                            weight_sum += 360
                    elif stone_cnt == 4:
                        if is_one_side_block and not is_one_space:
                            weight_sum += 200
                        elif is_one_side_block and is_one_space:
                            weight_sum += 190
                        elif not is_one_side_block and not is_one_space:
                            weight_sum += 1500
                        else:
                            weight_sum += 660
                    elif stone_cnt == 5 or stone_cnt == 6:
                        weight_sum += 2000

                    if cur_stone == Stone.BLACK:
                        player_weight += weight_sum
                    else:
                        ai_weight += weight_sum
        return ai_weight - player_weight


# 게임보드 클래스
class GameBoard:
    def __init__(self, surface, alpha_beta_pruning: AlphaBetaPruning):
        self.board = [[Stone.EMPTY for _ in range(GRID_NUM)] for _ in range(GRID_NUM)]
        self.rule = Rule(self.board)
        self.alpha_beta_pruning = alpha_beta_pruning
        self.surface = surface
        self.id = 1
        self.is_game_over = False
        self.current_player = Stone.BLACK
        self.coords = []
        self.images = {}
        self.all_coords = [
            self.get_coord(x, y)
            for x in range(GRID_NUM)
            for y in range(GRID_NUM)
        ]
        self.font = pygame.font.Font("NotoSans-Regular.ttf", 20)
        self.winner_stone = Stone.EMPTY
        self.aiX = None
        self.aiY = None

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

    def player_append_stone(self, position):
        coord = self.get_coord_contain_position(position)
        x, y = self.get_point(coord)
        self.coords.append(coord)
        self.board[y][x] = self.current_player
        self.id += 1
        if self.check_game_over(coord, self.current_player):
            self.is_game_over = True
            self.winner_stone = Stone.BLACK
        self.current_player = Stone.WHITE

    def ai_append_stone(self):
        x, y = self.alpha_beta_pruning.alpha_beta_search(self)
        coord = self.get_coord(x, y)
        self.coords.append(coord)
        self.board[y][x] = Stone.WHITE
        self.id += 1
        if self.check_game_over(coord, self.current_player):
            self.is_game_over = True
            self.winner_stone = Stone.WHITE
        self.current_player = Stone.BLACK

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

    def is_position_invalid(self, position):
        coord = self.get_coord_contain_position(position)
        if not coord:
            return True
        else:
            return False

    def is_position_empty(self, position):
        position = self.get_coord_contain_position(position)
        x, y = GameBoard.get_point(position)
        return self.board[y][x] == Stone.EMPTY

    def is_board_full(self):
        return self.id > GRID_NUM * GRID_NUM

    def check_game_over(self, position, stone):
        x, y = self.get_point(self.get_coord_contain_position(position))
        return self.is_board_full() or self.rule.is_game_over(x, y, stone)

    def make_text(self, text, left, top):
        surf = self.font.render(text, False, BLACK, BG_COLOR)
        rect = surf.get_rect()
        rect.center = (left, top)
        self.surface.blit(surf, rect)

    def show_winner_msg(self):
        stone = self.winner_stone
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

    def make_move(self, move):
        x, y = move
        if not Rule.is_invalid(x, y):
            self.board[y][x] = self.current_player
            self.current_player = Stone.BLACK if self.current_player == Stone.WHITE else Stone.WHITE  # 플레이어 교체
            return True
        else:
            return False

    def is_valid_move(self, x, y):
        return not Rule.is_invalid(x, y) and self.board[y][x] == Stone.EMPTY

    def generate_legal_moves(self):
        legal_moves = []
        for x in range(GRID_NUM):
            for y in range(GRID_NUM):
                if self.is_valid_move(x, y):
                    legal_moves.append((x, y))
        random.shuffle(legal_moves)  # 가능한 움직임을 무작위로 섞음
        return legal_moves

    def make_copy(self):
        copied_board = GameBoard(self.surface, self.alpha_beta_pruning)
        copied_board.board = [row[:] for row in self.board]
        copied_board.current_player = self.current_player
        return copied_board


def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Omok game")
    surface.fill(BG_COLOR)

    fps = 60
    fps_clock = pygame.time.Clock()

    alpha_beta = AlphaBetaPruning(depth=4, maximizing_player=True)
    game_board = GameBoard(surface, alpha_beta)
    is_running = True

    while is_running:
        for event in pygame.event.get():
            if event.type == QUIT:
                is_running = False
            elif event.type == MOUSEBUTTONUP:
                if not game_board.is_position_invalid(event.pos) and game_board.is_position_empty(
                        event.pos
                ):
                    game_board.player_append_stone(event.pos)
                    game_board.ai_append_stone()

        game_board.draw_stones()
        pygame.display.update()
        fps_clock.tick(fps)

        if game_board.is_game_over:
            game_board.show_winner_msg()
            is_running = False


if __name__ == '__main__':
    main()
