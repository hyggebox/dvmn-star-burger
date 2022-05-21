from django.db import migrations


def get_prices(apps, schema_editor):
    ProductInOrder = apps.get_model('foodcartapp', 'ProductInOrder')

    product_in_order_query = ProductInOrder.objects.all()
    for product_in_order in product_in_order_query.iterator():
        if not product_in_order.order_price:
            price = product_in_order.product.price
            product_in_order.order_price = price
            product_in_order.save()


def move_backwards(apps, schema_editor):
    ProductInOrder = apps.get_model('foodcartapp', 'ProductInOrder')

    product_in_order_query = ProductInOrder.objects.all()
    for product_in_order in product_in_order_query.iterator():
        product_in_order.order_price = None
        product_in_order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_rename_price_productsqty_order_price'),
    ]

    operations = [
        migrations.RunPython(get_prices, move_backwards),
    ]
