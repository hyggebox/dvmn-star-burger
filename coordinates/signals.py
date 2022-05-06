from django.db.models.signals import post_save
from django.dispatch import receiver

from foodcartapp.models import Order, Restaurant


@receiver(post_save, sender=Order)
def is_order_changed(sender, instance=None, created=False, **kwargs):
    instance.fetch_coords()


@receiver(post_save, sender=Restaurant)
def is_order_changed(sender, instance=None, created=False, **kwargs):
    instance.fetch_coords()
