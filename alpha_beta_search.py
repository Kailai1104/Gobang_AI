import numpy as np
from copy import deepcopy
from evaluation import Evaluation
from zobrist_hashing import Zobrist_Hashing
from functions import check_five


class Min_Max_Search:
    def __init__(self, d: int) -> None:
        super().__init__()
        self.dx = [1, 1, 0, -1, -1, -1, 0, 1]
        self.dy = [0, 1, 1, 1, 0, -1, -1, -1]
        self._2dx = [2, 2, 0, -2, -2, -2, 0, 2]
        self._2dy = [0, 2, 2, 2, 0, -2, -2, -2]
        self.depth = d
        self.n_depth = 0
        self.eval_machine = Evaluation()
        self.zobrist = Zobrist_Hashing()

    def search(
            self,
            board: np.array,
            row_score,
            col_score,
            diag_score,
            trans_diag_score,
            score: int,
            color: int,
            max_or_min: bool,
            alpha: float,
            beta: float,
            hashing_value: int,
    ):
        """
        color: 1 for black and 2 for white
        max_or_min: True for max and False for min
        """
        if self.n_depth == self.depth:
            return score
        self.n_depth += 1
        if self.n_depth == 1:
            positions = []

        max_score = float('-inf')
        min_score = float('inf')
        a_x, a_y = None, None
        alpha_beta_flag = False

        for i in range(len(board)):
            for j in range(len(board)):
                flag = 0
                if board[i][j] == 0:
                    # 位置剪枝
                    for k in range(8):
                        x1, y1 = i + self.dx[k], j + self.dy[k]
                        if 0 <= x1 < 15 and 0 <= y1 < 15:
                            if board[x1][y1] != 0:
                                flag = 1
                                break
                            else:
                                x2, y2 = i + self._2dx[k], j + self._2dy[k]
                                if 0 <= x2 < 15 and 0 <= y2 < 15:
                                    if board[x2][y2] != 0:
                                        flag = 1
                                        break
                    if flag == 1:
                        r_s = deepcopy(row_score)
                        c_s = deepcopy(col_score)
                        d_s = deepcopy(diag_score)
                        t_s = deepcopy(trans_diag_score)
                        if color == 2:
                            board[i][j] = 2
                        else:
                            board[i][j] = 1

                        hashing_value = self.zobrist.calculate_hashing_value(hashing_value, i, j, 0, color)
                        hashing_res = self.zobrist.get_score(hashing_value, self.depth)
                        if hashing_res is not None:
                            score = hashing_res
                        else:
                            s, _, _, _, _ = self.eval_machine.evaluate(board, r_s, c_s, d_s, t_s, i, j)
                            if check_five(board, i, j, color):
                                score = s
                            else:
                                score = self.search(board, r_s, c_s, d_s, t_s, s, 3 - color, not max_or_min,
                                                    deepcopy(alpha), deepcopy(beta), deepcopy(hashing_value))
                            if self.n_depth == 1:
                                if max_or_min:
                                    positions.append((i, j, -score))
                                else:
                                    positions.append((i, j, score))
                            self.zobrist.update_hashing_table(hashing_value, score, self.depth)
                        if max_or_min and score > max_score:
                            alpha = max(alpha, score)
                            max_score = score
                            a_x, a_y = i, j
                        if not max_or_min and score < min_score:
                            beta = min(beta, score)
                            min_score = score
                            a_x, a_y = i, j
                        board[i][j] = 0
                        hashing_value = self.zobrist.calculate_hashing_value(hashing_value, i, j, color, 0)
                        if beta <= alpha:
                            alpha_beta_flag = True
                            break
            if alpha_beta_flag:
                break

        self.n_depth -= 1

        if self.n_depth == 0:
            return (max_score if max_or_min else min_score), a_x, a_y, positions
        else:
            return (max_score if max_or_min else min_score)
