from django.contrib.auth import get_user_model
from django.db import models

# Get the default Django user model.
User = get_user_model()


class Board(models.Model):
    """Represent a Kanban board with an owner and members."""

    title = models.CharField(max_length=250)
    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="board_related_name",
    )
    members = models.ManyToManyField(User)

    class Meta:
        verbose_name = "Board"

    def __str__(self):
        """Return the board title."""
        return self.title


STATUS_CHOICES = [
    ("to-do", "To Do"),
    ("in-progress", "In Progress"),
    ("review", "Review"),
    ("done", "Done"),
]

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]


class Task(models.Model):
    """Represent a task belonging to a Kanban board."""

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="task_board",
    )
    title = models.CharField(max_length=250)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="to-do",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="low",
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_assignee",
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_reviewer",
        null=True,
        blank=True,
    )
    due_date = models.DateField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Task"

    def __str__(self):
        """Return the task title."""
        return self.title


class Comment(models.Model):
    """Represent a comment associated with a task."""

    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_author",
    )
    content = models.TextField()
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comment_task",
    )

    class Meta:
        verbose_name = "Comment"

    def __str__(self):
        """Return the comment ID and its author."""
        return f"Comment {self.pk} by {self.author}"
