from django.db import models

# Create your models here.
class Menu(models.Model):
    CATEGORY_CHOICES = [
        ('starter', 'Starter'),
        ('main_course', 'Main Course'),
        ('dessert', 'Dessert'),
        ('drink', 'Drink'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8,decimal_places=2)
    category = models.CharField(max_length=20,choices=CATEGORY_CHOICES)
    available = models.BooleanField(default=True)

    image = models.ImageField(
        upload_to='menu_images/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

