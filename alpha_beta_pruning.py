from __future__ import annotations
from typing import TYPE_CHECKING
import threading

from Rule import Rule
from common import Stone, GRID_NUM

if TYPE_CHECKING:
    from main import GameLogic


class AlphaBetaPruning:
    def __init__(self, depth, maximizing_player):
        self.depth = depth
        self.maximizing_player = maximizing_player
        self.best_move = None

    def alpha_beta_search(self, game_logic: GameLogic):
        self.best_move = None
        alpha = float("-inf")
        beta = float("inf")
        if self.maximizing_player:
            value = float("-inf")
            legal_moves = game_logic.generate_legal_moves()
            results = []
            thread_list = []

            for move in legal_moves:
                thread = threading.Thread(
                    target=self.min_value,
                    args=(
                        game_logic.make_copy(),
                        move,
                        self.depth,
                        alpha,
                        beta,
                        results,
                    ),
                )
                thread_list.append(thread)
                thread.start()

            for thread in thread_list:
                thread.join()

            for move, result in results:
                if result > value:
                    value = result
                    self.best_move = move

        else:
            value = float("inf")
            legal_moves = game_logic.generate_legal_moves()
            results = []
            thread_list = []

            for move in legal_moves:
                thread = threading.Thread(
                    target=self.max_value,
                    args=(
                        game_logic.make_copy(),
                        move,
                        self.depth,
                        alpha,
                        beta,
                        results,
                    ),
                )
                thread_list.append(thread)
                thread.start()

            for thread in thread_list:
                thread.join()

            for move, result in results:
                if result < value:
                    value = result
                    self.best_move = move

        return self.best_move

    def max_value(self, game_logic, move, depth, alpha, beta, results):
        if depth == 0 or game_logic.is_game_over:
            result = AlphaBetaPruning.evaluate(game_logic)
            results.append((move, result))
            return
        value = float("-inf")
        game_logic.make_move(move)
        legal_moves = game_logic.generate_legal_moves()
        for next_move in legal_moves:
            result = max(
                value,
                self.min_value(
                    game_logic.make_copy(), next_move, depth - 1, alpha, beta, results
                ),
            )
            if result is not None:
                value = result
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        results.append((move, value))

    def min_value(self, game_logic, move, depth, alpha, beta, results):
        if depth == 0 or game_logic.is_game_over:
            result = AlphaBetaPruning.evaluate(game_logic)
            results.append((move, result))
            return
        value = float("inf")
        game_logic.make_move(move)
        legal_moves = game_logic.generate_legal_moves()
        for next_move in legal_moves:
            result = min(
                value,
                self.max_value(
                    game_logic.make_copy(), next_move, depth - 1, alpha, beta, results
                ),
            )
            if result is not None:
                value = result
            beta = min(beta, value)
            if beta <= alpha:
                break
        results.append((move, value))

    @staticmethod
    def evaluate(game_logic: GameLogic):
        board = game_logic.board
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
                    if game_logic.rule.is_fit_five(x, y, k):
                        continue

                    nx, ny = x, y
                    stone_cnt = 1
                    flag = False
                    is_one_space = False

                    is_one_side_block = False

                    if k != 0 and (
                        x == 0 or y == 0 or x == GRID_NUM - 1 or y == GRID_NUM - 1
                    ):
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
                            if (
                                nx == 0
                                or ny == 0
                                or nx == GRID_NUM - 1
                                or ny == GRID_NUM - 1
                            ):
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
                            if (
                                nx == 0
                                or ny == 0
                                or nx == GRID_NUM - 1
                                or ny == GRID_NUM - 1
                            ):
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
