from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardSerializer, CommentSerializer, TaskSerializer
from kanmind_app.models import Board, Comment, Task
from rest_framework.response import Response

class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(members__user=self.request.user)
    
    def perform_create(self, serializer):
        board = serializer.save()
        board.members.add(self.request.user.userprofile)
        
    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            board = serializer.save()
            board.owner_id = request.user.userprofile
            board.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardSerializer
    queryset = Board.objects.all()
    
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])
      
    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user.userprofile.fullname,
            task_id=self.kwargs['task_pk']
        )
        
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])
    
class AssignedTasksListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        return Task.objects.filter(assignee__user=self.request.user)
    
class ReviewingTasksListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    
    def get_queryset(self):
        return Task.objects.filter(reviewer__user=self.request.user)