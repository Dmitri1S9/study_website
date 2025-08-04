# Используем официальный Nginx образ
FROM nginx:alpine

# Убираем копирование ssl_params — оно не нужно, если отказываемся от SSL
# COPY ssl_params /etc/nginx/ssl_params

# Копируем упрощённый конфиг Nginx без SSL
COPY nginx.conf /etc/nginx/conf.d/default.conf
