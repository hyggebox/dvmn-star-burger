# Generated by Django 4.0.4 on 2022-04-25 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_alter_order_products_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='комментарий'),
        ),
    ]