from rest_framework import serializers
from .models import Title, Character, ParsingMaterials

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['id', 'name']

class CharacterSerializer(serializers.ModelSerializer):
    title = TitleSerializer(read_only=True)  # выводим инфо о тайтле
    title_id = serializers.PrimaryKeyRelatedField(queryset=Title.objects.all(), source='title', write_only=True)

    class Meta:
        model = Character
        fields = ['id', 'name', 'title', 'title_id', 'description', 'created_at']

class ParsingMaterialsSerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    character_id = serializers.PrimaryKeyRelatedField(queryset=Character.objects.all(), source='character', write_only=True)

    class Meta:
        model = ParsingMaterials
        fields = ['id', 'character', 'character_id', 'link']