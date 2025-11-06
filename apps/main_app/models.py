from django.db import models

class Title(models.Model):
    id = models.AutoField(primary_key=True)
    title_name = models.CharField(max_length=100)


class Character(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    title = models.ForeignKey("Title", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Characteristics(models.Model):
    id = models.AutoField(primary_key=True)
    character = models.OneToOneField(Character, on_delete=models.CASCADE, related_name='characteristics')
    characteristics = models.JSONField()
