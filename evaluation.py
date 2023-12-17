import re
import numpy as np


class Evaluation:
    def __init__(self) -> None:
        super().__init__()
        self.black_dict = {
            '11111': '连五', '011110': '活四', '211110': '冲四', '011112': '冲四', '^11110': '冲四', '01111$': '冲四',
            '11101': '冲四', '10111': '冲四', '11011': '冲四', '001110': '活三', '011100': '活三', '011010': '活三',
            '010110': '活三', '211100': '眠三', '001112': '眠三', '^11100': '眠三', '00111$': '眠三', '211010': '眠三',
            '010112': '眠三', '^11010': '眠三', '01011$': '眠三', '210110': '眠三', '011012': '眠三', '^10110': '眠三',
            '01101$': '眠三', '11001': '眠三', '10011': '眠三', '10101': '眠三', '2011102': '眠三', '201110$': '眠三',
            '^011102': '眠三', '^01110$': '眠三', '000110': '活二', '011000': '活二', '001010': '活二', '010100': '活二',
            '010010': '活二', '001100': '活二', '211000': '眠二', '000112': '眠二', '^11000': '眠二', '00011$': '眠二',
            '210100': '眠二', '001012': '眠二', '^10100': '眠二', '00101$': '眠二', '210010': '眠二', '010012': '眠二',
            '^10010': '眠二', '01001$': '眠二', '10001': '眠二', '2011002': '眠二', '2001102': '眠二', '^011002': '眠二',
            '200110$': '眠二', '201100$': '眠二', '^001102': '眠二', '^01100$': '眠二', '^00110$': '眠二', '2010102': '眠二',
            '^010102': '眠二', '201010$': '眠二', '^01010$': '眠二'
        }
        self.white_dict = {
            '22222': '连五', '022220': '活四', '122220': '冲四', '022221': '冲四', '^22220': '冲四', '02222$': '冲四',
            '22202': '冲四', '20222': '冲四', '22022': '冲四', '002220': '活三', '022200': '活三', '022020': '活三',
            '020220': '活三', '122200': '眠三', '002221': '眠三', '^22200': '眠三', '00222$': '眠三', '122020': '眠三',
            '020221': '眠三', '^22020': '眠三', '02022$': '眠三', '120220': '眠三', '022021': '眠三', '^20220': '眠三',
            '02202$': '眠三', '22002': '眠三', '20022': '眠三', '20202': '眠三', '1022201': '眠三', '102220$': '眠三',
            '^022201': '眠三', '^02220$': '眠三', '000220': '活二', '022000': '活二', '002020': '活二', '020200': '活二',
            '020020': '活二', '002200': '活二', '122000': '眠二', '000221': '眠二', '^22000': '眠二', '00022$': '眠二',
            '120200': '眠二', '002021': '眠二', '^20200': '眠二', '00202$': '眠二', '120020': '眠二', '020021': '眠二',
            '^20020': '眠二', '02002$': '眠二', '20002': '眠二', '1022001': '眠二', '1002201': '眠二', '^022001': '眠二',
            '100220$': '眠二', '102200$': '眠二', '^002201': '眠二', '^02200$': '眠二', '^00220$': '眠二', '1020201': '眠二',
            '^020201': '眠二', '102020$': '眠二', '^02020$': '眠二'
        }
        self.score_dict = {
            '连五': [3000000, -3000000],
            '活四': [300000, -300000],
            '冲四': [2700, -2700],
            '活三': [3000, -3000],
            '眠三': [613, -613],
            '活二': [650, -650],
            '眠二': [200, -200]
        }  # 黑色正分，白色负分

        # 预处理两个dict
        for key in self.black_dict.keys():
            self.black_dict[key] = [re.compile(key), self.black_dict[key], key.count('1')]
        for key in self.white_dict.keys():
            self.white_dict[key] = [re.compile(key), self.white_dict[key], key.count('2')]

    def calculate_partial_score(self, partial_board, partial_score, idx: int, color: str, bias: int):
        partial_board = ''.join(partial_board.astype(str))
        if color == '1':  # 黑色
            tmp_dict = self.black_dict
        else:
            tmp_dict = self.white_dict
        vis_board = np.zeros(len(partial_board))
        for key in tmp_dict.keys():
            if tmp_dict[key][2] > bias:
                continue
            res = tmp_dict[key][0].finditer(partial_board)
            # res = re.finditer(key, partial_board)
            for tmp_res in res:
                # 避免重复计分
                if np.max(vis_board[tmp_res.span()[0]: tmp_res.span()[1]]) == 1:
                    continue
                bias -= tmp_dict[key][2]
                # 给vis_board涂色
                tmp_ar = np.zeros(len(vis_board))
                tmp_ar[tmp_res.span()[0] + np.where(np.array(list(tmp_res.group())) == color)[0]] = 1
                vis_board += tmp_ar
                partial_score[idx] += self.score_dict[tmp_dict[key][1]][int(color) - 1]

    def evaluate(
            self,
            board: np.array,
            row_score: np.array,
            column_score: np.array,
            diag_score: np.array,
            trans_diag_score: np.array,
            x: int,
            y: int,
    ):
        # 第x行
        row_score[x] = 0
        partial_board = board[x, :]
        num_of_chess = np.bincount(partial_board)
        self.calculate_partial_score(partial_board, row_score, x, '1', num_of_chess[1])
        self.calculate_partial_score(partial_board, row_score, x, '2',
                                     (0 if len(num_of_chess) < 3 else num_of_chess[2]))
        # 第y列
        column_score[y] = 0
        partial_board = board[:, y]
        num_of_chess = np.bincount(partial_board)
        self.calculate_partial_score(partial_board, column_score, y, '1', num_of_chess[1])
        self.calculate_partial_score(partial_board, column_score, y, '2',
                                     (0 if len(num_of_chess) < 3 else num_of_chess[2]))
        # 主对角线方向
        diag_score[(y - x) + len(board) - 1] = 0
        partial_board = np.diagonal(board, offset=y - x)
        num_of_chess = np.bincount(partial_board)
        self.calculate_partial_score(partial_board, diag_score, (y - x) + len(board) - 1, '1', num_of_chess[1])
        self.calculate_partial_score(partial_board, diag_score, (y - x) + len(board) - 1, '2',
                                     (0 if len(num_of_chess) < 3 else num_of_chess[2]))
        # 副对角线方向
        flip_board = np.fliplr(board)
        trans_diag_score[2 * (len(board) - 1) - y - x] = 0
        partial_board = np.diagonal(flip_board, offset=len(board) - 1 - y - x)
        num_of_chess = np.bincount(partial_board)
        self.calculate_partial_score(partial_board, trans_diag_score, 2 * (len(board) - 1) - y - x, '1',
                                     num_of_chess[1])
        self.calculate_partial_score(partial_board, trans_diag_score, 2 * (len(board) - 1) - y - x, '2',
                                     (0 if len(num_of_chess) < 3 else num_of_chess[2]))

        return np.sum(row_score) + np.sum(column_score) + np.sum(diag_score) + np.sum(trans_diag_score), \
               row_score, column_score, diag_score, trans_diag_score



