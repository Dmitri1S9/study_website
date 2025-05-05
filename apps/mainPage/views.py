from django.shortcuts import render
from .models import Product

# Create your views here.

# Главная страница приложения
def main(request):
    products = Product.objects.all()  # выгружаем все продукты из БД
    return render(request, 'mainPage/main.html', {'products': products})

