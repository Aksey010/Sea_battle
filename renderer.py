import pygame
from game_core import Board, CellState

# Константы отрисовки
CELL_SIZE = 40
GRID_SIZE = 10
MARGIN = 50

# Цвета
WATER = (0, 105, 148)
SHIP_COLOR = (100, 100, 100)
MISS = (255, 255, 255)
HIT = (255, 100, 100)
DESTROYED = (150, 0, 0)
GRID_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
PANEL_BG = (30, 30, 50)


class BoardRenderer:
    """Отрисовщик игрового поля."""
    def __init__(self, surface: pygame.Surface, top_left_x: int, top_left_y: int, board: Board, is_own_board: bool):
        self.surface = surface
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.board = board
        self.is_own_board = is_own_board
        self.cell_size = CELL_SIZE
        self.font = pygame.font.Font(None, 20)

    def draw(self):
        """Отрисовывает поле и все клетки."""
        # Отрисовка сетки и клеток
        for row in range(self.board.size):
            for col in range(self.board.size):
                x = self.top_left_x + col * self.cell_size
                y = self.top_left_y + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                cell = self.board.cells[row][col]
                color = WATER

                if self.is_own_board:
                    # Показываем все детали своего поля
                    if cell.state == CellState.SHIP:
                        color = SHIP_COLOR
                    elif cell.state == CellState.HIT:
                        color = HIT
                    elif cell.state == CellState.MISS:
                        color = MISS
                    elif cell.state == CellState.DESTROYED:
                        color = DESTROYED
                else:
                    # Скрываем корабли противника
                    if cell.state == CellState.HIT:
                        color = HIT
                    elif cell.state == CellState.MISS:
                        color = MISS
                    elif cell.state == CellState.DESTROYED:
                        color = DESTROYED

                pygame.draw.rect(self.surface, color, rect)
                pygame.draw.rect(self.surface, GRID_COLOR, rect, 1)

        # Подписи координат
        for i in range(self.board.size):
            # Буквы для столбцов
            label = self.font.render(chr(65 + i), True, TEXT_COLOR)
            x = self.top_left_x + i * self.cell_size + self.cell_size // 2 - label.get_width() // 2
            y = self.top_left_y - 20
            self.surface.blit(label, (x, y))

            # Цифры для строк
            label = self.font.render(str(i + 1), True, TEXT_COLOR)
            x = self.top_left_x - 25
            y = self.top_left_y + i * self.cell_size + self.cell_size // 2 - label.get_height() // 2
            self.surface.blit(label, (x, y))

    def get_cell_from_click(self, mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
        """Возвращает координаты клетки по позиции мыши или None."""
        col = (mouse_x - self.top_left_x) // self.cell_size
        row = (mouse_y - self.top_left_y) // self.cell_size

        if 0 <= row < self.board.size and 0 <= col < self.board.size:
            return row, col
        return None