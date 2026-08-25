import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='full_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(
                default='',
                max_length=20,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Enter a valid phone number (digits, spaces, + and - only).',
                        regex='^\\+?[0-9\\s\\-]{7,20}$',
                    )
                ],
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
