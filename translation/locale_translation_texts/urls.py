from django.conf.urls import url
from translation.locale_translation_texts.views import ListCreateLocaleTranslationTextsAPIView, ListLocaleTranslationTextDynamicsAPIView, RetrieveUpdateDestroyLocaleTranslationTextAPIView

urlpatterns = [
    url(r"^$", ListCreateLocaleTranslationTextsAPIView.as_view(), name="list_create_locale_translation_texts"),
    url(r"^stats/(?P<type>.+)/?", ListLocaleTranslationTextDynamicsAPIView.as_view(), name="list_dynamic_locale_translation_texts_statistics"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroyLocaleTranslationTextAPIView.as_view(), name="retrieve_update_destroy_locale_translation_text"),
]
