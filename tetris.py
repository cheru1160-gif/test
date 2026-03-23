import pygame
import random
import sys

# 定数
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 700
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 50

FPS = 60

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
BORDER_COLOR = (80, 80, 80)

COLORS = [
    (0, 0, 0),        # 0: 空
    (0, 240, 240),    # 1: I - シアン
    (240, 240, 0),    # 2: O - 黄
    (160, 0, 240),    # 3: T - 紫
    (0, 240, 0),      # 4: S - 緑
    (240, 0, 0),      # 5: Z - 赤
    (0, 0, 240),      # 6: J - 青
    (240, 160, 0),    # 7: L - オレンジ
]

# テトリミノの形状（回転4パターン）
TETROMINOES = {
    'I': [
        [[0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,0,1,0],
         [0,0,1,0],
         [0,0,1,0],
         [0,0,1,0]],
        [[0,0,0,0],
         [0,0,0,0],
         [1,1,1,1],
         [0,0,0,0]],
        [[0,1,0,0],
         [0,1,0,0],
         [0,1,0,0],
         [0,1,0,0]],
    ],
    'O': [
        [[0,1,1,0],
         [0,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
    ] * 4,
    'T': [
        [[0,1,0],
         [1,1,1],
         [0,0,0]],
        [[0,1,0],
         [0,1,1],
         [0,1,0]],
        [[0,0,0],
         [1,1,1],
         [0,1,0]],
        [[0,1,0],
         [1,1,0],
         [0,1,0]],
    ],
    'S': [
        [[0,1,1],
         [1,1,0],
         [0,0,0]],
        [[0,1,0],
         [0,1,1],
         [0,0,1]],
        [[0,0,0],
         [0,1,1],
         [1,1,0]],
        [[1,0,0],
         [1,1,0],
         [0,1,0]],
    ],
    'Z': [
        [[1,1,0],
         [0,1,1],
         [0,0,0]],
        [[0,0,1],
         [0,1,1],
         [0,1,0]],
        [[0,0,0],
         [1,1,0],
         [0,1,1]],
        [[0,1,0],
         [1,1,0],
         [1,0,0]],
    ],
    'J': [
        [[1,0,0],
         [1,1,1],
         [0,0,0]],
        [[0,1,1],
         [0,1,0],
         [0,1,0]],
        [[0,0,0],
         [1,1,1],
         [0,0,1]],
        [[0,1,0],
         [0,1,0],
         [1,1,0]],
    ],
    'L': [
        [[0,0,1],
         [1,1,1],
         [0,0,0]],
        [[0,1,0],
         [0,1,0],
         [0,1,1]],
        [[0,0,0],
         [1,1,1],
         [1,0,0]],
        [[1,1,0],
         [0,1,0],
         [0,1,0]],
    ],
}

PIECE_NAMES = list(TETROMINOES.keys())
PIECE_COLORS = {'I': 1, 'O': 2, 'T': 3, 'S': 4, 'Z': 5, 'J': 6, 'L': 7}


class Tetromino:
    def __init__(self, name=None):
        self.name = name or random.choice(PIECE_NAMES)
        self.color = PIECE_COLORS[self.name]
        self.rotation = 0
        self.shape = TETROMINOES[self.name]
        # 初期位置（中央上部）
        self.x = BOARD_WIDTH // 2 - len(self.shape[0][0]) // 2
        self.y = 0

    def get_cells(self):
        """現在の回転状態でのセル座標リストを返す"""
        shape = self.shape[self.rotation]
        cells = []
        for row_i, row in enumerate(shape):
            for col_i, val in enumerate(row):
                if val:
                    cells.append((self.x + col_i, self.y + row_i))
        return cells

    def rotated(self, direction=1):
        """回転後のTetromino（コピー）を返す"""
        t = Tetromino.__new__(Tetromino)
        t.name = self.name
        t.color = self.color
        t.shape = self.shape
        t.rotation = (self.rotation + direction) % len(self.shape)
        t.x = self.x
        t.y = self.y
        return t


class TetrisGame:
    def __init__(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current = Tetromino()
        self.next = Tetromino()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = self._get_fall_speed()

    def _get_fall_speed(self):
        """レベルに応じた落下速度（ミリ秒）"""
        return max(100, 800 - (self.level - 1) * 70)

    def is_valid(self, piece):
        """ピースの位置が有効か確認"""
        for x, y in piece.get_cells():
            if x < 0 or x >= BOARD_WIDTH:
                return False
            if y >= BOARD_HEIGHT:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True

    def lock_piece(self):
        """現在のピースをボードに固定"""
        for x, y in self.current.get_cells():
            if y >= 0:
                self.board[y][x] = self.current.color
        self._clear_lines()
        self.current = self.next
        self.next = Tetromino()
        if not self.is_valid(self.current):
            self.game_over = True

    def _clear_lines(self):
        """揃ったラインを消去してスコア加算"""
        new_board = [row for row in self.board if any(c == 0 for c in row)]
        cleared = BOARD_HEIGHT - len(new_board)
        if cleared > 0:
            empty_rows = [[0] * BOARD_WIDTH for _ in range(cleared)]
            self.board = empty_rows + new_board
            self.lines_cleared += cleared
            # スコア計算
            score_table = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += score_table.get(cleared, 800) * self.level
            # レベルアップ（10ライン毎）
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = self._get_fall_speed()

    def move(self, dx, dy):
        """ピースを移動。成功したらTrue"""
        moved = Tetromino.__new__(Tetromino)
        moved.__dict__ = self.current.__dict__.copy()
        moved.x += dx
        moved.y += dy
        if self.is_valid(moved):
            self.current = moved
            return True
        return False

    def rotate(self, direction=1):
        """ピースを回転。壁蹴りあり"""
        rotated = self.current.rotated(direction)
        kicks = [0, -1, 1, -2, 2]
        for kick in kicks:
            rotated.x = self.current.x + kick
            if self.is_valid(rotated):
                self.current = rotated
                return True
        return False

    def hard_drop(self):
        """ハードドロップ（一番下まで落とす）"""
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()

    def get_ghost_cells(self):
        """ゴーストピース（落下予測）のセル座標"""
        ghost = Tetromino.__new__(Tetromino)
        ghost.__dict__ = self.current.__dict__.copy()
        ghost.shape = self.current.shape
        while True:
            ghost.y += 1
            if not self.is_valid(ghost):
                ghost.y -= 1
                break
        return ghost.get_cells()

    def update(self, dt):
        """ゲーム状態を更新"""
        if self.game_over or self.paused:
            return
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.move(0, 1):
                self.lock_piece()


def draw_cell(surface, x, y, color, alpha=255):
    """セルを描画"""
    rect = pygame.Rect(
        BOARD_OFFSET_X + x * CELL_SIZE,
        BOARD_OFFSET_Y + y * CELL_SIZE,
        CELL_SIZE - 1, CELL_SIZE - 1
    )
    cell_color = COLORS[color]
    if alpha < 255:
        s = pygame.Surface((CELL_SIZE - 1, CELL_SIZE - 1), pygame.SRCALPHA)
        s.fill((*cell_color, alpha))
        surface.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surface, cell_color, rect)
        # ハイライト（左上）
        pygame.draw.line(surface, tuple(min(c + 80, 255) for c in cell_color),
                         rect.topleft, (rect.right - 1, rect.top), 2)
        pygame.draw.line(surface, tuple(min(c + 80, 255) for c in cell_color),
                         rect.topleft, (rect.left, rect.bottom - 1), 2)
        # シャドウ（右下）
        pygame.draw.line(surface, tuple(max(c - 80, 0) for c in cell_color),
                         (rect.right - 1, rect.top), rect.bottomright, 2)
        pygame.draw.line(surface, tuple(max(c - 80, 0) for c in cell_color),
                         (rect.left, rect.bottom - 1), rect.bottomright, 2)


def draw_next_piece(surface, piece, font):
    """次のピースを描画"""
    label = font.render("NEXT", True, WHITE)
    nx = BOARD_OFFSET_X + BOARD_WIDTH * CELL_SIZE + 20
    ny = BOARD_OFFSET_Y + 10
    surface.blit(label, (nx, ny))

    shape = piece.shape[piece.rotation]
    for row_i, row in enumerate(shape):
        for col_i, val in enumerate(row):
            if val:
                rect = pygame.Rect(
                    nx + col_i * 25,
                    ny + 30 + row_i * 25,
                    24, 24
                )
                pygame.draw.rect(surface, COLORS[piece.color], rect)


def draw_board(surface, game, font_small):
    """ボード全体を描画"""
    # ボード背景
    board_rect = pygame.Rect(
        BOARD_OFFSET_X - 2, BOARD_OFFSET_Y - 2,
        BOARD_WIDTH * CELL_SIZE + 4, BOARD_HEIGHT * CELL_SIZE + 4
    )
    pygame.draw.rect(surface, BORDER_COLOR, board_rect, 2)

    # グリッド
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            rect = pygame.Rect(
                BOARD_OFFSET_X + x * CELL_SIZE,
                BOARD_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE - 1, CELL_SIZE - 1
            )
            if game.board[y][x]:
                draw_cell(surface, x, y, game.board[y][x])
            else:
                pygame.draw.rect(surface, DARK_GRAY, rect)

    # ゴーストピース
    for gx, gy in game.get_ghost_cells():
        if gy >= 0:
            draw_cell(surface, gx, gy, game.current.color, alpha=60)

    # 現在のピース
    for cx, cy in game.current.get_cells():
        if cy >= 0:
            draw_cell(surface, cx, cy, game.current.color)

    # スコア表示
    nx = BOARD_OFFSET_X + BOARD_WIDTH * CELL_SIZE + 20
    score_y = BOARD_OFFSET_Y + 160

    for label, value in [("SCORE", game.score), ("LEVEL", game.level), ("LINES", game.lines_cleared)]:
        lbl = font_small.render(label, True, GRAY)
        val = font_small.render(str(value), True, WHITE)
        surface.blit(lbl, (nx, score_y))
        surface.blit(val, (nx, score_y + 22))
        score_y += 70


def draw_overlay(surface, text, font_large, font_small=None, sub_text=None):
    """ゲームオーバー・ポーズ画面"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    txt = font_large.render(text, True, WHITE)
    surface.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))

    if sub_text and font_small:
        sub = font_small.render(sub_text, True, GRAY)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("テトリス")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("monospace", 40, bold=True)
    font_small = pygame.font.SysFont("monospace", 20)

    game = TetrisGame()
    das_delay = 150   # 押し続けてからの遅延（ms）
    das_repeat = 50   # 繰り返し間隔（ms）
    das_timer = {'left': 0, 'right': 0}
    das_held = {'left': False, 'right': False}

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if game.game_over:
                    if event.key == pygame.K_r:
                        game = TetrisGame()
                    continue

                if event.key == pygame.K_p:
                    game.paused = not game.paused

                if game.paused:
                    continue

                if event.key == pygame.K_LEFT:
                    game.move(-1, 0)
                    das_held['left'] = True
                    das_timer['left'] = 0
                elif event.key == pygame.K_RIGHT:
                    game.move(1, 0)
                    das_held['right'] = True
                    das_timer['right'] = 0
                elif event.key == pygame.K_DOWN:
                    game.move(0, 1)
                    game.score += 1
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    game.rotate(1)
                elif event.key == pygame.K_z:
                    game.rotate(-1)
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    das_held['left'] = False
                elif event.key == pygame.K_RIGHT:
                    das_held['right'] = False

        # DAS（Delayed Auto Shift）処理
        if not game.game_over and not game.paused:
            for direction, dx in [('left', -1), ('right', 1)]:
                if das_held[direction]:
                    das_timer[direction] += dt
                    threshold = das_delay if das_timer[direction] < das_delay + das_repeat else das_repeat
                    if das_timer[direction] >= threshold:
                        game.move(dx, 0)
                        das_timer[direction] = das_delay  # リピート開始後はリピート間隔で

        game.update(dt)

        # 描画
        screen.fill(BLACK)
        draw_board(screen, game, font_small)
        draw_next_piece(screen, game.next, font_small)

        if game.paused and not game.game_over:
            draw_overlay(screen, "PAUSE", font_large, font_small, "P: 再開")
        elif game.game_over:
            draw_overlay(screen, "GAME OVER", font_large, font_small, "R: リスタート")

        pygame.display.flip()


if __name__ == "__main__":
    main()
