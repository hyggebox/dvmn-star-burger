# Generated by Django 4.0.4 on 2022-04-18 20:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='имя')),
                ('last_name', models.CharField(max_length=50, verbose_name='фамилия')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='номер тел.')),
                ('address', models.CharField(max_length=200, verbose_name='адрес')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
            },
        ),
        migrations.CreateModel(
            name='ProductsQty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.SmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quantity', to='foodcartapp.order', verbose_name='заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quantity', to='foodcartapp.product', verbose_name='товар')),
            ],
            options={
                'verbose_name': 'Количество товаров в заказе',
                'verbose_name_plural': 'Количество товаров в заказе',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(db_index=True, null=True, related_name='orders', through='foodcartapp.ProductsQty', to='foodcartapp.product', verbose_name='товары'),
        ),
    ]
