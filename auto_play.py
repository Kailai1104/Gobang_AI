import numpy as np
import time
from copy import deepcopy
import pyautogui
from alpha_beta_search import Min_Max_Search
from vc import VC
from functions import bxy2sxy, sxy2bxy

pyautogui.FAILSAFE = True  # 自启动故障处理

if __name__ == '__main__':
    # 初始化参数与变量
    board_length = 385
    b = np.zeros((15, 15)).astype(int)
    row_s = np.zeros(len(b)).astype(int)
    col_s = np.zeros(len(b)).astype(int)
    diag_s = np.zeros(2 * len(b) - 1).astype(int)
    t_diag_s = np.zeros(2 * len(b) - 1).astype(int)
    search_machine = Min_Max_Search(2)
    hashing_v = search_machine.zobrist.init_hashing_value

    # 定位棋盘
    loc = pyautogui.locateCenterOnScreen("images/icon0.png", confidence=0.8)
    region = (loc.x - 207, loc.y + 213, loc.x + 207, loc.y + 645)
    lu_x, lu_y = loc.x - 193, loc.y + 227
    region2 = (loc.x - 207, loc.y + 645, loc.x + 207, loc.y + 845)

    # 对战局数
    epoch = 10

    while epoch > 0:
        print(f'----epoch{epoch}----')
        epoch -= 1
        flag = pyautogui.locateCenterOnScreen("images/icon5.png", confidence=0.8, region=region2)  # 游戏是否结束
        chess_flag = None
        loc1, loc2 = None, None
        while flag is None:
            # 判断AI执哪种棋
            while chess_flag is None and loc1 is None and loc2 is None:
                loc1 = pyautogui.locateCenterOnScreen("images/icon3.png", confidence=0.8,
                                                      region=region2)  # region参数限制查找范围，加快查找速度
                loc2 = pyautogui.locateCenterOnScreen("images/icon4.png", confidence=0.8,
                                                      region=region2)  # region参数限制查找范围，加快查找速度
            if loc1 is not None:
                chess_flag = 2
                n_chess = 'images/icon2.png'
            else:
                chess_flag = 1
                n_chess = 'images/icon1.png'
            vc_machine = VC(3 - chess_flag)
            trans_vc_machine = VC(chess_flag)
            # 先手下中间
            if chess_flag == 2 and np.sum(b) == 0:
                w_x, w_y = 7, 7
                b[w_x][w_y] = 1
                hashing_v = search_machine.zobrist.calculate_hashing_value(hashing_v, w_x, w_y, 0, 1)
                pyautogui.click(*bxy2sxy(w_x, w_y, board_length, lu_x, lu_y), clicks=2)
            # 获取对方下棋的坐标
            n_x, n_y = None, None
            # 等待对方下棋
            while n_x is None:
                tmp_res = pyautogui.locateCenterOnScreen(n_chess, confidence=0.8,
                                                         region=region)
                if tmp_res is not None:
                    n_x, n_y = tmp_res
                # 判断对方是否投降
                flag = pyautogui.locateCenterOnScreen("images/icon5.png", confidence=0.8, region=region2)
                if flag is not None:
                    break
            if flag is not None:
                break
            # 对方落子
            pyautogui.moveTo(n_x, n_y)
            x, y = sxy2bxy(n_x, n_y, board_length, lu_x, lu_y)
            b[x][y] = chess_flag
            hashing_v = search_machine.zobrist.calculate_hashing_value(hashing_v, x, y, 0, chess_flag)
            _, row_s, col_s, diag_s, t_diag_s = search_machine.eval_machine.evaluate(b, row_s, col_s,
                                                                                     diag_s, t_diag_s,
                                                                                     x, y)

            # AI落子
            t1 = time.time_ns()
            vc_f, w_x, w_y = vc_machine.vc_search(3 - chess_flag, int(x), int(y), b, np.fliplr(b), 5, True)
            if vc_f is False:
                _, w_x, w_y, positions = search_machine.search(b, row_s, col_s, diag_s, t_diag_s, 0,
                                                               3 - chess_flag,
                                                               (False if chess_flag == 1 else True),
                                                               -10000000000,
                                                               10000000000, deepcopy(hashing_v))
                positions = sorted(positions, key=lambda x: x[2])
                for w_x, w_y, _s in positions:
                    b[w_x][w_y] = 3 - chess_flag
                    d_vc_f, _, _ = trans_vc_machine.vc_search(chess_flag, w_x, w_y, b, np.fliplr(b), 5,
                                                              True)
                    if d_vc_f:
                        b[w_x][w_y] = 0
                        print('trying to defend')
                    else:
                        print('defended')
                        break
            else:
                print('vc yes!')
            t2 = time.time_ns()
            b[w_x][w_y] = 3 - chess_flag
            hashing_v = search_machine.zobrist.calculate_hashing_value(hashing_v, w_x, w_y, 0,
                                                                       3 - chess_flag)
            _, row_s, col_s, diag_s, t_diag_s = search_machine.eval_machine.evaluate(b, row_s, col_s,
                                                                                     diag_s,
                                                                                     t_diag_s, w_x, w_y)
            print('searching time:', (t2 - t1) / 1e9, ' ', 'eval_val:', _)

            pyautogui.click(*bxy2sxy(w_x, w_y, board_length, lu_x, lu_y), clicks=2)

        b = np.zeros((15, 15)).astype(int)
        row_s = np.zeros(len(b)).astype(int)
        col_s = np.zeros(len(b)).astype(int)
        diag_s = np.zeros(2 * len(b) - 1).astype(int)
        t_diag_s = np.zeros(2 * len(b) - 1).astype(int)
        hashing_v = search_machine.zobrist.init_hashing_value
        # 保存数据
        # save_variable(search_machine.eval_machine.eval_dict, r'eval_memory.pkl')
        if epoch > 0:
            # 离开
            tmp_loc = pyautogui.locateCenterOnScreen("images/icon6.png", confidence=0.8, region=region2)
            pyautogui.click(*tmp_loc)

            # 开始
            tmp_loc = pyautogui.locateCenterOnScreen("images/icon7.png", confidence=0.8, region=region)
            pyautogui.click(*tmp_loc)
