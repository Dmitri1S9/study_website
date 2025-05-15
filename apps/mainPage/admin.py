from django.contrib import admin
from .models import WareHouse, Product, ProductImage, ProductDetail


@admin.register(WareHouse)
class WareHouseAdmin(admin.ModelAdmin):
    list_display = ('wareHouseID', 'address')
    search_fields = ('address',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductDetailInline(admin.StackedInline):
    model = ProductDetail
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('productID', 'wareHouse', 'cost')
    inlines = [ProductImageInline, ProductDetailInline]
    list_filter = ('wareHouse',)
    search_fields = ('productID',)