from rest_framework.permissions import BasePermission
from kanmind_app.models import Board, Task
from rest_framework.exceptions import NotFound


class IsBoardMemberOrOwner(BasePermission):
    """
    Object-level permission that grants access only if the requesting user
    is either a member or the owner of the board.
    Used for GET and PATCH on the board detail endpoint.
    """
    def has_object_permission(self, request, view, obj):
        return (
            obj.members.filter(user=request.user).exists() or
            obj.owner_id == request.user.userprofile
        )


class IsBoardOwner(BasePermission):
    """
    Object-level permission that grants access only if the requesting user
    is the owner of the board.
    Used for DELETE on the board detail endpoint.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.userprofile


class IsTaskBoardMemberOrOwner(BasePermission):
    """
    View-level permission for comment endpoints (nested under a task URL).
    Looks up the task by 'task_pk' from the URL kwargs, then checks whether
    the requesting user is a member or owner of that task's board.
    Uses has_permission (not has_object_permission) so it also applies to list views.
    Returns 404 if the task does not exist.
    """
    def has_permission(self, request, view):
        task_pk = view.kwargs.get('task_pk')
        try:
            task = Task.objects.get(pk=task_pk)
        except Task.DoesNotExist:
            raise NotFound('Task not found.')
        board = task.board
        return (
            board.members.filter(user=request.user).exists() or
            board.owner_id == request.user.userprofile
        )
