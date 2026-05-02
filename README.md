<h1 align="center"> Морской бой: ИИ-симулятор и Аналитика</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Pygame-2.5+-green.svg" alt="Pygame">
  <img src="https://img.shields.io/badge/Matplotlib-3.7+-orange.svg" alt="Matplotlib">
  <img src="https://img.shields.io/badge/Seaborn-0.12+-pink.svg" alt="Seaborn">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
</p>

## О проекте

Проект «Морской бой» — это не просто графическая игра, а полноценный исследовательский инструмент для анализа ИИ-стратегий.

-  **Игровой режим:** Сразитесь с ИИ в интерактивном интерфейсе с ручной или автоматической расстановкой кораблей.
-  **Симулятор:** Запустите тысячи партий «бот против бота» для сбора статистики.
-  **Аналитика:** Автоматически постройте графики и получите выводы о том, какая стратегия эффективнее и почему.

Проект демонстрирует навыки: **ООП, паттерны проектирования (Strategy), модульная архитектура, работа с Pygame, визуализация данных (Matplotlib/Seaborn), сбор и анализ статистики.**

##  Быстрый старт

### Установка и запуск

1. **Клонируйте репозиторий**
   git clone https://github.com/your-username/sea_battle.git
   cd sea_battle

2. **Установите зависимости**
   pip install -r requirements.txt

3. **Запустите игру**
   python run.py gui

##  Режимы работы

Проект имеет три режима, переключаемых через командную строку:

| Команда | Описание |
|---------|----------|
| `python run.py gui` | Графическая игра против ИИ |
| `python run.py simulate` | Симуляция (300 партий × 3 конфига) и генерация отчёта |
| `python run.py report` | Только аналитика по уже собранному CSV |

##  Стратегии ИИ

В проекте реализованы и сравниваются различные стратегии через паттерн **Strategy**.

### Паттерны расстановки кораблей
| Стратегия | Описание |
|-----------|----------|
| **Random** | Полностью случайное размещение |
| **Edge** | Корабли прижимаются к краям (сложнее найти) |
| **Clustered** | Корабли группируются (высокий риск для флота) |

### Алгоритмы стрельбы
| Стратегия | Описание |
|-----------|----------|
| **Random** | Случайный выбор клетки |
| **Hunt & Target** | «Сетка» для поиска + добивание раненых |
| **Probability** | Тепловая карта вероятностей для каждой клетки |

##  Аналитика

Симулятор проверяет 3 конфигурации:
- **Конфиг A (Базовый):** Random × Random
- **Конфиг B (Агрессивный поиск):** Edge + Hunt & Target × Random
- **Конфиг C (Битва стратегий):** Clustered + Hunt & Target × Edge + Probability

Результаты автоматически визуализируются

**Аналитические выводы** (формируются автоматически):
1. Влияние паттерна расстановки на живучесть флота
2. Эффективность стратегий стрельбы по сокращению длительности партии
3. Взаимодействие между стратегиями расстановки и стрельбы

##  Технологии

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pygame-00A000?style=for-the-badge&logo=pygame&logoColor=white" alt="Pygame">
  <img src="https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=matplotlib&logoColor=white" alt="Matplotlib">
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
</p>

##  Архитектура проекта

Ключевая особенность — **строгое разделение логики и представления.** Игровое ядро (`game_core.py`) не зависит от GUI, что позволяет использовать его и в игре, и в симуляторе.

```
sea_battle/
├── run.py                # Точка входа (argparse)
├── requirements.txt      # Зависимости
├── game_core.py          # Ядро игры (Board, GameEngine, все стратегии)
├── renderer.py           # Отрисовка поля (Pygame)
├── main_gui.py           # Графический интерфейс
├── simulator.py          # Пакетный симулятор матчей
├── run_experiment.py     # Конфигурация экспериментов
├── analysis.py           # Визуализация и генерация отчёта
├── experiment_results.csv
├── report/               # Графики и отчёт (авто)
│   ├── histogram.png
│   ├── boxplot.png
│   ├── winrate.png
│   ├── heatmap_accuracy.png
│   └── report.md
└── screenshots/          # Демо-материалы
```

##  Контрибьютинг

Приветствуются pull-request'ы! Для серьёзных изменений сначала создайте issue для обсуждения. Сейчас идёт активная работа над улучшением стратегий ии-ботов и анализом.


##  Контакты

Ваше Имя — [@Aksey_101](https://t.me/Aksey_101)
