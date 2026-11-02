
from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):

    # Order status choices
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
    ]

    # User who placed the order
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Customer details
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address = models.TextField()

    # Order details
    items = models.TextField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20
    )

    # Order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    # Date and time when the order was created
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Order #{self.id} - "
            f"{self.customer_name} - "
            f"{self.status}"
        )