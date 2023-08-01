# Generated by Django 4.2.3 on 2023-08-01 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0010_alter_customer_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentorderitem',
            name='rent_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='hub.rentorder'),
        ),
    ]
