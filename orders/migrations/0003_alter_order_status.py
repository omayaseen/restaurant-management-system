from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('confirmed', 'Confirmed'),
                    ('preparing', 'Preparing'),
                    ('ready', 'Ready'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
