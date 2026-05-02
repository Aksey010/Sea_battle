import csv
import os
from game_core import (
    GameEngine, Board,
    RandomPlacement, EdgePlacement, ClusteredPlacement,
    RandomShooting, HuntAndTarget, ProbabilityShooting,
    ShipPlacementStrategy, ShootingStrategy
)


def run_single_game(player_shooting: ShootingStrategy,
                    opponent_shooting: ShootingStrategy,
                    player_placement: ShipPlacementStrategy,
                    opponent_placement: ShipPlacementStrategy) -> dict:
    """
    Запускает одну игру с заданными стратегиями.
    Возвращает словарь с результатами.
    """
    engine = GameEngine()
    engine.setup_player_board(player_placement)
    engine.setup_opponent_board(opponent_placement)
    engine.setup_opponent_strategy(opponent_shooting)

    turns = 0
    while not engine.game_over:
        if engine.player_turn:
            row, col = player_shooting.choose_target(engine.board_opponent)
            result = engine.player_shoot(row, col)
            if result.name in ['HIT', 'DESTROYED']:
                if hasattr(player_shooting, 'notify_result'):
                    player_shooting.notify_result(row, col, result)
        else:
            result = engine.opponent_shoot()

        turns += 1
        # Предотвращение бесконечного цикла
        if turns > 10000:
            break

    return {
        "winner": engine.winner if engine.winner else "draw",
        "turns": turns,
        "total_shots_player": engine.total_shots_player,
        "total_shots_opponent": engine.total_shots_opponent,
        "hits_player": engine.hits_player,
        "hits_opponent": engine.hits_opponent,
        "misses_player": engine.misses_player,
        "misses_opponent": engine.misses_opponent,
        "player_placement": player_placement.__class__.__name__,
        "opponent_placement": opponent_placement.__class__.__name__,
        "player_shooting": player_shooting.__class__.__name__,
        "opponent_shooting": opponent_shooting.__class__.__name__
    }


def run_batch(n_games: int, configs: list[dict]) -> list[dict]:
    """
    Запускает пакет игр для нескольких конфигураций.
    configs - список словарей с ключами:
        player_shooting, opponent_shooting, player_placement, opponent_placement
    Возвращает список результатов всех игр.
    """
    results = []

    for config in configs:
        print(f"Запуск конфигурации: {config}")
        for game_num in range(n_games):
            # Создаем новые экземпляры стратегий для каждой игры
            player_shooting = config['player_shooting']()
            opponent_shooting = config['opponent_shooting']()
            player_placement = config['player_placement']()
            opponent_placement = config['opponent_placement']()

            result = run_single_game(
                player_shooting,
                opponent_shooting,
                player_placement,
                opponent_placement
            )
            results.append(result)

            if (game_num + 1) % 50 == 0:
                print(f"  Завершено игр: {game_num + 1}/{n_games}")

    return results


def export_to_csv(results: list[dict], filename: str):
    """Экспортирует результаты в CSV файл."""
    if not results:
        return

    fieldnames = list(results[0].keys())
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Результаты сохранены в {filename}")