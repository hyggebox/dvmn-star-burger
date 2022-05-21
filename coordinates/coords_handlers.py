import requests
from django.conf import settings
from geopy import distance

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
            new_address.save()


def count_distance(from_place, to_place, places_coords):
    coord_to_count = []
    for place in [from_place, to_place]:
        if places_coords[place]:
            coord_to_count.append(places_coords[place])
        else:
            place_instance = PlaceCoordinates.objects.filter(
                address=place).first()
            if not place_instance or not place_instance.lat:
                return 'не удалось вычислить расстояние, нет координат места'
            coord_to_count.append((place_instance.lat, place_instance.lon))
            places_coords[place] = (place_instance.lat, place_instance.lon)

    return round((distance.distance(coord_to_count[0], coord_to_count[1]).km), 2)
