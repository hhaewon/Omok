import random

import pygame

from Rule import Rule
from common import BG_COLOR, BLACK, WINDOW_SIZE, Stone, GRID_NUM, GRID_SIZE

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
        self.board[y][x] = self.turn
        self.id += 1
        if self.check_game_over(coord, self.turn):
            self.is_game_over = True
            self.winner_stone = Stone.BLACK
        self.turn = Stone.WHITE

    def ai_append_stone(self):
        if self.winner_stone == Stone.BLACK:
            return
        self.alpha_beta_pruning(0, float("-inf"), float("inf"))
        coord = self.get_coord(self.aiX, self.aiY)
        self.coords.append(coord)
        self.board[self.aiY][self.aiX] = Stone.WHITE
        self.id += 1
        if self.check_game_over(coord, self.turn):
            self.is_game_over = True
            self.winner_stone = Stone.WHITE
        self.turn = Stone.BLACK

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
        x, y = Omok.get_point(position)
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

    def alpha_beta_pruning(self, depth, alpha, beta):
        dir_x = [-1, 1, -1, 1, 0, 0, 1, -1]
        dir_y = [0, 0, -1, 1, -1, 1, -1, 1]

        max_depth = max(-self.id // 30 + 3, 1)
        if depth == max_depth:
            return self.evaluate()

        if depth % 2 == 0:
            v = float("-inf")
            pruning = False

            for x in range(15):
                for y in range(15):
                    cur_stone = self.board[y][x]
                    flag = False

                    if cur_stone == Stone.EMPTY:
                        for k in range(8):
                            nx = x + dir_x[k]
                            ny = y + dir_y[k]

                            if Rule.is_invalid(nx, ny):
                                continue
                            if self.board[ny][nx] != Stone.EMPTY:
                                flag = True
                                break

                        if flag:
                            self.board[y][x] = Stone.WHITE
                            temp = self.alpha_beta_pruning(depth + 1, alpha, beta)

                            if v < temp or (v == temp and random.choice([0, 1]) == 0):
                                v = temp
                                if depth == 0:
                                    self.aiX = x
                                    self.aiY = y
                            self.board[y][x] = Stone.EMPTY

                            alpha = max(alpha, v)

                            if beta <= alpha:
                                pruning = True
                                break
                    if pruning:
                        break
                if pruning:
                    break
            return v
        else:
            v = float("inf")
            pruning = False

            for x in range(15):
                for y in range(15):
                    curStone = self.board[y][x]
                    flag = False

                    if curStone == Stone.EMPTY:
                        for k in range(8):
                            nx = x + dir_x[k]
                            ny = y + dir_y[k]
                            if Rule.is_invalid(nx, ny):
                                continue
                            if self.board[ny][nx] != Stone.EMPTY:
                                flag = True
                                break
                        if flag:
                            self.board[y][x] = Stone.BLACK
                            v = min(v, self.alpha_beta_pruning(depth + 1, alpha, beta))
                            self.board[y][x] = Stone.EMPTY

                            beta = min(beta, v)

                            if beta <= alpha:
                                pruning = True
                                break
                    if pruning:
                        break
                if pruning:
                    break
            return v

    def evaluate(self):
        dir_x = [-1, 1, -1, 1, 0, 0, 1, -1]
        dir_y = [0, 0, -1, 1, -1, 1, -1, 1]
        ai_weight = 0
        player_weight = 0

        for x in range(15):
            for y in range(15):
                if self.board[y][x] == Stone.EMPTY:
                    continue

                cur_stone = self.board[y][x]

                for k in range(0, 8, 2):
                    if self.rule.is_fit_five(x, y, k):
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

                        if self.board[ny][nx] == Stone.EMPTY and is_one_space:
                            break
                        if self.board[ny][nx] == cur_stone:
                            stone_cnt += 1
                            if flag:
                                is_one_space = True
                                flag = False
                            if nx == 0 or ny == 0 or nx == 14 or ny == 14:
                                is_one_side_block = True
                        elif self.board[ny][nx] == Stone.EMPTY and not flag:
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

                        if self.board[ny][nx] == Stone.EMPTY and is_one_space:
                            break

                        if self.board[ny][nx] == cur_stone:
                            stone_cnt += 1
                            if flag:
                                is_one_space = True
                                flag = False
                            if nx == 0 or ny == 0 or nx == 14 or ny == 14:
                                is_one_side_block = True
                        elif self.board[ny][nx] == Stone.EMPTY and not flag:
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
                            weight_sum += 300
                        elif is_one_side_block and is_one_space:
                            weight_sum += 250
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


def main():
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Omok game")
    surface.fill(BG_COLOR)

    omok = Omok(surface)
    is_running = True

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if not omok.is_position_invalid(event.pos) and omok.is_position_empty(
                    event.pos
                ):
                    omok.player_append_stone(event.pos)
                    omok.ai_append_stone()
        omok.draw_stones()
        pygame.display.update()
        fps_clock.tick(fps)

        if omok.is_game_over:
            omok.show_winner_msg()
            is_running = False


if __name__ == "__main__":
    main()
