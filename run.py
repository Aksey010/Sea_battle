import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Морской бой - игра и симулятор')
    parser.add_argument('mode', choices=['gui', 'simulate', 'report'],
                        help='Режим запуска: gui (игра), simulate (симуляция), report (отчет)')

    args = parser.parse_args()

    if args.mode == 'gui':
        print("Запуск GUI...")
        from main_gui import main as gui_main
        gui_main()

    elif args.mode == 'simulate':
        print("Запуск симуляции...")
        from run_experiment import run as experiment_run
        experiment_run()

        print("\nГенерация отчета...")
        from analysis import generate_report
        generate_report()

    elif args.mode == 'report':
        print("Генерация отчета по существующим данным...")
        from analysis import generate_report
        generate_report()


if __name__ == "__main__":
    main()