from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from auth_user.models import UserProfile

# Available priority levels for tasks
PRIORITY_CHOICES = (
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
)

# Available status stages a task can be in
STATUS_CHOICES = (
    ('to-do', 'To Do'),
    ('in-progress', 'In Progress'),
    ('review', 'Review'),
    ('done', 'Done'),
)


class Board(models.Model):
    """
    Represents a Kanban board.
    A board has an owner and a list of members (UserProfiles) who can access it.
    """
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(UserProfile, related_name='boards', blank=True)
    owner_id = models.ForeignKey(UserProfile, related_name='owned_boards', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Represents a task (ticket) on a board.
    A task belongs to exactly one board and can optionally have an assignee and a reviewer.
    If the board is deleted, all its tasks are deleted too (CASCADE).
    If the assignee or reviewer is deleted, the field is set to null (SET_NULL).
    """
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
    """
    Represents a comment on a task.
    The author is stored as plain text (fullname at time of writing).
    If the task is deleted, all its comments are deleted too (CASCADE).
    """
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.TextField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.task}'


@receiver(m2m_changed, sender=Board.members.through)
def null_task_assignments_on_member_removal(sender, instance, action, pk_set, **kwargs):
    """
    Signal handler that fires whenever members are removed from a board.
    Automatically sets assignee and reviewer to null for any tasks on that board
    that were assigned to the removed members.
    """
    if action == 'post_remove':
        Task.objects.filter(board=instance, assignee_id__in=pk_set).update(assignee=None)
        Task.objects.filter(board=instance, reviewer_id__in=pk_set).update(reviewer=None)
