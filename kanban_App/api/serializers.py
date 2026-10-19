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


class UserSerializer(serializers.ModelSerializer):

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return obj.first_name + " " + obj.last_name


class DetailBoardSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="members",
        many=True,
        write_only=True,
        required=False,
    )
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "member_ids",
            "tasks",
        ]
        read_only_fields = ["id", "owner_id"]

    def get_tasks(self, obj):
        tasks = obj.task_board.all()
        return [self.serialize_task(task) for task in tasks]

    def serialize_task(self, task):
        return {
            "id": task.pk,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assignee": self.serialize_user(task.assignee),
            "reviewer": self.serialize_user(task.reviewer),
            "due_date": task.due_date,
            "comments_count": task.comment_task.count(),
        }

    def serialize_user(self, user):
        if user is None:
            return None
        return UserSerializer(user).data


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

    def validate_board(self, value):
        if self.instance and value != self.instance.board:
            raise serializers.ValidationError(
                "A task cannot be moved to another board."
            )
        return value

    def validate_board_user(self, user, board, field_name):
        if user is None:
            return

        is_owner = board.owner_id == user
        is_member = board.members.filter(id=user.id).exists()

        if not (is_owner or is_member):
            raise serializers.ValidationError(
                {field_name: "User must be a board member or owner."}
            )

    def validate(self, attrs):
        board = self.instance.board if self.instance else attrs.get("board")

        if board is None:
            return attrs

        for field in ("assignee", "reviewer"):
            self.validate_board_user(attrs.get(field), board, f"{field}_id")

        return attrs


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
