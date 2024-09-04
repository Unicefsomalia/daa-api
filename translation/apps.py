from django.apps import AppConfig


class TranslationConfig(AppConfig):
    name = "translation"

    def ready(self) -> None:
        import translation.receivers
