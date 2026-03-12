from django.urls import path
from .views import AssignedTasksListView, BoardListCreateView, BoardDetailView, CommentDetailView, CommentListCreateView, ReviewingTasksListView, TaskListCreateView, TaskDetailView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='assigned-tasks-list'),
    path('tasks/reviewing/', ReviewingTasksListView.as_view(), name='reviewing-tasks-list'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]