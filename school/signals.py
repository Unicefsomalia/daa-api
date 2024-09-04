from django.dispatch import Signal, receiver

partner_save = Signal(providing_args=["instance",])
