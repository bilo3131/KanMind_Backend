from rest_framework import serializers
from auth_user.models import UserProfile
from kanmind_app.models import Board, Task, Comment
from auth_user.api.serializers import UserProfileSerializer


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserProfileSerializer(read_only=True)
    reviewer = UserProfileSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(
    ), source='assignee', write_only=True, allow_null=True, required=False)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(
    ), source='reviewer', write_only=True, allow_null=True, required=False)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
                  'due_date', 'priority', 'board', 'status', 'comments_count']

    def get_comments_count(self, obj):
        return obj.comments.count()

class BoardSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'tasks', 'owner_id', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['members'] = UserProfileSerializer(
            instance.members.all(), many=True).data
        return data
    
class CommentSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'created_at']
        read_only_fields = ['task','author', 'created_at']



