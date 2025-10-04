from django.db import models

class Title(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Character(models.Model):
    # all data must be in english
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="characters")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ParsingMaterials(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="parsing_materials")
    link = models.URLField(null=False, blank=False)