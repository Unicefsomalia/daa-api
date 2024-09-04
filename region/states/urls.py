
from django.conf.urls import url
from region.states.views import ListCreateStatesAPIView, RetrieveUpdateDestroyStateAPIView
urlpatterns=[
    url(r'^$',ListCreateStatesAPIView.as_view(),name="list_create_states"),
    url(r'^(?P<pk>[0-9]+)/?$',RetrieveUpdateDestroyStateAPIView.as_view(),name="retrieve_update_destroy_state"),
]
