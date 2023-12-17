import numpy as np
import pygame
import pygame.gfxdraw
import sys
from pygame.locals import QUIT, KEYDOWN
from alpha_beta_search import Min_Max_Search
from vc import VC
import time
from copy import deepcopy
from functions import check_five


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        font = pygame.font.SysFont("SimHei", 24)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Game:

    def __init__(self, margin=62, grid_width=44, board_width=740, board_height=820, line_color=(105, 105, 105),
                 screen_color=(230, 230, 250), chess_flag=2, button_width=80, button_height=30) -> None:
        super().__init__()
        self.margin = margin
        self.grid_width = grid_width
        self.board_width = board_width
        self.board_height = board_height
        self.line_color = line_color
        self.screen_color = screen_color
        self.reset(chess_flag)
        self.button_b = Button(board_width // 3 - button_width // 2 + 1,
                               board_width + (board_height - board_width) // 8 - button_height // 2, button_width,
                               button_height, '黑棋', (105, 105, 105))
        self.button_w = Button(2 * board_width // 3 - button_width // 2 + 6,
                               board_width + (board_height - board_width) // 8 - button_height // 2, button_width,
                               button_height, '白棋', (105, 105, 105))
        self.button_r = Button(board_width // 2 - button_width // 2 + 2,
                               board_width + (board_height - board_width) // 8 - button_height // 2, button_width,
                               button_height, '重开', (105, 105, 105))

    def reset(self, chess_flag):
        self.playing_flag = False
        self.ai_run_flag = False
        self.chess_flag = chess_flag
        self.board = np.zeros((15, 15)).astype(int)
        self.ai = Min_Max_Search(2)
        self.hashing_v = self.ai.zobrist.init_hashing_value
        self.vc_machine = VC(3 - self.chess_flag)
        self.trans_vc_machine = VC(self.chess_flag)
        self.chess_count = 0
        self.row_s = np.zeros(15).astype(int)
        self.col_s = np.zeros(15).astype(int)
        self.diag_s = np.zeros(29).astype(int)
        self.t_diag_s = np.zeros(29).astype(int)

        pygame.init()
        self.screen = pygame.display.set_mode((self.board_width, self.board_height))

    def draw_board(self):
        line_margin = 8
        for i in range(self.margin, self.board_width - self.grid_width + 1, self.grid_width):
            if i == self.margin:
                pygame.draw.line(self.screen, self.line_color, [i - line_margin, self.margin - line_margin],
                                 [i - line_margin, self.board_width - self.margin + line_margin], 2)
                pygame.draw.line(self.screen, self.line_color, [i, self.margin], [i, self.board_width - self.margin], 2)
            elif i == self.board_width - self.margin:
                pygame.draw.line(self.screen, self.line_color, [i + line_margin, self.margin - line_margin],
                                 [i + line_margin, self.board_width - self.margin + line_margin], 2)
                pygame.draw.line(self.screen, self.line_color, [i, self.margin], [i, self.board_width - self.margin], 2)
            else:
                pygame.draw.line(self.screen, self.line_color, [i, self.margin], [i, self.board_width - self.margin], 2)
            if i == self.margin:
                pygame.draw.line(self.screen, self.line_color, [self.margin - line_margin, i - line_margin],
                                 [self.board_width - self.margin + line_margin, i - line_margin], 2)
                pygame.draw.line(self.screen, self.line_color, [self.margin, i], [self.board_width - self.margin, i], 2)
            elif i == self.board_width - self.margin:
                pygame.draw.line(self.screen, self.line_color, [self.margin - line_margin, i + line_margin],
                                 [self.board_width - self.margin + line_margin, i + line_margin], 2)
                pygame.draw.line(self.screen, self.line_color, [self.margin, i], [self.board_width - self.margin, i], 2)

            else:
                pygame.draw.line(self.screen, self.line_color, [self.margin, i], [self.board_width - self.margin, i], 2)
        pygame.draw.circle(self.screen, self.line_color,
                           [self.margin + self.grid_width * 7 + 1, self.margin + self.grid_width * 7 + 1], 6, 0)

    def draw_chess(self, x, y, color):
        if color == 1:  # 黑棋
            pygame.gfxdraw.filled_circle(self.screen, self.margin + self.grid_width * x,
                                         self.margin + self.grid_width * y, 16, [105, 105, 105])
            pygame.gfxdraw.aacircle(self.screen, self.margin + self.grid_width * x, self.margin + self.grid_width * y,
                                    16, [105, 105, 105])
        elif color == 2:
            pygame.gfxdraw.filled_circle(self.screen, self.margin + self.grid_width * x,
                                         self.margin + self.grid_width * y, 16, [255, 255, 255])
            pygame.gfxdraw.aacircle(self.screen, self.margin + self.grid_width * x, self.margin + self.grid_width * y,
                                    16, [255, 255, 255])

    def human_play(self, event):
        x = round((event.pos[0] - self.margin) / self.grid_width)
        y = round((event.pos[1] - self.margin) / self.grid_width)
        if 15 > x >= 0 and 0 <= y < 15:
            if self.board[x][y] == 0:
                self.board[x][y] = self.chess_flag
                self.hashing_v = self.ai.zobrist.calculate_hashing_value(self.hashing_v, x, y, 0, self.chess_flag)
                _, row_s, col_s, diag_s, t_diag_s = self.ai.eval_machine.evaluate(self.board, self.row_s, self.col_s,
                                                                                  self.diag_s, self.t_diag_s,
                                                                                  x, y)
                self.chess_count += 1
                self.ai_run_flag = True
                self.chess_count += 1
                return x, y
        return None, None

    def ai_play(self, x, y):
        # AI落子
        t1 = time.time_ns()
        vc_f, a_x, a_y = self.vc_machine.vc_search(3 - self.chess_flag, x, y, self.board, np.fliplr(self.board), 5,
                                                   True)
        if vc_f is False:
            _, a_x, a_y, positions = self.ai.search(self.board, self.row_s, self.col_s, self.diag_s, self.t_diag_s, 0,
                                                    3 - self.chess_flag,
                                                    (False if self.chess_flag == 1 else True),
                                                    -10000000000,
                                                    10000000000, deepcopy(self.hashing_v))
            if self.board[a_x][a_y] != 0:
                print()
            positions = sorted(positions, key=lambda x: x[2])
            for a_x, a_y, _s in positions:
                self.board[a_x][a_y] = 3 - self.chess_flag
                d_vc_f, _, _ = self.trans_vc_machine.vc_search(self.chess_flag, a_x, a_y, self.board,
                                                               np.fliplr(self.board), 5, True)
                if d_vc_f:
                    self.board[a_x][a_y] = 0
                    print('trying to defend')
                else:
                    print('defended')
                    break
        else:
            print('vc yes!')
        t2 = time.time_ns()
        self.board[a_x][a_y] = 3 - self.chess_flag
        self.hashing_v = self.ai.zobrist.calculate_hashing_value(self.hashing_v, a_x, a_y, 0,
                                                                 3 - self.chess_flag)
        _, row_s, col_s, diag_s, t_diag_s = self.ai.eval_machine.evaluate(self.board, self.row_s, self.col_s,
                                                                          self.diag_s,
                                                                          self.t_diag_s, a_x, a_y)
        print('searching time:', (t2 - t1) / 1e9, ' ', 'eval_val:', _)
        self.ai_run_flag = False
        self.chess_count += 1
        return a_x, a_y

    def draw(self):
        self.screen.fill(self.screen_color)
        self.draw_board()
        for i in range(15):
            for j in range(15):
                if self.board[i][j] != 0:
                    self.draw_chess(i, j, self.board[i][j])
        if self.playing_flag:
            self.button_r.draw(self.screen)
        else:
            self.button_b.draw(self.screen)
            self.button_w.draw(self.screen)

    def run_game_epoch(self):
        while True:
            if self.chess_flag == 2 and self.chess_count == 0:
                a_x, a_y = 7, 7
                self.board[7][7] = 1
                self.hashing_v = self.ai.zobrist.calculate_hashing_value(self.hashing_v, a_x, a_y, 0, 1)

                self.draw()
                pygame.display.update()
            if not self.ai_run_flag:
                for event in pygame.event.get():
                    if event.type in (QUIT, KEYDOWN):
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.button_r.rect.collidepoint(event.pos):
                            self.reset(self.chess_flag)
                            self.playing_flag = False
                            return None
                    if event.type == pygame.MOUSEBUTTONUP:
                        x, y = self.human_play(event)
                    if self.ai_run_flag:
                        if check_five(self.board, x, y, self.chess_flag):
                            return 'human win'
                        if self.chess_count == 225:
                            return 'draw'
                        self.draw()
                        pygame.display.update()
                        break
            if self.ai_run_flag:
                a_x, a_y = self.ai_play(x, y)
                if check_five(self.board, a_x, a_y, 3 - self.chess_flag):
                    return 'ai win'
                if self.chess_count == 225:
                    return 'draw'
                self.draw()
                pygame.display.update()

    def run(self):
        while True:
            self.draw()
            pygame.display.update()
            if not self.playing_flag:
                for event in pygame.event.get():
                    if event.type in (QUIT, KEYDOWN):
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.button_b.rect.collidepoint(event.pos):
                            self.reset(1)
                            self.playing_flag = True
                            break
                        if self.button_w.rect.collidepoint(event.pos):
                            self.reset(2)
                            self.playing_flag = True
                            break
            else:
                res = self.run_game_epoch()
                print(res)
                self.playing_flag = False


if __name__ == '__main__':
    game = Game()
    print(game.run())
