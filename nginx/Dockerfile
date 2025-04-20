# Используем официальный Nginx образ
FROM nginx:alpine

COPY ssl_params /etc/nginx/ssl_params

# Копируем конфигурацию Nginx в контейнер
COPY nginx.conf /etc/nginx/conf.d/default.conf
