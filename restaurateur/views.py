from collections import defaultdict
from environs import Env

from geopy import distance
import requests

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem


env = Env()
env.read_env()


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


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def count_distance(yandex_api_key, from_place, to_place):
    from_coord = fetch_coordinates(yandex_api_key, from_place)
    to_coord = fetch_coordinates(yandex_api_key, to_place)
    return round((distance.distance(from_coord, to_coord).km), 2)


def get_available_restaurants(orders, yandex_api_key):
    available_restaurants = defaultdict(list)
    for rest_menu_item in RestaurantMenuItem.objects.get_available_restaurants():
        available_restaurants[rest_menu_item.product].append(rest_menu_item.restaurant)

    for order in orders:
        order_products_restaurants = []
        order_products = order.products.all()

        for product in order_products:
            order_products_restaurants.append(available_restaurants[product])

        order_restaurants = set.intersection(*map(set, order_products_restaurants))

        order_restaurants_w_distances = [(restaurant.name,
                                          count_distance(yandex_api_key,
                                                         restaurant.address,
                                                         order.address))
                                         for restaurant in order_restaurants]

        order.available_restaurants = sorted(order_restaurants_w_distances,
                                             key=lambda rest_data: rest_data[1])
    return orders


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    yandex_api_key = env.str('YANDEX_API_KEY')

    orders = Order.objects.get_total().get_restaurants()
    get_available_restaurants(orders, yandex_api_key)
    # get_distances(orders, yandex_api_key)

    return render(request, template_name='order_items.html', context={
        'orders': orders,
        'request': request
    })
