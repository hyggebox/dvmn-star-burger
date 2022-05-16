import requests
from django.conf import settings
from django.utils import timezone

from coordinates.models import PlaceCoordinates


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def save_coordinates(address):
    new_address, created = PlaceCoordinates.objects.get_or_create(
        address=address,
    )
    if created:
        place_coordinates = fetch_coordinates(address)
        if place_coordinates:
            new_address.lat, new_address.lon = place_coordinates
            new_address.save_date = timezone.now()
            new_address.save()

