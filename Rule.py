from common import *

empty = 0
black_stone = 1
white_stone = 2
last_b_stone = 3
last_a_stont = 4
tie = 100


class Rule(object):
    def __init__(self, board):
        self.board = board

    @staticmethod
    def is_invalid(x, y):
        return x < 0 or x >= GRID_NUM or y < 0 or y >= GRID_NUM

    def is_game_over(self, x, y, stone):
        input_x, input_y = x, y
        list_dx = [-1, 1, -1, 1, 0, 0, 1, -1]
        list_dy = [0, 0, -1, 1, -1, 1, -1, 1]
        cnt = 1
        for i in range(0, len(list_dx), 2):
            cnt = 1
            for j in range(i, i + 2):
                dx, dy = list_dx[j], list_dy[j]
                x, y = input_x, input_y
                while True:
                    x, y = x + dx, y + dy
                    if Rule.is_invalid(x, y) or self.board[y][x] != stone:
                        break
                    else:
                        cnt += 1
            if cnt >= 5:
                return True
        return False
