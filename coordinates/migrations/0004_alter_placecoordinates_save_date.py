# Generated by Django 4.0.4 on 2022-05-21 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0003_alter_placecoordinates_save_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placecoordinates',
            name='save_date',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='дата актуализации'),
        ),
    ]
