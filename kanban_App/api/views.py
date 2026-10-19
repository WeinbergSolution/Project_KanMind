from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_App.models import Board, Task, Comment

from .permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsTaskCreatorOrBoardOwner,
    IsCommentAuthor,
)
from .serializers import (
    BoardSerializer,
    DetailBoardSerializer,
    UserSerializer,
    TaskSerializer,
    CommentSerializer,
)


class BoardView(APIView):
    """
    Create boards and list accessible boards.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner_id=request.user)
        return Response(
            BoardSerializer(board).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        boards = Board.objects.filter(
            Q(owner_id=request.user) | Q(members=request.user)
        ).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)


class DetailBoardView(APIView):
    """
    Retrieve, update and delete boards.
    """

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]

    def get_board(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        self.check_object_permissions(request, board)
        return board

    def get(self, request, board_id):
        board = self.get_board(request, board_id)
        serializer = DetailBoardSerializer(board)
        return Response(serializer.data)

    def patch(self, request, board_id):
        board = self.get_board(request, board_id)
        serializer = DetailBoardSerializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, board_id):
        board = self.get_board(request, board_id)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    """
    Look up a user by email address.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            raise ValidationError("No email address provided.")

        user = get_object_or_404(User, email=email)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserTaskView(APIView):
    """
    List tasks assigned to or reviewed by the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, task_type):
        if task_type == "assigned-to-me":
            tasks = Task.objects.filter(assignee=request.user)
        elif task_type == "reviewing":
            tasks = Task.objects.filter(reviewer=request.user)
        else:
            return Response(
                {"detail": "Unknown task type."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskView(APIView):
    """
    Create tasks on accessible boards.
    """

    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.validated_data["board"]
        self.check_object_permissions(request, board)

        task = serializer.save(created_by=request.user)
        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_201_CREATED,
        )


class TaskDetailView(APIView):
    """
    Update and delete tasks with method-specific permissions.
    """

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsBoardMemberOrOwner()]

    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentView(APIView):
    """
    List and create comments on accessible tasks.
    """

    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_task(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(request, task)
        return task

    def get(self, request, task_id):
        task = self.get_task(request, task_id)
        comments = Comment.objects.filter(task=task).order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = self.get_task(request, task_id)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(task=task, author=request.user)
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class TaskCommentDetailView(APIView):
    """
    Delete comments owned by the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        IsBoardMemberOrOwner,
        IsCommentAuthor,
    ]

    def delete(self, request, task_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
