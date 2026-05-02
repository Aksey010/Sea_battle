import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Tuple, Dict

# Стандартный набор кораблей
SHIP_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
GRID_SIZE = 10


class CellState(Enum):
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3
    DESTROYED = 4


class ShotResult(Enum):
    MISS = 0
    HIT = 1
    DESTROYED = 2
    ALREADY_SHOT = 3


class Cell:
    """Клетка игрового поля."""
    def __init__(self):
        self.state = CellState.EMPTY
        self.ship_id: Optional[int] = None


class Board:
    """Игровое поле, управляющее клетками и кораблями."""
    def __init__(self, size: int = GRID_SIZE):
        self.size = size
        self.cells: List[List[Cell]] = [[Cell() for _ in range(size)] for _ in range(size)]
        self.ships: Dict[int, List[Tuple[int, int]]] = {}
        self._next_ship_id = 1

    def is_valid_coord(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def get_cell(self, row: int, col: int) -> Cell:
        if not self.is_valid_coord(row, col):
            raise IndexError(f"Координаты ({row}, {col}) вне границ поля")
        return self.cells[row][col]

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Возвращает координаты всех 8 соседей в границах поля."""
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if self.is_valid_coord(nr, nc):
                    neighbors.append((nr, nc))
        return neighbors

    def get_orthogonal_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Возвращает координаты 4 ортогональных соседей."""
        neighbors = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = row + dr, col + dc
            if self.is_valid_coord(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def is_ship_cell(self, row: int, col: int) -> bool:
        return self.get_cell(row, col).state == CellState.SHIP

    def all_ships_destroyed(self) -> bool:
        """Проверяет, уничтожены ли все корабли на доске."""
        for ship_cells in self.ships.values():
            for r, c in ship_cells:
                if self.cells[r][c].state != CellState.DESTROYED:
                    return False
        return True

    def can_place_ship(self, row: int, col: int, size: int, horizontal: bool) -> bool:
        """Проверяет возможность размещения корабля без пересечений и касаний."""
        # Проверка границ
        if horizontal:
            if col + size > self.size:
                return False
            cells_to_place = [(row, col + i) for i in range(size)]
        else:
            if row + size > self.size:
                return False
            cells_to_place = [(row + i, col) for i in range(size)]

        # Проверка клеток и их соседей
        for r, c in cells_to_place:
            if not self.is_valid_coord(r, c):
                return False
            if self.get_cell(r, c).state != CellState.EMPTY:
                return False
            # Проверка всех 8 соседей
            for nr, nc in self.get_neighbors(r, c):
                if self.is_ship_cell(nr, nc):
                    return False
        return True

    def place_ship(self, row: int, col: int, size: int, horizontal: bool) -> int:
        """Размещает корабль. Возвращает ship_id. Выбрасывает ValueError, если размещение невозможно."""
        if not self.can_place_ship(row, col, size, horizontal):
            raise ValueError(f"Нельзя разместить корабль размером {size} в ({row}, {col}) горизонтально={horizontal}")

        ship_id = self._next_ship_id
        self._next_ship_id += 1
        ship_cells = []

        if horizontal:
            for i in range(size):
                r, c = row, col + i
                self.cells[r][c].state = CellState.SHIP
                self.cells[r][c].ship_id = ship_id
                ship_cells.append((r, c))
        else:
            for i in range(size):
                r, c = row + i, col
                self.cells[r][c].state = CellState.SHIP
                self.cells[r][c].ship_id = ship_id
                ship_cells.append((r, c))

        self.ships[ship_id] = ship_cells
        return ship_id

    def remove_all_ships(self):
        """Очищает все корабли с доски."""
        self.cells = [[Cell() for _ in range(self.size)] for _ in range(self.size)]
        self.ships.clear()
        self._next_ship_id = 1

    def get_ship_cells(self, ship_id: int) -> List[Tuple[int, int]]:
        return self.ships.get(ship_id, [])

    def receive_shot(self, row: int, col: int) -> ShotResult:
        """Обрабатывает выстрел по клетке. Возвращает результат."""
        cell = self.get_cell(row, col)

        # Уже стреляли
        if cell.state in (CellState.HIT, CellState.MISS, CellState.DESTROYED):
            return ShotResult.ALREADY_SHOT

        # Промах
        if cell.state == CellState.EMPTY:
            cell.state = CellState.MISS
            return ShotResult.MISS

        # Попадание
        if cell.state == CellState.SHIP:
            cell.state = CellState.HIT
            ship_id = cell.ship_id
            # Проверка уничтожения корабля
            ship_cells = self.ships[ship_id]
            if all(self.cells[r][c].state == CellState.HIT for r, c in ship_cells):
                # Корабль уничтожен
                for r, c in ship_cells:
                    self.cells[r][c].state = CellState.DESTROYED
                    # Автоокружение - помечаем всех соседей как MISS
                    for nr, nc in self.get_neighbors(r, c):
                        if self.cells[nr][nc].state == CellState.EMPTY:
                            self.cells[nr][nc].state = CellState.MISS
                return ShotResult.DESTROYED
            return ShotResult.HIT

        return ShotResult.ALREADY_SHOT  # fallback

    def get_available_cells(self) -> List[Tuple[int, int]]:
        """Возвращает клетки, по которым еще не стреляли (EMPTY или SHIP)."""
        available = []
        for r in range(self.size):
            for c in range(self.size):
                if self.cells[r][c].state in (CellState.EMPTY, CellState.SHIP):
                    available.append((r, c))
        return available


# ------------------ Стратегии расстановки ------------------
class ShipPlacementStrategy(ABC):
    @abstractmethod
    def place_ships(self, board: Board) -> None:
        """Размещает все корабли из SHIP_SIZES на доске. Должен очистить доску перед размещением."""
        pass


class RandomPlacement(ShipPlacementStrategy):
    def place_ships(self, board: Board) -> None:
        board.remove_all_ships()
        for size in SHIP_SIZES:
            placed = False
            for _ in range(1000):
                row = random.randint(0, board.size - 1)
                col = random.randint(0, board.size - 1)
                horizontal = random.choice([True, False])
                if board.can_place_ship(row, col, size, horizontal):
                    board.place_ship(row, col, size, horizontal)
                    placed = True
                    break
            if not placed:
                raise RuntimeError(f"Не удалось разместить корабль размера {size}")


class EdgePlacement(ShipPlacementStrategy):
    """70% вероятность разместить первую палубу на краю доски."""
    def place_ships(self, board: Board) -> None:
        board.remove_all_ships()
        for size in SHIP_SIZES:
            placed = False
            for _ in range(1000):
                if random.random() < 0.7:
                    # Выбираем крайние клетки
                    edge_cells = []
                    for c in range(board.size):
                        edge_cells.append((0, c))
                        edge_cells.append((board.size - 1, c))
                    for r in range(1, board.size - 1):
                        edge_cells.append((r, 0))
                        edge_cells.append((r, board.size - 1))
                    row, col = random.choice(edge_cells)
                else:
                    row = random.randint(0, board.size - 1)
                    col = random.randint(0, board.size - 1)

                horizontal = random.choice([True, False])
                if board.can_place_ship(row, col, size, horizontal):
                    board.place_ship(row, col, size, horizontal)
                    placed = True
                    break
            if not placed:
                raise RuntimeError(f"Не удалось разместить корабль размера {size}")


class ClusteredPlacement(ShipPlacementStrategy):
    """80% вероятность разместить новый корабль рядом с уже существующими."""
    def place_ships(self, board: Board) -> None:
        board.remove_all_ships()
        occupied_cells = []  # клетки, занятые кораблями

        for size in SHIP_SIZES:
            placed = False
            for _ in range(1000):
                if occupied_cells and random.random() < 0.8:
                    # Выбираем случайную занятую клетку и пробуем рядом
                    base_r, base_c = random.choice(occupied_cells)
                    # Генерируем кандидатов в радиусе 3 клеток
                    candidates = []
                    for dr in range(-3, 4):
                        for dc in range(-3, 4):
                            nr, nc = base_r + dr, base_c + dc
                            if board.is_valid_coord(nr, nc):
                                candidates.append((nr, nc))
                    random.shuffle(candidates)
                    for row, col in candidates:
                        horizontal = random.choice([True, False])
                        if board.can_place_ship(row, col, size, horizontal):
                            board.place_ship(row, col, size, horizontal)
                            placed = True
                            # Обновляем список занятых клеток
                            new_cells = board.get_ship_cells(board._next_ship_id - 1)
                            occupied_cells.extend(new_cells)
                            break
                else:
                    row = random.randint(0, board.size - 1)
                    col = random.randint(0, board.size - 1)
                    horizontal = random.choice([True, False])
                    if board.can_place_ship(row, col, size, horizontal):
                        board.place_ship(row, col, size, horizontal)
                        placed = True
                        new_cells = board.get_ship_cells(board._next_ship_id - 1)
                        occupied_cells.extend(new_cells)
                        break

                if placed:
                    break

            if not placed:
                raise RuntimeError(f"Не удалось разместить корабль размера {size}")


# ------------------ Стратегии стрельбы ------------------
class ShootingStrategy(ABC):
    @abstractmethod
    def choose_target(self, board: Board) -> Tuple[int, int]:
        """Выбирает цель на доске противника. Должна возвращать только доступные клетки."""
        pass


class RandomShooting(ShootingStrategy):
    def choose_target(self, board: Board) -> Tuple[int, int]:
        available = board.get_available_cells()
        if not available:
            raise RuntimeError("Нет доступных клеток для выстрела")
        return random.choice(available)


class HuntAndTarget(ShootingStrategy):
    """Стратегия охоты и добивания с шахматным паттерном."""
    def __init__(self):
        self.target_queue: List[Tuple[int, int]] = []
        self.hunt_mode = True
        self.hunt_parity = random.randint(0, 1)  # фиксированная четность на партию
        self.hunt_cells: List[Tuple[int, int]] = []
        self.last_hit = None

    def choose_target(self, board: Board) -> Tuple[int, int]:
        available = set(board.get_available_cells())

        # Очистка очереди от недоступных клеток
        self.target_queue = [cell for cell in self.target_queue if cell in available]

        # Если есть очередь добивания
        if self.target_queue:
            return self.target_queue.pop(0)

        # Режим охоты - шахматный паттерн
        if not self.hunt_cells:
            all_cells = [(r, c) for r in range(board.size) for c in range(board.size)
                        if (r + c) % 2 == self.hunt_parity]
            random.shuffle(all_cells)
            self.hunt_cells = all_cells

        # Берем следующую клетку из шахматного паттерна, которая доступна
        while self.hunt_cells:
            candidate = self.hunt_cells.pop()
            if candidate in available:
                return candidate

        # Если шахматные клетки кончились, стреляем по оставшимся
        remaining = list(available)
        if not remaining:
            raise RuntimeError("Нет доступных клеток")
        return random.choice(remaining)

    def notify_result(self, row: int, col: int, result: ShotResult):
        """Обновляет состояние стратегии на основе результата выстрела."""
        if result == ShotResult.HIT:
            self.last_hit = (row, col)
            # Добавляем ортогональных соседей в начало очереди
            board = None  # Нужна доска? - передаем через параметры
        elif result == ShotResult.DESTROYED:
            self.target_queue.clear()
        # При MISS ничего не делаем (клетка удаляется при следующем выборе)


class ProbabilityShooting(ShootingStrategy):
    """Стрельба на основе вероятностной карты с учетом оставшихся кораблей."""
    def __init__(self):
        self._remaining_sizes = list(SHIP_SIZES)

    def choose_target(self, board: Board) -> Tuple[int, int]:
        available = board.get_available_cells()
        if not available:
            raise RuntimeError("Нет доступных клеток")

        # Определяем оставшиеся корабли
        self._update_remaining_sizes(board)

        # Строим вероятностную карту
        weight_map = [[0] * board.size for _ in range(board.size)]

        for size in set(self._remaining_sizes):
            # Горизонтальные позиции
            for r in range(board.size):
                for c in range(board.size - size + 1):
                    if self._can_place_prob(board, r, c, size, True):
                        for i in range(size):
                            if (r, c + i) in available:
                                weight_map[r][c + i] += 1

            # Вертикальные позиции
            for r in range(board.size - size + 1):
                for c in range(board.size):
                    if self._can_place_prob(board, r, c, size, False):
                        for i in range(size):
                            if (r + i, c) in available:
                                weight_map[r + i][c] += 1

        # Выбираем клетку с максимальным весом
        max_weight = -1
        best_cell = available[0]
        for r, c in available:
            if weight_map[r][c] > max_weight:
                max_weight = weight_map[r][c]
                best_cell = (r, c)

        return best_cell

    def _update_remaining_sizes(self, board: Board):
        """Обновляет список оставшихся размеров кораблей."""
        destroyed_sizes = []
        for ship_id, cells in board.ships.items():
            if all(board.cells[r][c].state == CellState.DESTROYED for r, c in cells):
                destroyed_sizes.append(len(cells))

        remaining = list(SHIP_SIZES)
        for size in destroyed_sizes:
            if size in remaining:
                remaining.remove(size)
        self._remaining_sizes = remaining

    def _can_place_prob(self, board: Board, row: int, col: int, size: int, horizontal: bool) -> bool:
        """Проверяет, может ли корабль разместиться гипотетически (без учета касаний, только по попаданиям/промахам)."""
        if horizontal:
            if col + size > board.size:
                return False
            cells_to_check = [(row, col + i) for i in range(size)]
        else:
            if row + size > board.size:
                return False
            cells_to_check = [(row + i, col) for i in range(size)]

        for r, c in cells_to_check:
            cell = board.cells[r][c]
            # Клетка не должна быть промахом или уничтоженным кораблем
            if cell.state in (CellState.MISS, CellState.DESTROYED):
                return False
            # Если клетка подбита (HIT), она должна быть частью этого же корабля
            if cell.state == CellState.HIT:
                # Упрощенно: разрешаем, если это может быть тот же корабль
                pass
        return True


# ------------------ Игровой движок ------------------
class GameEngine:
    """Управляет игровым процессом."""
    def __init__(self, player_strategy: Optional[ShootingStrategy] = None):
        self.board_player = Board()
        self.board_opponent = Board()
        self.player_turn = True
        self.game_over = False
        self.winner: Optional[str] = None
        self.player_strategy = player_strategy
        self.opponent_strategy: Optional[ShootingStrategy] = None

        # Статистика
        self.total_shots_player = 0
        self.total_shots_opponent = 0
        self.hits_player = 0
        self.hits_opponent = 0
        self.misses_player = 0
        self.misses_opponent = 0

    def setup_player_board(self, strategy: ShipPlacementStrategy):
        strategy.place_ships(self.board_player)

    def setup_opponent_board(self, strategy: ShipPlacementStrategy):
        strategy.place_ships(self.board_opponent)

    def setup_opponent_strategy(self, strategy: ShootingStrategy):
        self.opponent_strategy = strategy

    def player_shoot(self, row: int, col: int) -> ShotResult:
        """Выстрел игрока по полю противника."""
        if self.game_over:
            return ShotResult.ALREADY_SHOT

        result = self.board_opponent.receive_shot(row, col)
        self.total_shots_player += 1

        if result == ShotResult.HIT or result == ShotResult.DESTROYED:
            self.hits_player += 1
            if result == ShotResult.DESTROYED:
                if hasattr(self.player_strategy, 'notify_result'):
                    self.player_strategy.notify_result(row, col, result)
            if self.check_victory():
                return result
            return result  # Ход остается
        elif result == ShotResult.MISS:
            self.misses_player += 1
            self.player_turn = False
            return result
        else:  # ALREADY_SHOT
            return result

    def opponent_shoot(self) -> ShotResult:
        """Выстрел противника по полю игрока."""
        if self.game_over or not self.opponent_strategy:
            return ShotResult.ALREADY_SHOT

        row, col = self.opponent_strategy.choose_target(self.board_player)
        result = self.board_player.receive_shot(row, col)
        self.total_shots_opponent += 1

        if result == ShotResult.HIT or result == ShotResult.DESTROYED:
            self.hits_opponent += 1
            if result == ShotResult.DESTROYED:
                if hasattr(self.opponent_strategy, 'notify_result'):
                    self.opponent_strategy.notify_result(row, col, result)
                if self.check_victory():
                    return result
            return result
        elif result == ShotResult.MISS:
            self.misses_opponent += 1
            self.player_turn = True
            return result
        else:
            return result

    def check_victory(self) -> bool:
        """Проверяет условие победы."""
        if self.board_opponent.all_ships_destroyed():
            self.game_over = True
            self.winner = "player"
            return True
        if self.board_player.all_ships_destroyed():
            self.game_over = True
            self.winner = "opponent"
            return True
        return False

    def reset(self):
        self.board_player = Board()
        self.board_opponent = Board()
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.total_shots_player = 0
        self.total_shots_opponent = 0
        self.hits_player = 0
        self.hits_opponent = 0
        self.misses_player = 0
        self.misses_opponent = 0