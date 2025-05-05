from django.db import models


class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Увеличил размер для хранения хешированного пароля

    def __str__(self):
        return self.username



