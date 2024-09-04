from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse
from attendance.models import Attendance

from core.tests import BaseAPITest
from school.models import Stream, Student


class StreamTests(BaseAPITest):
    @tag("nc")
    def test_creating_stream(self):
        resp = self.create_stream(name="TeStream", base_class="1", school=1)
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

        resp = self.create_stream(name="TeStream", base_class="2", school=1)
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

        resp = self.create_stream(name="testream", base_class="1", school=1)
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = self.create_stream(base_class="8", school=1, name=None)
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

        resp = self.create_stream(base_class="0", school=1, name="")
        resp = self.create_stream(base_class="0", school=1, name="")
        # print(resp.json())
        self.assertEquals(resp.status_code, 400)

        # print(resp.json())

        resp = self.create_stream(name="TeStream", base_class="1", school=1)
        # self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listing_streams(self):
        self.set_authenticated_user(2)
        resp = self.auth_client.get(reverse("list_create_streams"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_stream(self):
        # Id 2 beacause id is automatically created on creating a stream
        resp = self.auth_client.get(reverse("retrieve_update_destroy_stream", kwargs={"pk": 1}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "TheStream")

    @tag("upst")
    def test_updating_stream(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_stream", kwargs={"pk": 1}), data={"name": "Hello"})
        print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # self.assertEquals(resp.data["name"], "Hello")

        resp = self.auth_client.patch(reverse("retrieve_update_destroy_stream", kwargs={"pk": 1}), data={"name": ""})
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # self.assertEquals(resp.data["name"], "Hello")

    @tag("dst")
    def test_delete_stream_no_learners(self):
        streamresp = self.create_stream(name="TBD", base_class="1")
        id = streamresp.json()["id"]
        self.assertTrue(Stream.objects.filter(id=id).exists())

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        self.assertEquals(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Stream.objects.filter(id=id).exists())
        print(f"{id}")

    @tag("dst1")
    def test_delete_stream_with_learners_move_learners(self):
        id = 1
        # print(Stream.objects.all().values_list("id", flat=True))
        self.assertTrue(Stream.objects.filter(id=id).exists())

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        # print(resp.json())
        self.assertEquals(resp.status_code, 403)
        self.assertTrue(Stream.objects.filter(id=id).exists())
        self.take_attendance()
        Student.objects.filter(stream_id=id).update(stream_id=2)

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        self.assertEquals(resp.status_code, 204)
        self.assertTrue(Stream.objects.filter(id=id).exists())

    @tag("dst2")
    def test_delete_stream_with_learners_deactivate_learners(self):
        id = 1
        # print(Stream.objects.all().values_list("id", flat=True))
        self.assertTrue(Stream.objects.filter(id=id).exists())

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        # print(resp.json())
        self.assertEquals(resp.status_code, 403)
        self.assertTrue(Stream.objects.filter(id=id).exists())
        self.take_attendance()
        Student.objects.filter(stream_id=id).update(active=False)

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        self.assertEquals(resp.status_code, 204)
        self.assertTrue(Stream.objects.filter(id=id).exists())

    @tag("dst", "dst2")
    def test_delete_stream_with_learners_deactivate_learners(self):
        id = 1
        # print(Stream.objects.all().values_list("id", flat=True))
        self.assertTrue(Stream.objects.filter(id=id).exists())

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        # print(resp.json())
        self.assertEquals(resp.status_code, 403)
        self.assertTrue(Stream.objects.filter(id=id).exists())
        self.take_attendance()
        Student.objects.filter(stream_id=id).update(stream_id=2)
        ## Delete all attendances
        Attendance.objects.filter(stream_id=id).delete()

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_stream", kwargs={"pk": id}))
        self.assertEquals(resp.status_code, 204)
        self.assertFalse(Stream.objects.filter(id=id).exists())
