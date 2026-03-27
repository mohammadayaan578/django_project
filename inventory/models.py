from django.db import models


# SUPPLIER MODEL
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name


# CATEGORY MODEL
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# PRODUCT MODEL
class Product(models.Model):
    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.IntegerField()

    def __str__(self):
        return self.name


# INVOICE MODEL
class Invoice(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=200)
    customer_address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.id}"



class SupplierTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('IN', 'Stock In'),   # supplier se liya
        ('OUT', 'Stock Out'), # supplier ko diya
    )

    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"