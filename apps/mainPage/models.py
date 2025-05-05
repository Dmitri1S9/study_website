from django.db import models


class WareHouse(models.Model):
    wareHouseID = models.AutoField(primary_key=True)
    address = models.TextField(unique=True, db_index=True)

    def __str__(self):
        return self.address

class Product(models.Model):
    productID = models.AutoField(primary_key=True)
    wareHouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    cost = models.IntegerField()

    def __str__(self):
        return str(self.productID)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.BinaryField()

class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.TextField()

