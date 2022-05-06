from django.contrib import admin

from .models import PlaceCoordinates


@admin.register(PlaceCoordinates)
class PlaceCoordinatesAdmin(admin.ModelAdmin):
    list_display = ('address', 'save_date', 'lat', 'lon')
    readonly_fields = ['save_date', 'lat', 'lon']
