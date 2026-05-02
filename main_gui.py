import pygame
import sys
import time
from game_core import (
    GameEngine, Board, CellState, ShotResult,
    RandomPlacement, EdgePlacement, ClusteredPlacement,
    RandomShooting, HuntAndTarget, ProbabilityShooting,
    SHIP_SIZES
)
from renderer import BoardRenderer, CELL_SIZE, GRID_SIZE, MARGIN, PANEL_BG, TEXT_COLOR
import random

# Размеры окна
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 620

# Позиции полей
PLAYER_BOARD_X = 30
PLAYER_BOARD_Y = 50
OPPONENT_BOARD_X = 480
OPPONENT_BOARD_Y = 50

# Позиция и размеры панели статуса
PANEL_X = 910
PANEL_Y = 50
PANEL_WIDTH = 170
PANEL_HEIGHT = 420

# Область для надписей и кнопок под полями
INFO_Y_START = 475
BUTTONS_Y = 540

# Цвета
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
BUTTON_TEXT_COLOR = (255, 255, 255)
PANEL_BORDER = (100, 100, 140)


class Button:
    """Простая кнопка для GUI."""

    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, surface, font):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()
                return True
        return False


class SeaBattleGUI:
    """Главный класс GUI игры Морской бой."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Морской бой")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.medium_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.tiny_font = pygame.font.Font(None, 18)

        self.engine = GameEngine()
        self.placement_strategy = None
        self.game_state = "placement"  # placement, playing, victory
        self.manual_placement_index = 0
        self.manual_horizontal = True
        self.message = "Выберите стратегию расстановки кораблей"
        self.opponent_strategy = None

        # Таймер для хода бота
        self.bot_timer = 0
        self.bot_shot_pending = False
        self.BOT_DELAY = 500

    def run(self):
        """Основной цикл игры."""
        running = True
        while running:
            dt = self.clock.tick(60)

            self.screen.fill(PANEL_BG)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            # Обработка хода бота с задержкой
            if self.bot_shot_pending and self.game_state == "playing":
                self.bot_timer += dt
                if self.bot_timer >= self.BOT_DELAY:
                    self.bot_timer = 0
                    self.execute_bot_shot()

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def handle_event(self, event):
        """Обработка событий."""
        if self.game_state == "placement":
            self.handle_placement_event(event)
        elif self.game_state == "playing":
            self.handle_playing_event(event)
        elif self.game_state == "victory":
            self.handle_victory_event(event)

    def handle_placement_event(self, event):
        """Обработка событий на экране расстановки."""
        if event.type == pygame.KEYDOWN:
            if self.placement_strategy == "manual" and self.manual_placement_index < len(SHIP_SIZES):
                if event.key == pygame.K_h:
                    self.manual_horizontal = True
                    self.message = f"Горизонтальная. Корабль {SHIP_SIZES[self.manual_placement_index]}-палубный"
                elif event.key == pygame.K_v:
                    self.manual_horizontal = False
                    self.message = f"Вертикальная. Корабль {SHIP_SIZES[self.manual_placement_index]}-палубный"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Кнопки стратегий
            buttons_config = [
                (30, BUTTONS_Y, 150, 40, "Случайно", "random"),
                (200, BUTTONS_Y, 150, 40, "К краям", "edge"),
                (370, BUTTONS_Y, 150, 40, "Кластер", "cluster"),
                (540, BUTTONS_Y, 150, 40, "Вручную", "manual"),
                (710, BUTTONS_Y, 150, 40, "Готов", "ready")
            ]

            for x, y, w, h, text, action in buttons_config:
                if pygame.Rect(x, y, w, h).collidepoint(mouse_pos):
                    if action == "random":
                        self.placement_strategy = "random"
                        RandomPlacement().place_ships(self.engine.board_player)
                        self.message = "Корабли расставлены случайно. Нажмите 'Готов'"
                    elif action == "edge":
                        self.placement_strategy = "edge"
                        EdgePlacement().place_ships(self.engine.board_player)
                        self.message = "Корабли расставлены к краям. Нажмите 'Готов'"
                    elif action == "cluster":
                        self.placement_strategy = "cluster"
                        ClusteredPlacement().place_ships(self.engine.board_player)
                        self.message = "Корабли расставлены кластером. Нажмите 'Готов'"
                    elif action == "manual":
                        self.placement_strategy = "manual"
                        self.manual_placement_index = 0
                        self.manual_horizontal = True
                        self.engine.board_player.remove_all_ships()
                        self.message = f"Разместите {SHIP_SIZES[0]}-палубный корабль (H/V)"
                    elif action == "ready" and self.placement_strategy:
                        self.start_game()
                    break

            # Ручная расстановка
            if self.placement_strategy == "manual":
                renderer = BoardRenderer(self.screen, PLAYER_BOARD_X, PLAYER_BOARD_Y, self.engine.board_player, True)
                cell = renderer.get_cell_from_click(*mouse_pos)
                if cell and self.manual_placement_index < len(SHIP_SIZES):
                    row, col = cell
                    size = SHIP_SIZES[self.manual_placement_index]
                    try:
                        self.engine.board_player.place_ship(row, col, size, self.manual_horizontal)
                        self.manual_placement_index += 1
                        if self.manual_placement_index < len(SHIP_SIZES):
                            self.message = f"Разместите {SHIP_SIZES[self.manual_placement_index]}-палубный (H/V)"
                        else:
                            self.message = "Все корабли расставлены! Нажмите 'Готов'"
                    except ValueError:
                        self.message = "Нельзя разместить здесь! Другая позиция"

    def handle_playing_event(self, event):
        """Обработка событий во время игры."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.engine.player_turn and not self.engine.game_over and not self.bot_shot_pending:
                renderer = BoardRenderer(self.screen, OPPONENT_BOARD_X, OPPONENT_BOARD_Y, self.engine.board_opponent,
                                         False)
                cell = renderer.get_cell_from_click(*event.pos)
                if cell:
                    row, col = cell
                    result = self.engine.player_shoot(row, col)

                    if result == ShotResult.ALREADY_SHOT:
                        self.message = "Сюда уже стреляли!"
                        return

                    self.update_message(result, "Вы")

                    if self.engine.game_over:
                        self.handle_game_over()
                    elif result == ShotResult.MISS:
                        self.start_bot_turn()

    def start_bot_turn(self):
        """Запускает ход бота с задержкой."""
        self.bot_shot_pending = True
        self.bot_timer = 0

    def execute_bot_shot(self):
        """Выполняет один выстрел бота."""
        if self.engine.game_over or self.engine.player_turn:
            self.bot_shot_pending = False
            return

        try:
            result = self.engine.opponent_shoot()
            self.update_message(result, "Бот")

            if self.engine.game_over:
                self.handle_game_over()
            elif result == ShotResult.MISS:
                self.bot_shot_pending = False
                self.message = "Ваш ход!"
            elif result == ShotResult.ALREADY_SHOT:
                self.bot_shot_pending = False
            else:
                # Бот попал - продолжает стрелять
                self.bot_shot_pending = True
                self.bot_timer = 0

        except Exception as e:
            print(f"Ошибка при выстреле бота: {e}")
            self.bot_shot_pending = False
            self.message = "Ваш ход!"

    def handle_game_over(self):
        """Обрабатывает конец игры."""
        self.game_state = "victory"
        self.bot_shot_pending = False
        winner_text = "Вы" if self.engine.winner == "player" else "Компьютер"
        self.message = f"Победитель: {winner_text}!"

    def handle_victory_event(self, event):
        """Обработка событий на экране победы."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, 300, 150, 40)
            if button_rect.collidepoint(event.pos):
                self.reset_game()

            exit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, 360, 150, 40)
            if exit_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    def start_game(self):
        """Начинает игру."""
        self.opponent_strategy = HuntAndTarget()

        self.engine.setup_opponent_board(RandomPlacement())
        self.engine.setup_opponent_strategy(self.opponent_strategy)
        self.engine.player_turn = True
        self.game_state = "playing"
        self.message = "Ваш ход!"
        self.bot_shot_pending = False
        self.bot_timer = 0

    def update_message(self, result, who):
        """Обновляет сообщение на основе результата выстрела."""
        if self.engine.game_over:
            return

        if result == ShotResult.MISS:
            self.message = f"{who}: Промах!"
        elif result == ShotResult.HIT:
            self.message = f"{who}: Попадание!"
        elif result == ShotResult.DESTROYED:
            self.message = f"{who}: Корабль уничтожен!"
        elif result == ShotResult.ALREADY_SHOT:
            self.message = "Сюда уже стреляли!"

    def reset_game(self):
        """Сбрасывает игру."""
        self.engine.reset()
        self.placement_strategy = None
        self.game_state = "placement"
        self.manual_placement_index = 0
        self.manual_horizontal = True
        self.message = "Выберите стратегию расстановки кораблей"
        self.bot_shot_pending = False
        self.bot_timer = 0
        self.opponent_strategy = None

    def draw(self):
        """Отрисовка текущего состояния."""
        # Заголовок
        title = self.font.render("Морской бой", True, TEXT_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 8))

        if self.game_state == "placement":
            self.draw_placement_screen()
        elif self.game_state == "playing":
            self.draw_playing_screen()
        elif self.game_state == "victory":
            self.draw_victory_screen()

    def draw_placement_screen(self):
        """Отрисовка экрана расстановки."""
        # Поле игрока
        renderer = BoardRenderer(self.screen, PLAYER_BOARD_X, PLAYER_BOARD_Y, self.engine.board_player, True)
        renderer.draw()

        # Подпись под полем игрока
        label = self.medium_font.render("Ваше поле", True, TEXT_COLOR)
        label_x = PLAYER_BOARD_X + (GRID_SIZE * CELL_SIZE) // 2 - label.get_width() // 2
        label_y = PLAYER_BOARD_Y + GRID_SIZE * CELL_SIZE + 10
        self.screen.blit(label, (label_x, label_y))

        # Инструкция - теперь под подписью "Ваше поле"
        info_y = label_y + 30
        instruction = self.medium_font.render(self.message, True, (255, 255, 150))
        # Центрируем инструкцию под полем
        instr_x = PLAYER_BOARD_X + (GRID_SIZE * CELL_SIZE) // 2 - instruction.get_width() // 2
        # Если инструкция выходит за пределы, смещаем левее
        if instr_x < 10:
            instr_x = 10
        self.screen.blit(instruction, (instr_x, info_y))

        # Подсказка по ориентации для ручной расстановки
        if self.placement_strategy == "manual" and self.manual_placement_index < len(SHIP_SIZES):
            orient = "Горизонтальная" if self.manual_horizontal else "Вертикальная"
            hint = self.small_font.render(f"Ориентация: {orient} (H/V для смены)", True, (200, 200, 100))
            hint_x = PLAYER_BOARD_X + (GRID_SIZE * CELL_SIZE) // 2 - hint.get_width() // 2
            if hint_x < 10:
                hint_x = 10
            self.screen.blit(hint, (hint_x, info_y + 25))

        # Кнопки стратегий
        buttons = [
            (30, BUTTONS_Y, 150, 40, "Случайно"),
            (200, BUTTONS_Y, 150, 40, "К краям"),
            (370, BUTTONS_Y, 150, 40, "Кластер"),
            (540, BUTTONS_Y, 150, 40, "Вручную"),
            (710, BUTTONS_Y, 150, 40, "Готов")
        ]
        for x, y, w, h, text in buttons:
            rect = pygame.Rect(x, y, w, h)
            color = BUTTON_HOVER_COLOR if rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            text_surf = self.small_font.render(text, True, BUTTON_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

    def draw_playing_screen(self):
        """Отрисовка игрового экрана."""
        # Поле игрока (слева)
        player_renderer = BoardRenderer(self.screen, PLAYER_BOARD_X, PLAYER_BOARD_Y, self.engine.board_player, True)
        player_renderer.draw()

        # Подпись под полем игрока
        label = self.medium_font.render("Ваше поле", True, TEXT_COLOR)
        label_x = PLAYER_BOARD_X + (GRID_SIZE * CELL_SIZE) // 2 - label.get_width() // 2
        label_y = PLAYER_BOARD_Y + GRID_SIZE * CELL_SIZE + 10
        self.screen.blit(label, (label_x, label_y))

        # Поле противника (по центру)
        opponent_renderer = BoardRenderer(self.screen, OPPONENT_BOARD_X, OPPONENT_BOARD_Y, self.engine.board_opponent,
                                          False)
        opponent_renderer.draw()

        # Подпись под полем противника
        label = self.medium_font.render("Поле противника", True, TEXT_COLOR)
        label_x = OPPONENT_BOARD_X + (GRID_SIZE * CELL_SIZE) // 2 - label.get_width() // 2
        label_y = OPPONENT_BOARD_Y + GRID_SIZE * CELL_SIZE + 10
        self.screen.blit(label, (label_x, label_y))

        # Панель статуса (справа)
        self.draw_status_panel()

    def draw_status_panel(self):
        """Отрисовка панели статуса с проверкой границ."""
        # Фон панели
        panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel_rect, 2)

        # Отступы внутри панели
        margin = 8
        content_x = PANEL_X + margin
        content_y = PANEL_Y + margin
        content_width = PANEL_WIDTH - 2 * margin

        # Заголовок панели
        title = self.small_font.render("СТАТУС", True, TEXT_COLOR)
        title_x = PANEL_X + (PANEL_WIDTH - title.get_width()) // 2
        self.screen.blit(title, (title_x, content_y))
        content_y += title.get_height() + 8

        # Разделительная линия
        pygame.draw.line(self.screen, PANEL_BORDER,
                         (content_x, content_y),
                         (content_x + content_width, content_y), 1)
        content_y += 8

        # Индикатор хода
        if self.engine.player_turn:
            turn_text = "Ваш ход"
            turn_color = (100, 255, 100)
        else:
            turn_text = "Ход бота"
            turn_color = (255, 150, 150)

        turn_surf = self.medium_font.render(turn_text, True, turn_color)
        turn_x = PANEL_X + (PANEL_WIDTH - turn_surf.get_width()) // 2

        if turn_x + turn_surf.get_width() > PANEL_X + PANEL_WIDTH:
            turn_surf = self.small_font.render(turn_text, True, turn_color)
            turn_x = PANEL_X + (PANEL_WIDTH - turn_surf.get_width()) // 2

        self.screen.blit(turn_surf, (turn_x, content_y))
        content_y += turn_surf.get_height() + 12

        # Статистика
        stats = [
            ("Ходов:", f"{self.engine.total_shots_player + self.engine.total_shots_opponent}"),
            ("", ""),
            ("-- Вы --", ""),
            ("Попаданий:", f"{self.engine.hits_player}"),
            ("Промахов:", f"{self.engine.misses_player}"),
            ("Точность:", f"{self._calc_accuracy(self.engine.hits_player, self.engine.total_shots_player)}%"),
            ("", ""),
            ("-- Бот --", ""),
            ("Попаданий:", f"{self.engine.hits_opponent}"),
            ("Промахов:", f"{self.engine.misses_opponent}"),
            ("Точность:", f"{self._calc_accuracy(self.engine.hits_opponent, self.engine.total_shots_opponent)}%"),
        ]

        for label, value in stats:
            if label == "":
                content_y += 4
                continue

            if label.startswith("--"):
                text = self.tiny_font.render(label, True, (200, 200, 100))
                self.screen.blit(text, (content_x, content_y))
                content_y += text.get_height() + 4
            else:
                label_surf = self.tiny_font.render(label, True, TEXT_COLOR)
                value_surf = self.tiny_font.render(value, True, (255, 255, 200))

                total_width = label_surf.get_width() + value_surf.get_width() + 4
                if total_width <= content_width:
                    self.screen.blit(label_surf, (content_x, content_y))
                    self.screen.blit(value_surf, (content_x + label_surf.get_width() + 4, content_y))
                else:
                    self.screen.blit(label_surf, (content_x, content_y))
                    content_y += label_surf.get_height() + 2
                    self.screen.blit(value_surf, (content_x, content_y))

                content_y += label_surf.get_height() + 3

            if content_y > PANEL_Y + PANEL_HEIGHT - 30:
                break

        # Сообщение внизу панели
        content_y = PANEL_Y + PANEL_HEIGHT - 55
        pygame.draw.line(self.screen, PANEL_BORDER,
                         (content_x, content_y),
                         (content_x + content_width, content_y), 1)
        content_y += 6

        msg_lines = self._wrap_text_to_width(self.message, content_width, self.tiny_font)
        for line in msg_lines[:2]:
            msg_surf = self.tiny_font.render(line, True, (255, 255, 150))
            msg_x = PANEL_X + (PANEL_WIDTH - msg_surf.get_width()) // 2
            if msg_x < content_x:
                msg_x = content_x
            if msg_x + msg_surf.get_width() > PANEL_X + PANEL_WIDTH - margin:
                clipped = line[:25] + "..."
                msg_surf = self.tiny_font.render(clipped, True, (255, 255, 150))
                msg_x = PANEL_X + (PANEL_WIDTH - msg_surf.get_width()) // 2
            self.screen.blit(msg_surf, (msg_x, content_y))
            content_y += msg_surf.get_height() + 2

    def _calc_accuracy(self, hits, total):
        """Вычисляет точность в процентах."""
        if total == 0:
            return 0
        return round(hits / total * 100, 1)

    def _wrap_text_to_width(self, text, max_width, font):
        """Переносит текст на строки с учетом максимальной ширины в пикселях."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " + word if current_line else word)
            test_surf = font.render(test_line, True, (0, 0, 0))

            if test_surf.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]

    def draw_victory_screen(self):
        """Отрисовка экрана победы."""
        # Полупрозрачный фон
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(PANEL_BG)
        self.screen.blit(overlay, (0, 0))

        # Заголовок победы
        winner_text = "ПОБЕДА!" if self.engine.winner == "player" else "ПОРАЖЕНИЕ!"
        winner_color = (0, 255, 0) if self.engine.winner == "player" else (255, 100, 100)
        text = self.font.render(winner_text, True, winner_color)
        self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 100))

        # Сообщение о победителе
        text = self.medium_font.render(self.message, True, TEXT_COLOR)
        self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 160))

        # Статистика
        stats = [
            f"Всего ходов: {self.engine.total_shots_player + self.engine.total_shots_opponent}",
            f"Ваша точность: {self.engine.hits_player}/{self.engine.total_shots_player} ({self._calc_accuracy(self.engine.hits_player, self.engine.total_shots_player)}%)",
            f"Точность бота: {self.engine.hits_opponent}/{self.engine.total_shots_opponent} ({self._calc_accuracy(self.engine.hits_opponent, self.engine.total_shots_opponent)}%)"
        ]
        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, TEXT_COLOR)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 220 + i * 30))

        # Кнопка "Новая игра"
        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, 320, 150, 40)
        color = BUTTON_HOVER_COLOR if button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
        text_surf = self.small_font.render("Новая игра", True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)

        # Кнопка "Выход"
        exit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, 380, 150, 40)
        color = (200, 50, 50) if exit_rect.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
        pygame.draw.rect(self.screen, color, exit_rect, border_radius=5)
        text_surf = self.small_font.render("Выход", True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=exit_rect.center)
        self.screen.blit(text_surf, text_rect)


def main():
    """Точка входа для GUI."""
    game = SeaBattleGUI()
    game.run()


if __name__ == "__main__":
    main()