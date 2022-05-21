from django.db import models


class PlaceCoordinates(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True,
        db_index=True
    )
    lat = models.DecimalField(
        'широта',
        max_digits=8,
        decimal_places=6,
        null=True
    )
    lon = models.DecimalField(
        'долгота',
        max_digits=8,
        decimal_places=6,
        null=True
    )
    save_date = models.DateTimeField(
        'дата актуализации',
        auto_now=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'координаты места'
        verbose_name_plural = 'координаты мест'

    def __str__(self):
        return self.address
