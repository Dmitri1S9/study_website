# Используем базовый образ с Mamba (в 10 раз быстрее, чем Conda)
FROM condaforge/mambaforge:latest

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл окружения
COPY archangel_env.yml /app/

# Создаём окружение (название возьми из environment.yml, например Archangel)
RUN mamba env create -f archangel_env.yml

# Устанавливаем переменные среды
ENV PATH="/opt/conda/envs/Archangel/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=Archangel.settings

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт
EXPOSE 5000

# Собираем статику через окружение Archangel
#RUN python manage.py migrate
RUN /opt/conda/envs/Archangel/bin/python manage.py collectstatic --noinput

# Запуск Gunicorn из нужного окружения
CMD ["/opt/conda/envs/Archangel/bin/gunicorn", "--bind", "0.0.0.0:5000", "Archangel.wsgi:application"]
