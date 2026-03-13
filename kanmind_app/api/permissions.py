from rest_framework.permissions import BasePermission
from kanmind_app.models import Board, Task
from rest_framework.exceptions import NotFound

class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.members.filter(user=request.user).exists() or
            obj.owner_id == request.user.userprofile
        )
        
class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.userprofile
    
class IsTaskBoardMemberOrOwner(BasePermission):
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