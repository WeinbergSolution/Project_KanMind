from django.contrib.auth.models import User
from rest_framework import serializers

from kanban_App.models import Board, Comment, Task


class BoardSerializer(serializers.ModelSerializer):
    """Serialize boards with member and task statistics."""

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
        """Return the number of board members."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of board tasks."""
        return obj.task_board.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with to-do status."""
        return obj.task_board.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of high-priority tasks."""
        return obj.task_board.filter(priority="high").count()


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user information."""

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        """Return the user's full name."""
        return f"{obj.first_name} {obj.last_name}"


class DetailBoardSerializer(serializers.ModelSerializer):
    """Serialize board details, members, and associated tasks."""

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
        """Return serialized tasks belonging to the board."""
        tasks = obj.task_board.all()
        return [self.serialize_task(task) for task in tasks]

    def serialize_task(self, task):
        """Return task details for the board response."""
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
        """Return user details or None if no user is assigned."""
        if user is None:
            return None
        return UserSerializer(user).data


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks and validate board user assignments."""

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
        """Return the number of comments on a task."""
        return obj.comment_task.count()

    def validate_board(self, value):
        """Prevent moving an existing task to another board."""
        if self.instance and value != self.instance.board:
            raise serializers.ValidationError(
                "A task cannot be moved to another board."
            )
        return value

    def validate_board_user(self, user, board, field_name):
        """Ensure an assigned user belongs to the task board."""
        if user is None:
            return

        is_owner = board.owner_id == user
        is_member = board.members.filter(id=user.id).exists()

        if not (is_owner or is_member):
            raise serializers.ValidationError(
                {field_name: "User must be a board member or owner."}
            )

    def validate(self, attrs):
        """Validate assignee and reviewer against the board."""
        board = self.instance.board if self.instance else attrs.get("board")
        if board is None:
            return attrs

        for field in ("assignee", "reviewer"):
            if field in attrs:
                self.validate_board_user(attrs[field], board, f"{field}_id")

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Serialize task comments with their authors."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "created_at",
            "author",
            "content",
        ]
