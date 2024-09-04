
from django.conf.urls import url
from translation.translation_texts.views import ListCreateTranslationTextsAPIView, RetrieveUpdateDestroyTranslationTextAPIView
urlpatterns=[
    url(r'^$',ListCreateTranslationTextsAPIView.as_view(),name="list_create_translation_texts"),
    url(r'^(?P<pk>[0-9]+)/?$',RetrieveUpdateDestroyTranslationTextAPIView.as_view(),name="retrieve_update_destroy_translation_text"),
]
