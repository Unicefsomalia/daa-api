from django.db import models
from mylib.my_common import MyModel
from django.db.models import F, Q, Count, ExpressionWrapper, BooleanField, Case, When, Value

# Create your models here.

MAX_TRANLATION_FIELD_LENGTH = 500


class TranslationText(MyModel):
    title = models.TextField(unique=True, max_length=MAX_TRANLATION_FIELD_LENGTH)
    example = models.JSONField(default=True, blank=True, null=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"{self.title}"[:45]


class TranslationLocale(MyModel):
    name = models.CharField(unique=True, max_length=45)
    country_code = models.CharField(max_length=3)
    language_code = models.CharField(max_length=3)
    translations = models.JSONField(null=True, blank=True)
    version = models.CharField(max_length=100, editable=False)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-id",)
        unique_together = ("country_code", "language_code")

    def __str__(self):
        return f"{self.language_code}_{self.country_code}"


class LocaleTranslationText(MyModel):
    locale = models.ForeignKey(TranslationLocale, on_delete=models.CASCADE, related_name="text_translations")
    text = models.ForeignKey(TranslationText, on_delete=models.CASCADE, related_name="locale_translations")
    translated_text = models.TextField(max_length=MAX_TRANLATION_FIELD_LENGTH + 100, null=True, blank=True)

    class Meta:
        ordering = ("-text_id",)
        unique_together = ("text", "locale")

    def __str__(self):
        return f"{self.locale.name} -> {self.text.title[:45]}"


LOCALE_TRANSLATIONS_TEXTS_STATS_DEFINTIONS = {
    "id": {
        "value": F("id"),
        "extra_fields": {
            "language": F("locale__name"),
            "country_code": F("locale__country_code"),
            "language_code": F("locale__language_code"),
            "original": F("text__title"),
            "original_description": F("text__description"),
            "translated": F("translated_text"),
            "is_translated": Case(
                When(translated_text__isnull=False, then=True),
                default=False,
                output_field=models.BooleanField(),
            ),
        },
        "resp_fields": {
            "id",
        },
    },
    "locale": {
        "value": F("locale_id"),
        "extra_fields": {
            "language": F("locale__name"),
            "country_code": F("locale__country_code"),
            "language_code": F("locale__language_code"),
            "active": F("locale__active"),
        },
    },
    "status": {
        "value": F("id"),
        "extra_fields": {},
        "resp_fields": {},
    },
}
LOCALE_TRANSLATIONS_TEXTS_DEFAULT_FIELDS = {
    "translated": Count("id", filter=Q(translated_text__isnull=False)),
    "missing": Count("id", filter=Q(translated_text__isnull=True)),
}
