from rest_framework import serializers
from kanban_App.models import Board, Task, Comment
from django.contrib.auth.models import User


class BoardSerializer(serializers.ModelSerializer):

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

        read_only_fields = ["owner_id"]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.task_board.count()

    def get_tasks_to_do_count(self, obj):
        return obj.task_board.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.task_board.filter(priority="high").count()


class DetailBoardSerializer(serializers.ModelSerializer):
    """
    Detail Serializers
    """

    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]

    def get_members(self, obj):

        members = obj.members.all()
        data = []

        for member in members:
            data.append(
                {
                    "id": member.pk,
                    "email": member.email,
                    "fullname": member.first_name + " " + member.last_name,
                }
            )
        return data

    def get_tasks(self, obj):
        # Alle Tasks abrufen, die zu diesem Board gehören
        tasks = obj.task_board.all()
        data = []

        for task in tasks:

            # Zugewiesenen User auslesen
            assignee = task.assignee
            assignee_data = None

            if assignee is not None:
                assignee_data = {
                    "id": assignee.pk,
                    "email": assignee.email,
                    "fullname": assignee.first_name + " " + assignee.last_name,
                }

            # Reviewer auslesen
            reviewer = task.reviewer
            reviewer_data = None

            if reviewer is not None:
                reviewer_data = {
                    "id": reviewer.pk,
                    "email": reviewer.email,
                    "fullname": reviewer.first_name + " " + reviewer.last_name,
                }

            # Task mit den zugehörigen User-Daten zur Liste hinzufügen
            data.append(
                {
                    "id": task.pk,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assignee": assignee_data,
                    "reviewer": reviewer_data,
                    "due_date": task.due_date,
                    "comments_count": task.comment_task.count(),
                }
            )

        return data


class UserSerializer(serializers.ModelSerializer):

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return obj.first_name + " " + obj.last_name


class TaskSerializer(serializers.ModelSerializer):

    comments_count = serializers.SerializerMethodField()

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="reviewer",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return obj.comment_task.count()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]
