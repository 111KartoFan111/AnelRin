
## Настройка проекта

1. Клонировать репозиторий:
   ```bash
git clone [https://github.com/your-repo/wedding-planner.git](https://github.com/your-repo/wedding-planner.git)

2. Создайте виртуальное окружение Python :
    ```bash
source venv/bin/activate

3. Установите зависимости из файла requirements.txt
    ```bash
pip install -r requirements.txt

4. Перейдите в папку проекта:
    ```bash
cd wedding-planner

5. Cоздайте суперпользователя :
    ```bash
python manage.py createsuperuser

## Запуск проекта

Запустите сервер разработки:
   ```bash
python manage.py runserver