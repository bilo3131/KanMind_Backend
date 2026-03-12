from django.urls import path
from .views import AssignedTasksListView, BoardListCreateView, BoardDetailView, CommentDetailView, CommentListCreateView, ReviewingTasksListView, TaskListCreateView, TaskDetailView
from auth_user.api.views import LoginView, UserProfileList, RegistrationView, UserProfileDetail, EmailCheckView

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='userprofile-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='userprofile-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='assigned-tasks-list'),
    path('tasks/reviewing/', ReviewingTasksListView.as_view(), name='reviewing-tasks-list'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]