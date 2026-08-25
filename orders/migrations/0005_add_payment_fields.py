from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_add_checkout_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
                default='pending',
                max_length=20,
            ),
        ),
    ]
