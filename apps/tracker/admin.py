from django.contrib import admin
from apps.tracker.models import Title, Character, ParsingMaterials

# Register your models here.
@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'title', 'created_at')
    search_fields = ('name',)


@admin.register(ParsingMaterials)
class ParsingMaterialsAdmin(admin.ModelAdmin):
    list_display = ('id', 'character', 'link')
    search_fields = ('character__name', )
