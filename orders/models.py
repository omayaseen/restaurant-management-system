from django.db import models
from django.core.validators import RegexValidator
from accounts.models import User
from menu.models import Menu

# Create your models here.

phone_validator = RegexValidator(
    regex=r'^\+?[0-9\s\-]{7,20}$',
    message="Enter a valid phone number (digits, spaces, + and - only)."
)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Tracks payment (money), separate from `status` above which tracks the
    # kitchen/delivery workflow. Added in Step 2 - Payment Integration.
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
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

    # Checkout / delivery details (added in Step 1 - Professional Checkout).
    # default='' keeps this migration safe for orders that already exist
    # in the database; the CheckoutForm still requires these for new orders.
    full_name = models.CharField(
        max_length=100,
        default=''
    )
    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        default=''
    )
    delivery_address = models.TextField(
        default=''
    )
    notes = models.TextField(
        blank=True,
        null=True
    )

    # --- Payment tracking (added in Step 2 - Payment Integration) ---
    #
    # razorpay_order_id: the id Razorpay assigns when we ask it to create an
    # order to be paid for. We store it (and make it unique) so that if the
    # browser ever resubmits a successful payment - e.g. a double-click, a
    # network retry, or the user hitting Back and re-submitting - we can
    # recognise "this payment was already processed" and avoid creating a
    # second Order for the same payment.
    #
    # razorpay_payment_id: the id of the actual payment Razorpay processed,
    # kept for reference/support purposes (e.g. looking a payment up in the
    # Razorpay dashboard).
    #
    # payment_status: whether the money side of things succeeded. This is
    # deliberately a separate field from `status` - `status` is about food
    # preparation/delivery, `payment_status` is about money. In this project
    # an Order row is only ever created once payment is confirmed, so in
    # practice payment_status will be 'paid' at creation time; it's kept as
    # its own field (rather than reusing `status`) so the two concerns don't
    # get mixed together, and so it has somewhere to live if a refund/failed
    # capture needs to be recorded later.
    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )
    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
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
