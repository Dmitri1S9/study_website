from django.shortcuts import render
from .models import Product, ProductImage, ProductDetail

# Create your views here.

# Главная страница приложения
def main(request):
    products = Product.objects.all()  # выгружаем все продукты из БД
    images = ProductImage.objects.all()
    details = ProductDetail.objects.all()
    return render(request, 'mainPage/main.html', {
        'products': products, 'images': images, 'details': details
    })

