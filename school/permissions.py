from rest_framework.permissions import BasePermission

PROTECTED_METHODS = ["DELETE", "PATCH", "PUT"]


class IsNonDeleteTeacher(BasePermission):
    message = "Failed since the teacher is the school's superuser."

    def has_object_permission(self, request, view, obj):
        if request.method in PROTECTED_METHODS:
            return not obj.is_non_delete
        return True


class IsAnEmptySteam(BasePermission):
    message = "Move students before attempting to delete the class."

    def has_object_permission(self, request, view, obj):
        if request.method in ["DELETE"]:
            return obj.students.filter(active=True).all().count() == 0
        return True
