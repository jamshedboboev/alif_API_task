# Запуск проекта

git clone git@github.com:jamshedboboev/alif_API_task.git
cd alif_API_task/app

# Виртуальное окружение и зависимости

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Файл с конфигами

В файле config.yaml можно менять:

- базовую валюту
- список валют
- интервал обнвления
- пороги min/max
- процент изменения для отслеживания

# Запуск приложения

файл - main.py