# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Открываем порты, которые использует приложение
EXPOSE 5000

ENV DJANGO_SETTINGS_MODULE=Archangel.settings

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Команда для запуска Gunicorn с Django приложением
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "Archangel.wsgi:application"]
