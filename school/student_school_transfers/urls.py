from django.conf.urls import url
from school.student_school_transfers.views import ListCreateStudentSchoolTransfersAPIView, RetrieveUpdateDestroyStudentSchoolTransferAPIView, AcceptDenyStudentSchoolTransferAPIView

urlpatterns = [
    url(r"^$", ListCreateStudentSchoolTransfersAPIView.as_view(), name="list_create_student_school_transfers"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroyStudentSchoolTransferAPIView.as_view(), name="retrieve_update_destroy_student_school_transfer"),
    url(r"^(?P<pk>[0-9]+)/(?P<school_choice>.+)/?$", AcceptDenyStudentSchoolTransferAPIView.as_view(), name="accept_deny_student_school_transfer"),
]
