from django.db import migrations


def get_prices(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')

    for order in Order.objects.all().iterator():
        for product_qty in order.quantity.all().iterator():
            price = product_qty.product.price
            product_qty.order_price = price
            product_qty.save()


def move_backwards(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    for order in Order.objects.all().iterator():
        for product_qty in order.quantity.all().iterator():
            product_qty.order_price = None
            product_qty.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_rename_price_productsqty_order_price'),
    ]

    operations = [
        migrations.RunPython(get_prices, move_backwards),
    ]
