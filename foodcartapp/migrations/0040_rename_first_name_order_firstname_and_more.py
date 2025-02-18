# Generated by Django 4.0.4 on 2022-04-20 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_alter_productsqty_qty'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone_number',
            new_name='phonenumber',
        ),
        migrations.RenameField(
            model_name='productsqty',
            old_name='qty',
            new_name='quantity',
        ),
        migrations.AlterField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(db_index=True, related_name='orders', through='foodcartapp.ProductsQty', to='foodcartapp.product', verbose_name='товары'),
        ),
    ]
