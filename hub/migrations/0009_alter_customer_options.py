# Generated by Django 4.2.3 on 2023-07-29 02:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0008_alter_rentorder_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__first_name', 'user__last_name'], 'permissions': [('view_history', 'Can view history')]},
        ),
    ]
