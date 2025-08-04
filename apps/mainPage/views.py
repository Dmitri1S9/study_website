from django.shortcuts import render
from .models import Product
from django.contrib.auth import logout

# Create your views here.

# Главная страница приложения
def main(request):

    # action_products = Product.objects.filter(
    #     productaction__isnull=False
    # ).prefetch_related('productimage_set', 'productdetail_set').distinct()

    # return render(request, 'mainPage/main.html', {'products': action_products})
    return render(request, 'mainPage/main.html')

