from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator


class Warehouse(models.Model):
    """
    Модель для хранения информации о складе.

    :param address - адрес склада, строка длиной до 250 символов.
    """
    address = models.CharField(max_length=250)


class Employee(models.Model):
    """
    Модель для хранения информации о сотрудниках.

    :param warehouse - связь с моделью Warehouse, указывающая на склад, где работает сотрудник.
    :param salary - зарплата сотрудника, не может быть отрицательной.
    :param is_manager - булево значение, указывающее, является ли сотрудник менеджером.
    """
    warehouse = models.ForeignKey(to=Warehouse, on_delete=models.CASCADE)
    salary = models.IntegerField(validators=[MinValueValidator(0)])
    is_manager = models.BooleanField(default=False)


class Product(models.Model):
    """
    Модель для хранения информации о товаре.

    :param warehouse - связь с моделью Warehouse, указывающая на склад, где находится товар.
    :param cost - стоимость товара, не может быть отрицательной.
    :param image - изображение товара, загружается в папку 'products/'.
    :param description - текстовое описание товара.
    """
    warehouse = models.ForeignKey(to=Warehouse, on_delete=models.CASCADE)
    cost = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/')
    description = models.TextField()


class Basket(models.Model):
    """
    Модель для хранения информации о корзине пользователя.

    :param user - связь с моделью User, указывающая на пользователя, которому принадлежит корзина.
    :param product - связь с моделью Product, указывающая на товар, добавленный в корзину.
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)


class Comment(models.Model):
    """
    Модель для хранения комментариев к товарам.

    :param user - связь с моделью User, указывающая на пользователя, который оставил комментарий.
    :param product - связь с моделью Product, указывающая на товар, к которому оставлен комментарий.
    :param text - текст комментария.
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    text = models.TextField()