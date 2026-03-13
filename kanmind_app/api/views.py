from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardDetailSerializer, BoardSerializer, CommentSerializer, TaskSerializer
from kanmind_app.models import Board, Comment, Task
from .permissions import IsBoardMemberOrOwner, IsBoardOwner, IsTaskBoardMemberOrOwner
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response


class BoardListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/boards/  — Returns all boards the authenticated user is a member of.
    POST /api/boards/  — Creates a new board. The creator is automatically set as
                         owner and added as the first member.
    """
    serializer_class = BoardSerializer

    def get_queryset(self):
        # Only return boards where the current user is a member
        return Board.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        board = serializer.save()
        # Set the creator as owner and add them as a member
        board.owner_id = self.request.user.userprofile
        board.members.add(self.request.user.userprofile)
        board.save()


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/boards/{pk}/ — Returns full board details including members and tasks.
    PATCH  /api/boards/{pk}/ — Updates the board (title, members). Members/Owner only.
    DELETE /api/boards/{pk}/ — Deletes the board. Owner only.
    """
    serializer_class = BoardDetailSerializer
    queryset = Board.objects.all()

    def get_permissions(self):
        # Only the board owner is allowed to delete; members can read and update
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/  — Returns all tasks.
    POST /api/tasks/  — Creates a new task on a board.
                        Validates that the board exists and that assignee/reviewer
                        are members of that board.
    """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def create(self, request, *args, **kwargs):
        board_id = request.data.get('board')

        # Return 404 if the referenced board does not exist
        if not Board.objects.filter(pk=board_id).exists():
            raise NotFound('Board not found.')

        board = Board.objects.get(pk=board_id)
        member_ids = board.members.values_list('id', flat=True)

        assignee_id = request.data.get('assignee_id')
        reviewer_id = request.data.get('reviewer_id')

        # Assignee and reviewer must be members of the board
        if assignee_id and int(assignee_id) not in member_ids:
            return Response({'assignee_id': 'User is not a member of this board.'}, status=status.HTTP_400_BAD_REQUEST)
        if reviewer_id and int(reviewer_id) not in member_ids:
            return Response({'reviewer_id': 'User is not a member of this board.'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/{pk}/ — Returns a single task.
    PATCH  /api/tasks/{pk}/ — Updates a task.
    DELETE /api/tasks/{pk}/ — Deletes a task.
    """
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/{task_pk}/comments/ — Returns all comments for a task.
    POST /api/tasks/{task_pk}/comments/ — Adds a comment to a task.
    Only accessible to members or the owner of the task's board.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])

    def perform_create(self, serializer):
        # Automatically set the author (fullname) and link to the task from the URL
        serializer.save(
            author=self.request.user.userprofile.fullname,
            task_id=self.kwargs['task_pk']
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/{task_pk}/comments/{pk}/ — Returns a single comment.
    PATCH  /api/tasks/{task_pk}/comments/{pk}/ — Updates a comment.
    DELETE /api/tasks/{task_pk}/comments/{pk}/ — Deletes a comment.
    Only accessible to members or the owner of the task's board.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])


class AssignedTasksListView(generics.ListAPIView):
    """
    GET /api/tasks/assigned-to-me/ — Returns all tasks where the current user is the assignee.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee__user=self.request.user)


class ReviewingTasksListView(generics.ListAPIView):
    """
    GET /api/tasks/reviewing/ — Returns all tasks where the current user is the reviewer.
    """
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer__user=self.request.user)
