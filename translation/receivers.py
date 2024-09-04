from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

from translation.models import LocaleTranslationText, TranslationLocale, TranslationText

print("JHELLOAKOD")


@receiver(post_save, sender=TranslationLocale, dispatch_uid="translation_locale_save")
def on_translation_locale_save(sender, **kwargs):
    created = kwargs["created"]
    instance = kwargs["instance"]
    print("Translation locale creaded")

    ## Update all the translationTexts
    if created:
        text_ids = TranslationText.objects.values_list("id", flat=True)
        translations = [LocaleTranslationText(text_id=id, locale_id=instance.id) for id in text_ids]
        # print(translations)
        try:
            LocaleTranslationText.objects.bulk_create(translations)
        except Exception as e:
            print(e)


@receiver(post_save, sender=TranslationText, dispatch_uid="translation_text_save")
def on_translation_text_save(sender, **kwargs):
    created = kwargs["created"]
    instance = kwargs["instance"]
    # print("Translation Text creaded")

    if created:
        local_ids = TranslationLocale.objects.values_list("id", flat=True)
        translations = [LocaleTranslationText(locale_id=id, text_id=instance.id) for id in local_ids]
        # print(translations)

        try:
            LocaleTranslationText.objects.bulk_create(translations)

        except Exception as e:
            print(e)
