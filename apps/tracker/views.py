from django.shortcuts import render
from rest_framework import viewsets
from .models import Title, Character, ParsingMaterials
from .serializers import TitleSerializer, CharacterSerializer, ParsingMaterialsSerializer

class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer

class ParsingMaterialsViewSet(viewsets.ModelViewSet):
    queryset = ParsingMaterials.objects.all()
    serializer_class = ParsingMaterialsSerializer