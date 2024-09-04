import os
import sys

from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from random import randint
from client.models import MyUser
from core.common import MyUserRoles
from school.models import OoscPartner, School, StudentIntergrate, Teacher, Student, StudentAbsentReason, SchoolsStudentsImport
from school.tasks import import_school_students
import school.signals as school_signals
from django.db import transaction

@receiver(post_save, sender=School, dispatch_uid="school_create_teacher")
def my_school_handler(sender, **kwargs):
    created = kwargs["created"]
    instance = kwargs["instance"]
    if created:
        ###Create the username and password
        try:
            teacher = Teacher.objects.create(
                is_school_admin=True, email=instance.email, first_name="ADMIN", last_name=instance.name, is_non_delete=True, phone=instance.emis_code, school_id=instance.id
            )
            # print("Created Teacher: {}".format(teacher.id))
        except Exception as e:
            print(e)


@receiver(post_save, sender=Teacher, dispatch_uid="teacher_create_credentials")
def my_teacher_handler(sender, **kwargs):
    created = kwargs["created"]
    instance = kwargs["instance"]

    ###Create the username and password
    if created:
        try:
            username = instance.school.emis_code if instance.is_non_delete else instance.phone
            role = "SCHA" if instance.is_non_delete else "SCHT"
            # if instance.email == None or instance.email == "":
            old_password = "admin"
            # else:
            #     old_password = "{}".format(randint(111111, 999999))
            user = MyUser.objects.create_user(
                password=old_password,
                # old_password=old_password,
                username=username,
                email=instance.email,
                role=role,
                filter_args="{}".format(instance.school_id),
                first_name=instance.first_name,
                last_name=instance.last_name,
            )
            instance.user_id = user.id
            instance.save()
        except Exception as e:
            print(e)


@receiver(school_signals.partner_save, sender=OoscPartner, dispatch_uid="oosc_partner_create_credentials")
def my_oosc_partner_handler(sender, **kwargs):
    instance = kwargs["instance"]
    
    # print("Setting up partner")
    try:
        ids=list(map(lambda x:str(x), instance.schools.all().values_list("id",flat=True)))
        
        filter_args= ",".join(ids)
        if(instance.user !=None):
            instance.user.filter_args=filter_args
            instance.user.name=instance.name
            instance.user.username=instance.email
            instance.user.save()
        else:
            use=MyUser.objects.create(
                first_name=instance.name,
                username=instance.email,
                filter_args=filter_args,
                role=MyUserRoles.NGO.name,
            )
            # print(use)
            use.set_password("admin")
            use.save()
            instance.user_id=use.id
            instance.save()
    except Exception as e:
        raise e
        print("Failed to save.")
        print(e)
            


@receiver(post_delete, sender=Teacher, dispatch_uid="teacher_pre_delete_credentials")
def teacher_pre_delete(sender, **kwargs):
    instance = kwargs["instance"]
    if instance.user_id:
        MyUser.objects.filter(id=instance.user_id).delete()


@receiver(post_save, sender=Student, dispatch_uid="create_update_student")
def student_added(sender, **kwargs):
    instance = kwargs["instance"]
    created = kwargs.get("created", False)


@receiver(post_save, sender=StudentIntergrate, dispatch_uid="student_intergrate_add")
def student_intergation_added(sender, **kwargs):
    instance = kwargs["instance"]
    created = kwargs.get("created", False)
    if created:
        ## Movie the student
        Student.objects.filter(id=instance.student_id).update(stream_id=instance.to_stream_id)
        StudentIntergrate.objects.exclude(id=instance.id).update(can_reverse=False)


@receiver(post_delete, sender=StudentIntergrate, dispatch_uid="student_intergrate_deleted")
def student_intergation_deleted(sender, **kwargs):
    instance = kwargs["instance"]
    # print(instance)
    if instance.can_reverse:
        Student.objects.filter(id=instance.student_id).update(stream_id=instance.from_stream_id)


# @receiver(post_save, sender=StudentAbsentReason, dispatch_uid="create_update_student_absent_reason")
# def student_absent_reason_added(sender,**kwargs):
#     instance = kwargs["instance"]
#     created = kwargs.get("created", False)
#     # Update the other regardless of the situatuib
#     update_attendance_reason_for_absent(instance)


@receiver(post_save, sender=SchoolsStudentsImport, dispatch_uid="on_imports_creation")
def import_added(sender, **kwargs):
    instance = kwargs["instance"]
    created = kwargs.get("created", False)
    if created:
        if "test" in sys.argv:
            import_school_students.task_function(instance.id)
        else:
            import_school_students(instance.id)


@receiver(post_delete, sender=SchoolsStudentsImport, dispatch_uid="on_delete_stud_import")
def auto_delete_file_on_delete_school_import(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.import_file:
        if os.path.isfile(instance.import_file.path):
            os.remove(instance.import_file.path)

    if instance.errors_file:
        if os.path.isfile(instance.errors_file.path):
            os.remove(instance.errors_file.path)
