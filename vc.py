import re
import numpy as np
from functions import check_five


def check_pattern(pattern: re.Pattern, partial_board):
    if partial_board is None:
        return None
    tmp_res = pattern.search(partial_board)
    return None if tmp_res is None else tmp_res.span()


def generate_partial_boards(board, flip_board, x, y):
    partial_board1 = board[x, :]
    pl1 = len(partial_board1)
    partial_board1 = ("{}" * pl1).format(*(partial_board1[i] for i in range(pl1)))

    partial_board2 = board[:, y]
    pl2 = len(partial_board2)
    partial_board2 = ("{}" * pl2).format(*(partial_board2[i] for i in range(pl2)))

    partial_board3 = np.diagonal(board, offset=y - x)
    pl3 = len(partial_board3)
    if pl3 >= 5:
        partial_board3 = ("{}" * pl3).format(*(partial_board3[i] for i in range(pl3)))
    else:
        partial_board3 = None

    partial_board4 = np.diagonal(flip_board, offset=len(board) - 1 - y - x)
    pl4 = len(partial_board4)
    if pl4 >= 5:
        partial_board4 = ("{}" * pl4).format(*(partial_board4[i] for i in range(pl4)))
    else:
        partial_board4 = None

    return partial_board1, partial_board2, partial_board3, partial_board4


class VC:
    def __init__(self, color: int) -> None:
        super().__init__()
        if color == 1:  # 黑棋杀
            self.bl4 = re.compile('011110')
            self.bb4 = ['211110', '011112', '^11110', '01111$', '11101', '10111', '11011']
            self.bb4 = [re.compile(self.bb4[i]) for i in range(len(self.bb4))]
            self.bl3 = ['001110', '011100', '011010', '010110']
            self.bl3 = [re.compile(self.bl3[i]) for i in range(len(self.bl3))]
            self.wl4 = re.compile('022220')
            self.wb4 = {'122220': 5, '022221': 0, '^22220': 4, '02222$': 0, '22202': 3, '20222': 1, '22022': 2}
            self.wl3 = {'002220': (0, 1, 5), '022200': (0, 4, 5), '022020': (0, 3, 5), '020220': (0, 2, 5)}
        else:  # 白棋杀
            self.bl4 = re.compile('022220')
            self.bb4 = ['122220', '022221', '^22220', '02222$', '22202', '20222', '22022']
            self.bb4 = [re.compile(self.bb4[i]) for i in range(len(self.bb4))]
            self.bl3 = ['002220', '022200', '022020', '020220']
            self.bl3 = [re.compile(self.bl3[i]) for i in range(len(self.bl3))]
            self.wl4 = re.compile('011110')
            self.wb4 = {'211110': 5, '011112': 0, '^11110': 4, '01111$': 0, '11101': 3, '10111': 1, '11011': 2}
            self.wl3 = {'001110': (0, 1, 5), '011100': (0, 4, 5), '011010': (0, 3, 5), '010110': (0, 2, 5)}
        for key in self.wb4.keys():
            self.wb4[key] = [re.compile(key), self.wb4[key]]
        for key in self.wl3.keys():
            self.wl3[key] = [re.compile(key), self.wl3[key]]
        self.dx = [1, 1, 0, -1, -1, -1, 0, 1]
        self.dy = [0, 1, 1, 1, 0, -1, -1, -1]
        self._2dx = [2, 2, 0, -2, -2, -2, 0, 2]
        self._2dy = [0, 2, 2, 2, 0, -2, -2, -2]

    def vc_search(self, color: int, x: int, y: int, board: np.array, flip_board: np.array, depth: int, vc_flag: bool):
        """
        :param x: 上一步的x坐标
        :param y: 上一步的y坐标
        """
        if depth == 0:
            return False, None, None
        if vc_flag:  # 黑棋
            # 算白棋能否成连五，能的话直接返回不能
            bw_flag = check_five(board, x, y, 3 - color)
            if bw_flag:
                return False, None, None
            # 算黑棋能否成连五，能得话直接返回能
            vis = np.zeros((15, 15))
            for i in range(len(board)):
                for j in range(len(board)):
                    if board[i][j] == 0:
                        flag = 0
                        for k in range(8):
                            x1, y1 = i + self.dx[k], j + self.dy[k]
                            if 0 <= x1 < 15 and 0 <= y1 < 15:
                                if board[x1][y1] == color:
                                    flag = 1
                                    break
                        if flag == 1:
                            vis[i][j] = 1
                            board[i][j] = color
                            if check_five(board, i, j, color):
                                board[i][j] = 0
                                return True, i, j
                            board[i][j] = 0
            # 算白棋上一步是否形成活四，如形成则返回不能
            pb1, pb2, pb3, pb4 = generate_partial_boards(board, flip_board, x, y)
            if check_pattern(self.wl4, pb1) is not None or check_pattern(self.wl4, pb2) is not None or \
                    check_pattern(self.wl4, pb3) is not None or check_pattern(self.wl4, pb4):
                return False, None, None
            # 算白棋上一步是否形成冲四，形成冲四则选择防守位置继续递归
            for key in self.wb4:
                pattern = self.wb4[key][0]
                r1, r2, r3, r4 = check_pattern(pattern, pb1), check_pattern(pattern, pb2), check_pattern(pattern, pb3), \
                                 check_pattern(pattern, pb4)
                if r1 is not None:
                    n_y = r1[0] + self.wb4[key][1]
                    board[x][n_y] = color
                    flip_board[x][14 - n_y] = color
                    res, _, _ = self.vc_search(3 - color, x, n_y, board, flip_board, depth - 1, not vc_flag)
                    board[x][n_y] = 0
                    flip_board[x][14 - n_y] = 0
                    if res:
                        return True, x, n_y
                    else:
                        return False, None, None
                if r2 is not None:
                    n_x = r2[0] + self.wb4[key][1]
                    board[n_x][y] = color
                    flip_board[n_x][14 - y] = color
                    res, _, _ = self.vc_search(3 - color, n_x, y, board, flip_board, depth - 1, not vc_flag)
                    board[n_x][y] = 0
                    flip_board[n_x][14 - y] = 0
                    if res:
                        return True, n_x, y
                    else:
                        return False, None, None
                if r3 is not None:
                    if x > y:
                        n_y = r3[0] + self.wb4[key][1]
                        n_x = (x - y) + n_y
                    else:
                        n_x = r3[0] + self.wb4[key][1]
                        n_y = n_x + y - x
                    board[n_x][n_y] = color
                    flip_board[n_x][14 - n_y] = color
                    res, _, _ = self.vc_search(3 - color, n_x, n_y, board, flip_board, depth - 1, not vc_flag)
                    board[n_x][n_y] = 0
                    flip_board[n_x][14 - n_y] = 0
                    if res:
                        return True, n_x, n_y
                    else:
                        return False, None, None
                if r4 is not None:
                    f_y = 14 - y
                    if x > f_y:
                        n_y = r4[0] + self.wb4[key][1]
                        n_x = (x - f_y) + n_y
                        n_y = 14 - n_y
                    else:
                        n_x = r4[0] + self.wb4[key][1]
                        n_y = n_x + f_y - x
                        n_y = 14 - n_y
                    board[n_x][n_y] = color
                    flip_board[n_x][14 - n_y] = color
                    res, _, _ = self.vc_search(3 - color, n_x, n_y, board, flip_board, depth - 1, not vc_flag)
                    board[n_x][n_y] = 0
                    flip_board[n_x][14 - n_y] = 0
                    if res:
                        return True, n_x, n_y
                    else:
                        return False, None, None
            # 算黑棋能否形成活四，如形成则返回能
            for i in range(len(board)):
                for j in range(len(board)):
                    if vis[i][j] == 1:
                        board[i][j] = color
                        flip_board[i][14 - j] = color
                        _pb1, _pb2, _pb3, _pb4 = generate_partial_boards(board, flip_board, i, j)
                        if check_pattern(self.bl4, _pb1) is not None or check_pattern(self.bl4,
                                                                                      _pb2) is not None or \
                                check_pattern(self.bl4, _pb3) is not None or check_pattern(self.bl4, _pb4):
                            board[i][j] = 0
                            flip_board[i][14 - j] = 0
                            return True, i, j
                        board[i][j] = 0
                        flip_board[i][14 - j] = 0
            # 否则算黑棋有无能形成冲四的位置，有的话继续递归
            for i in range(len(board)):
                for j in range(len(board)):
                    if vis[i][j] == 1:
                        board[i][j] = color
                        flip_board[i][14 - j] = color
                        for pattern in self.bb4:
                            _pb1, _pb2, _pb3, _pb4 = generate_partial_boards(board, flip_board, i, j)
                            if check_pattern(pattern, _pb1) is not None or check_pattern(pattern, _pb2) is not None \
                                    or check_pattern(pattern, _pb3) is not None or check_pattern(pattern, _pb4):
                                res, _, _ = self.vc_search(3 - color, i, j, board, flip_board, depth - 1,
                                                           not vc_flag)
                                if res is True:
                                    board[i][j] = 0
                                    flip_board[i][14 - j] = 0
                                    return True, i, j
                        board[i][j] = 0
                        flip_board[i][14 - j] = 0
            # 否则算白棋有无活三，有的话防守
            for key in self.wl3:
                pattern = self.wl3[key][0]
                r1, r2, r3, r4 = check_pattern(pattern, pb1), check_pattern(pattern, pb2), check_pattern(
                    pattern, pb3), \
                                 check_pattern(pattern, pb4)
                if r1 is not None:
                    for i in range(3):
                        n_y = r1[0] + self.wl3[key][1][i]
                        board[x][n_y] = color
                        flip_board[x][14 - n_y] = color
                        res, _, _ = self.vc_search(3 - color, x, n_y, board, flip_board, depth - 1, not vc_flag)
                        board[x][n_y] = 0
                        flip_board[x][14 - n_y] = 0
                        if res:
                            return True, x, n_y
                    return False, None, None
                if r2 is not None:
                    for i in range(3):
                        n_x = r2[0] + self.wl3[key][1][i]
                        board[n_x][y] = color
                        flip_board[n_x][14 - y] = color
                        res, _, _ = self.vc_search(3 - color, n_x, y, board, flip_board, depth - 1, not vc_flag)
                        board[n_x][y] = 0
                        flip_board[n_x][14 - y] = 0
                        if res:
                            return True, n_x, y
                    return False, None, None
                if r3 is not None:
                    for i in range(3):
                        if x > y:
                            n_y = r3[0] + self.wl3[key][1][i]
                            n_x = (x - y) + n_y
                        else:
                            n_x = r3[0] + self.wl3[key][1][i]
                            n_y = n_x + y - x
                        board[n_x][n_y] = color
                        flip_board[n_x][14 - n_y] = color
                        res, _, _ = self.vc_search(3 - color, n_x, n_y, board, flip_board, depth - 1,
                                                   not vc_flag)
                        board[n_x][n_y] = 0
                        flip_board[n_x][14 - n_y] = 0
                        if res:
                            return True, n_x, n_y
                    return False, None, None
                if r4 is not None:
                    for i in range(3):
                        f_y = 14 - y
                        if x > f_y:
                            n_y = r4[0] + self.wl3[key][1][i]
                            n_x = (x - f_y) + n_y
                            n_y = 14 - n_y
                        else:
                            n_x = r4[0] + self.wl3[key][1][i]
                            n_y = n_x + f_y - x
                            n_y = 14 - n_y
                        board[n_x][n_y] = color
                        flip_board[n_x][14 - n_y] = color
                        res, _, _ = self.vc_search(3 - color, n_x, n_y, board, flip_board, depth - 1,
                                                   not vc_flag)
                        board[n_x][n_y] = 0
                        flip_board[n_x][14 - n_y] = 0
                        if res:
                            return True, n_x, n_y
                    return False, None, None
            # 否则算黑棋有无能形成活三的位置，有的话进攻
            for i in range(len(board)):
                for j in range(len(board)):
                    if vis[i][j] == 1:
                        board[i][j] = color
                        flip_board[i][14 - j] = color
                        for pattern in self.bl3:
                            pb1, pb2, pb3, pb4 = generate_partial_boards(board, flip_board, i, j)
                            if check_pattern(pattern, pb1) is not None or check_pattern(pattern, pb2) is not None \
                                    or check_pattern(pattern, pb3) is not None or check_pattern(pattern, pb4):
                                res, _, _ = self.vc_search(3 - color, i, j, board, flip_board, depth - 1,
                                                           not vc_flag)
                                if res is True:
                                    board[i][j] = 0
                                    flip_board[i][14 - j] = 0
                                    return True, i, j
                        board[i][j] = 0
                        flip_board[i][14 - j] = 0

            return False, None, None
        else:  # 白棋
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
                            board[i][j] = color
                            flip_board[i][14 - j] = color
                            res, _, _ = self.vc_search(3 - color, i, j, board, flip_board, depth - 1, not vc_flag)
                            board[i][j] = 0
                            flip_board[i][14 - j] = 0
                            if res is False:
                                return False, None, None

            return True, None, None
