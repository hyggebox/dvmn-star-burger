# Generated by Django 4.0.4 on 2022-04-22 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_alter_productsqty_order_price'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productsqty',
            options={'verbose_name': 'Товары в заказе', 'verbose_name_plural': 'Товары в заказе'},
        ),
    ]