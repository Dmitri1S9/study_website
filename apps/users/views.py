from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User


class FatalError(Exception):
    pass


def handle_login(email, password):
    try:
        user = User.objects.get(email=email)
        # print(password, user.password)
        if check_password(password, user.password):
            return True, user
        return False, 'Неверный пароль.'
    except User.DoesNotExist:
        return False, 'Пользователь с таким email не найден.'


def handle_registration(username, email, password):
    # tests are ready
    # don't change, or change tests too!
    if User.objects.filter(email=email).exists():
        return False, 'Электронная почта уже используется.'
    if User.objects.filter(username=username).exists():
        return False, 'Имя уже используется.'
    if len(username) < 4 or not username.strip():
        return False, 'Слишком короткое имя'

    hashed_password = make_password(password)
    user = User(username=username, email=email, password=hashed_password)
    user.save()
    return True, user


def register(request):
    if request.method == 'POST':
        # print(request.POST)
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        flag = request.POST.get('login', 'false').lower() == 'true'
        # print(username, email, password, flag)
        if flag:  # Логин
            success, result = handle_login(email, password)
            if success:
                messages.success(request, f'Добро пожаловать, {result.username}!')
                return redirect('worldPage')
            else:
                messages.error(request, result)
        else:  # Регистрация
            success, result = handle_registration(username, email, password)
            if success:
                messages.success(request, 'Вы успешно зарегистрированы!')
                return redirect('worldPage')
            else:
                messages.error(request, result)

    return render(request, 'registration/register.html')

