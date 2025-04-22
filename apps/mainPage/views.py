from django.shortcuts import render

# Create your views here.

# Главная страница приложения
def home(request):
    return render(request, 'mainPage/main.html')
