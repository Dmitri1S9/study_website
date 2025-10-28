FROM condaforge/mambaforge:latest

ENV MAMBA_NO_BANNER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN mamba env create -n service -f /app/services_env.yml && mamba clean -afy

WORKDIR /app/app
EXPOSE 8044

CMD ["conda","run","--no-capture-output","-n","service","uvicorn","main:app","--host","0.0.0.0","--port","8044"]
