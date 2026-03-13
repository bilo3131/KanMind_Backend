from rest_framework import serializers
from auth_user.models import UserProfile
from kanmind_app.models import Board, Task, Comment
from auth_user.api.serializers import UserProfileSerializer
from .permissions import IsBoardMember


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task objects.
    Assignee and reviewer are returned as full objects (read-only).
    For writing, use assignee_id and reviewer_id (UserProfile PKs).
    comments_count is a computed field showing how many comments the task has.
    """
    assignee = UserProfileSerializer(read_only=True)
    reviewer = UserProfileSerializer(read_only=True)
    # Write-only fields to accept UserProfile PKs when creating/updating a task
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(
    ), source='assignee', write_only=True, allow_null=True, required=False)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(
    ), source='reviewer', write_only=True, allow_null=True, required=False)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer',
                  'due_date', 'comments_count', 'assignee_id', 'reviewer_id']
        permission_classes = [IsBoardMember]

    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the board list endpoint (/api/boards/).
    Returns summary data: title, owner, and computed counts.
    The members field is write-only (used when creating a board with initial members).
    """
    # Write-only: accepts a list of UserProfile PKs when creating a board
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=UserProfile.objects.all(), write_only=True, required=False)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'members', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(BoardSerializer):
    """
    Serializer for the board detail endpoint (/api/boards/{pk}/).
    Extends BoardSerializer with full member objects, owner data, and nested tasks.

    GET response includes: id, title, owner_id, members (full objects), tasks (without board field).
    PATCH response includes: id, title, owner_data, members_data (after update).
    """
    # Readable and writable list of UserProfile PKs (used in PATCH to update members)
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=UserProfile.objects.all(), required=False)
    members_data = UserProfileSerializer(source='members', many=True, read_only=True)
    owner_data = UserProfileSerializer(source='owner_id', read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'owner_data', 'members', 'members_data', 'tasks']

    def to_representation(self, instance):
        """
        Adjusts the response fields depending on the HTTP method:
        - PATCH: returns owner_data and members_data (full objects), hides tasks
        - GET:   returns owner_id and members as full objects, removes board from each task
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            data.pop('owner_id', None)
            data.pop('members', None)
            data.pop('tasks', None)
        else:
            data.pop('owner_data', None)
            data.pop('members_data', None)
            data['members'] = UserProfileSerializer(instance.members.all(), many=True).data
            for task in data.get('tasks', []):
                task.pop('board', None)
        return data

    def update(self, instance, validated_data):
        """
        Updates the board. If a new members list is provided, the M2M relationship
        is updated via members.set(), which triggers the m2m_changed signal.
        The signal in models.py automatically nulls assignee/reviewer on tasks
        for any members that were removed.
        """
        members = validated_data.pop('members', None)
        instance = super().update(instance, validated_data)
        if members is not None:
            # Triggers the m2m_changed signal which handles task assignment nulling
            instance.members.set(members)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment objects.
    The author, task, and created_at fields are read-only (set automatically on creation).
    created_at is formatted to second precision.
    """
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['task', 'author', 'created_at']
