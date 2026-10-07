from django.db import models
from django.contrib.auth import get_user_model

# ruft das Stadart user model
User = get_user_model()


class Board(models.Model):
    """
    Class for Board model
    """

    title = models.CharField(max_length=250)
    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="board_related_name",
    )
    members = models.ManyToManyField(User)

    class Meta:
        verbose_name = "Board"


STATUS_CHOICES = {
    ("TODO", "to-do"),
    ("INPROGRESS", "in-progress"),
    ("REVIEW", "rewiev"),
}

PRIORITY_CHOICES = {
    ("LOW", "low"),
    ("MEDIUM", "medium"),
    ("HIGH", "high"),
}


class Task(models.Model):
    """
    class for tasks
    """

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="task_board",
    )
    title = models.CharField(max_length=250)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="LOW")
    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_assignee",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_reviewer",
    )
    due_date = models.DateField()

    class Meta:
        verbose_name = "Task"


class Comment(models.Model):
    """
    class dor comments
    """

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
