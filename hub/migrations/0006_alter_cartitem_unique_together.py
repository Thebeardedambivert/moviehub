# Generated by Django 4.2.3 on 2023-07-26 04:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0005_alter_movie_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'movie')},
        ),
    ]
