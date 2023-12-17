import re
import numpy as np


def check_five(board, x: int, y: int, color: int):
    dx = [(1, -1), (0, 0), (1, -1), (1, -1)]
    dy = [(0, 0), (1, -1), (1, -1), (-1, 1)]
    for i in range(4):
        ndx = dx[i]
        ndy = dy[i]
        cnt = 1
        for j in range(2):
            tmp_x, tmp_y = x ^ 1, y ^ 1
            tmp_x, tmp_y = tmp_x ^ 1, tmp_y ^ 1
            while True:
                tmp_x += ndx[j]
                tmp_y += ndy[j]
                if 0 <= tmp_x < 15 and 0 <= tmp_y < 15 and board[tmp_x][tmp_y] == color:
                    cnt += 1
                else:
                    break
        if cnt >= 5:
            return True
    return False


def check_line(partial_board):
    partial_board = ''.join(partial_board.astype(str))
    res_b = re.search('11111', partial_board)
    res_w = re.search('22222', partial_board)
    if res_b is not None:
        return 'black win'
    if res_w is not None:
        return 'white win'
    return None


def check_win(board: np.array):
    for i in range(len(board)):
        partial_board = board[i, :]
        res = check_line(partial_board)
        if res is not None:
            return res

    for i in range(len(board)):
        partial_board = board[:, i]
        res = check_line(partial_board)
        if res is not None:
            return res

    for i in range(-(len(board) - 1), len(board)):
        partial_board = np.diagonal(board, offset=i)
        res = check_line(partial_board)
        if res is not None:
            return res

    flip_board = np.fliplr(board)
    for i in range(-(len(board) - 1), len(board)):
        partial_board = np.diagonal(flip_board, offset=i)
        res = check_line(partial_board)
        if res is not None:
            return res

    return None


def bxy2sxy(x, y, bl, lu_x, lu_y):
    return y * bl / 14 + lu_x, x * bl / 14 + lu_y


def sxy2bxy(x, y, bl, lu_x, lu_y):
    return round((y - lu_y) * 14 / bl), round((x - lu_x) * 14 / bl)
