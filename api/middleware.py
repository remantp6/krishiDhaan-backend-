from rest_framework.permissions import BasePermission


class SpeakerPermission(BasePermission):
    def has_permission(self, request, view):
        # customize logic to check if this is authentic user
        if request.user:
            return True
        else:
            return True


class SuperUserOnlyList(BasePermission):
    message = 'List only available for SuperUsers'  # error message

    def has_permission(self, request, view):
        if view.action == 'list' and request.user.is_superuser:
            return True
        return False


# readonly
class RetrieveOnly(BasePermission):
    message = 'Read Only'

    def has_permission(self, request, view):
        if view.action in ['retrieve'] or request.user.is_superuser:
            return True
        return False


class ListOnly(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list'] or request.user.is_superuser:
            return True
        return False
