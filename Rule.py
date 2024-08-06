from common import *


class Rule(object):
    def __init__(self, board):
        self.board = board

    @staticmethod
    def is_invalid(x, y):
        return x < 0 or x >= GRID_NUM or y < 0 or y >= GRID_NUM

    def four_way_search(self, x, y, stone):
        four_dir_x = [-1, 0, 1, 1]
        four_dir_y = [1, 1, 1, 0]
        for i in range(4):
            nx, ny = x, y
            s = True

            for k in range(4):
                nx += four_dir_x[i]
                ny += four_dir_y[i]

                if Rule.is_invalid(nx, ny) or self.board[ny][nx] != stone:
                    s = False

            if s:
                return True
        return False

    def is_fit_five(self, x, y, k):
        nx, ny = x, y
        cur_stone: Stone = self.board[y][x]
        dir_x = [-1, 1, -1, 1, 0, 0, 1, -1]
        dir_y = [0, 0, -1, 1, -1, 1, -1, 1]

        cnt = 0
        for i in range(4):
            nx += dir_x[k]
            ny += dir_y[k]

            if (
                Rule.is_invalid(nx, ny)
                or self.board[ny][nx] == cur_stone.get_toggle_color()
            ):
                break
            else:
                cnt += 1

        nx = x
        ny = y
        for i in range(4):
            nx += dir_x[k + 1]
            ny += dir_y[k + 1]

            if (
                Rule.is_invalid(nx, ny)
                or self.board[ny][nx] == cur_stone.get_toggle_color()
            ):
                break
            else:
                cnt += 1

        return cnt >= 4

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
