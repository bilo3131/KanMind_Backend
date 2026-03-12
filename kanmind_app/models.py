from django.db import models
from auth_user.models import UserProfile

PRIORITY_CHOICES = (
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
)

STATUS_CHOICES = (
    ('to-do', 'To Do'),
    ('in-progress', 'In Progress'),
    ('review', 'Review'),
    ('done', 'Done'),
)

class Board(models.Model):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(UserProfile, related_name='boards', blank=True)
    owner_id = models.ForeignKey(UserProfile, related_name='owned_boards', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(UserProfile, related_name='assigned_tasks', null=True, blank=True, on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(UserProfile, related_name='review_tasks', null=True, blank=True, on_delete=models.SET_NULL)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to-do')

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.TextField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.task}'