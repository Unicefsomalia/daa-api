
from django.conf.urls import url
from school.student_intergrates.views import ListCreateStudentIntergratesAPIView, RetrieveUpdateDestroyStudentIntergrateAPIView
urlpatterns=[
    url(r'^$',ListCreateStudentIntergratesAPIView.as_view(),name="list_create_student_intergrates"),
    url(r'^(?P<pk>[0-9]+)/?$',RetrieveUpdateDestroyStudentIntergrateAPIView.as_view(),name="retrieve_update_destroy_student_intergrate"),
]
