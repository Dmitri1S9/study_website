FROM condaforge/mambaforge:latest

WORKDIR /app

COPY archangel_env.yml /app/

RUN mamba env create -f archangel_env.yml

ENV PATH="/opt/conda/envs/Archangel/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=Archangel.settings

COPY . /app/

EXPOSE 5000

RUN /opt/conda/envs/Archangel/bin/python manage.py collectstatic --noinput

CMD ["/opt/conda/envs/Archangel/bin/gunicorn", "--bind", "0.0.0.0:5000", "Archangel.wsgi:application"]
