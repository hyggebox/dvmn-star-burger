from collections import defaultdict

from geopy import distance

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from coordinates.models import PlaceCoordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def count_distance(from_place, to_place, places_coords):
    coord_to_count = []
    for place in [from_place, to_place]:
        if places_coords[place]:
            coord_to_count.append(places_coords[from_place])
        else:
            place_instance = PlaceCoordinates.objects.filter(
                address=place).first()
            if not place_instance:
                return 'не удалось вычислить расстояние, нет координат места'
            coord_to_count.append((place_instance.lat, place_instance.lon))
            places_coords[place] = (place_instance.lat, place_instance.lon)

    return round((distance.distance(coord_to_count[0], coord_to_count[1]).km), 2)


def get_available_restaurants(orders):
    available_restaurants = defaultdict(list)
    places_coords = defaultdict(tuple)

    for rest_menu_item in RestaurantMenuItem.objects.get_available_restaurants():
        available_restaurants[rest_menu_item.product].append(rest_menu_item.restaurant)

    for order in orders:
        order_products_restaurants = []
        order_products = order.products.all()

        for product in order_products:
            order_products_restaurants.append(available_restaurants[product])

        order_restaurants = set.intersection(*map(set, order_products_restaurants))

        order_restaurants_w_distances = [(restaurant.name,
                                          count_distance(restaurant.address,
                                                         order.address,
                                                         places_coords))
                                         for restaurant in order_restaurants]

        order.available_restaurants = sorted(order_restaurants_w_distances,
                                             key=lambda rest_data: rest_data[1])
    return orders


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_total().get_unprocessed().get_restaurants().defer(
        'registered_at',
        'called_at',
        'delivered_at'
    )
    get_available_restaurants(orders)

    return render(request, template_name='order_items.html', context={
        'orders': orders,
        'request': request
    })
