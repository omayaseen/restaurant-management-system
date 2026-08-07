from django.db import models
from accounts.models import User
from menu.models import Menu

# Create your models here.

class Order(models.Model): 
    STATUS_CHOICES = [
        ('pending','Pending'),
        ('preparing','Preparing'),
        ('completed','Completed')
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    order_date = models.DateTimeField(
       auto_now_add = True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Order {self.id}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1
    )
    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
