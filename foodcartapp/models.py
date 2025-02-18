from collections import defaultdict

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from coordinates.coords_handlers import save_coordinates, count_distance


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name

    def save_coords(self):
        save_coordinates(self.address)


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItemQuerySet(models.QuerySet):

    def get_available_rests_for_products(self):
        return self.filter(availability=True).prefetch_related('product',
                                                               'restaurant')


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    objects = RestaurantMenuItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(models.QuerySet):

    def get_total_price(self):
        total_price = self.annotate(
            total_price=Sum(F('products_in_order__quantity') * F('products_in_order__order_price'))
        )
        return total_price

    def get_restaurants(self):
        return self.prefetch_related('products__menu_items__restaurant')

    def get_unprocessed(self):
        return self.filter(status='unprocessed')

    def get_available_restaurants(self):
        available_restaurants = defaultdict(list)
        available_rests_for_products = RestaurantMenuItem.objects.get_available_rests_for_products()

        for rest_menu_item in available_rests_for_products:
            available_restaurants[rest_menu_item.product].append(
                rest_menu_item.restaurant)

        for order in self:
            order_products_restaurants = []
            order_products = order.products.all()

            for product in order_products:
                order_products_restaurants.append(
                    available_restaurants[product])

            order_restaurants = set.intersection(
                *map(set, order_products_restaurants))

            order.available_restaurants = order_restaurants
        return self

    def get_distances(self):
        places_coords = defaultdict(tuple)
        for order in self:
            try:
                order.available_restaurants
            except AttributeError:
                self.get_available_restaurants()
            finally:
                order_restaurants_w_distances = [(restaurant.name,
                                                  count_distance(
                                                      restaurant.address,
                                                      order.address,
                                                      places_coords))
                                                 for restaurant in
                                                 order.available_restaurants]

                order.available_restaurants = sorted(
                    order_restaurants_w_distances,
                    key=lambda rest_data:
                    rest_data[1])
        return self


class Order(models.Model):
    PROCESSED = 'processed'
    UNPROCESSED = 'unprocessed'
    STATUS_CHOICES = [
        (UNPROCESSED, 'Необработанный'),
        (PROCESSED, 'Обработанный'),
    ]

    CASH = 'cash'
    BANK_CARD = 'card'
    ONLINE = 'online'

    PAYMENT_CHOICES = [
        (ONLINE, '✅ Картой на сайте'),
        (BANK_CARD, '💳 Картой'),
        (CASH, '💵 Наличными')
    ]

    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=20,
        choices=STATUS_CHOICES,
        default=UNPROCESSED,
        db_index=True
    )
    payment_method = models.CharField(
        verbose_name='Способ оплаты',
        max_length=30,
        choices=PAYMENT_CHOICES,
        db_index=True
    )
    firstname = models.CharField('имя', max_length=50)
    lastname = models.CharField('фамилия', max_length=50)
    phonenumber = PhoneNumberField('номер тел.', db_index=True)
    address = models.CharField('адрес', max_length=200)
    products = models.ManyToManyField(
        Product,
        through='ProductInOrder',
        verbose_name='товары',
        related_name='orders',
        )
    comment = models.TextField('комментарий', blank=True)
    registered_at = models.DateTimeField(
        'Создан',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Обработан',
        null=True,
        blank=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'Доставлен',
        null=True,
        blank=True,
        db_index=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.lastname} {self.firstname}'

    def save_coords(self):
        save_coordinates(self.address)


class ProductInOrder(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='товар',
        related_name='in_order',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='products_in_order',
    )
    quantity = models.SmallIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)],
        db_index=True
    )
    order_price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_index=True
    )

    class Meta:
        verbose_name = 'Товары в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.order.id} | {self.order}'
