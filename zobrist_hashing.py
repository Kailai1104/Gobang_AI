import numpy as np


class Zobrist_Hashing:
    def __init__(self) -> None:
        super().__init__()
        np.random.seed(2023)
        self.map = np.random.randint(1, 1000000000, size=(15, 15, 3), dtype='int64')
        self.init_hashing_value = 0
        for i in self.map[:, :, 0].reshape(225):
            self.init_hashing_value = self.init_hashing_value ^ i
        self.hashing_table = {}

    def calculate_hashing_value(self, hashing_value, x: int, y: int, c1: int, c2: int):
        """
        :param c1: 原状态
        :param c2: 新状态
        """
        return hashing_value ^ self.map[x][y][c1] ^ self.map[x][y][c2]

    def update_hashing_table(self, hashing_value: int, score: int, depth: int):
        self.hashing_table[(hashing_value, depth)] = score

    def get_score(self, hashing_value: int, depth: int):
        if (hashing_value, depth) in self.hashing_table:
            return self.hashing_table[(hashing_value, depth)]
        else:
            return None
