from simulator import run_batch, export_to_csv
from game_core import (
    RandomPlacement, EdgePlacement, ClusteredPlacement,
    RandomShooting, HuntAndTarget, ProbabilityShooting
)
import time


def run():
    """Запускает все эксперименты и сохраняет результаты."""
    print("Начало экспериментов...")
    start_time = time.time()

    # Определение конфигураций
    configs = [
        {
            'name': 'A',
            'player_shooting': RandomShooting,
            'opponent_shooting': RandomShooting,
            'player_placement': RandomPlacement,
            'opponent_placement': RandomPlacement
        },
        {
            'name': 'B',
            'player_shooting': HuntAndTarget,
            'opponent_shooting': RandomShooting,
            'player_placement': EdgePlacement,
            'opponent_placement': RandomPlacement
        },
        {
            'name': 'C',
            'player_shooting': HuntAndTarget,
            'opponent_shooting': ProbabilityShooting,
            'player_placement': ClusteredPlacement,
            'opponent_placement': EdgePlacement
        }
    ]

    n_games = 300
    all_results = []

    for config in configs:
        print(f"\n{'='*50}")
        print(f"Конфигурация {config['name']}:")
        print(f"  Игрок: {config['player_placement'].__name__} + {config['player_shooting'].__name__}")
        print(f"  Противник: {config['opponent_placement'].__name__} + {config['opponent_shooting'].__name__}")

        batch_config = [config]
        results = run_batch(n_games, batch_config)
        all_results.extend(results)

        # Статистика по конфигурации
        player_wins = sum(1 for r in results if r['winner'] == 'player')
        avg_turns = sum(r['turns'] for r in results) / len(results)
        print(f"  Побед игрока: {player_wins}/{n_games} ({player_wins/n_games*100:.1f}%)")
        print(f"  Средняя длительность: {avg_turns:.1f} ходов")

    # Сохранение результатов
    export_to_csv(all_results, 'experiment_results.csv')

    elapsed_time = time.time() - start_time
    print(f"\nЭксперименты завершены за {elapsed_time:.1f} секунд")
    print("Результаты сохранены в experiment_results.csv")


if __name__ == "__main__":
    run()