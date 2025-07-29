from django.contrib import admin
from main.models import Warehouse, Employee, Product, Basket, Comment


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'address')
    search_fields = ('address',)
    ordering = ('id',)
    list_display_links = ('id', 'address')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'salary', 'is_manager')
    ordering = ('id',)
    list_display_links = ('id', 'warehouse', 'salary', 'is_manager')
    list_filter = ('is_manager',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'warehouse', 'cost', 'image', 'description')
    ordering = ('id',)
    list_display_links = ('id', 'warehouse', 'cost', 'image', 'description')


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    ordering = ('id',)
    list_display_links = ('id', 'user', 'product')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'text')
    ordering = ('id',)
    list_display_links = ('id', 'user', 'product', 'text')
