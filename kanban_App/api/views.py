from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from kanban_App.api.serializers import (
    BoardSerializer,
    DetailBoardSerializer,
    UserSerializer,
    TaskSerializer,
    CommentSerializer,
)
from rest_framework.response import Response
from django.db.models import Q
from kanban_App.models import Board, Task, Comment
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


# Postview
class BoardView(APIView):
    """
    View to Create Board
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Post Mehode
        """
        in_serializer = BoardSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        board = in_serializer.save(owner_id=request.user)
        out_serializer = BoardSerializer(board)
        return Response(data=out_serializer.data, status=201)

    def get(self, request):
        """
        Get all boards of the authenticated user
        """
        boards = Board.objects.filter(
            Q(owner_id=request.user) | Q(members=request.user)
        ).distinct()

        out_serializer = BoardSerializer(boards, many=True)

        return Response(data=out_serializer.data)


class DetailBoardView(APIView):
    """
    Method for Detail Action
    """

    def get(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        is_owner = board.owner_id == user
        is_member = board.members.filter(id=user.id).exists()

        if not (is_owner or is_member):
            raise PermissionDenied("Kein Zugriff auf das Board")

        out_serializer = DetailBoardSerializer(board)
        return Response(out_serializer.data)

    def patch(self, request, board_id):

        board = get_object_or_404(Board, id=board_id)

        if board.owner_id != request.user:
            raise PermissionDenied("Keine Berechtigung, das Board zu ändern")

        serializer = DetailBoardSerializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, board_id):

        board = get_object_or_404(Board, id=board_id)

        if board.owner_id != request.user:
            raise PermissionDenied("Keine Berechtigung, das Board zu löschen!")

        board.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            raise ValidationError("No email address entered")

        user = get_object_or_404(User, email=email)

        serializer = UserSerializer(user)

        return Response(serializer.data)


class UserTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_type):
        if task_type == "assigned-to-me":
            tasks = Task.objects.filter(assignee=request.user)

        elif task_type == "reviewing":
            tasks = Task.objects.filter(reviewer=request.user)

        else:
            return Response({"detail": "Unbekannter Task-Typ."}, status=404)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        in_serializer = TaskSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        board = in_serializer.validated_data["board"]

        # Prüfen, ob der angemeldete Benutzer Board-Mitglied ist
        is_owner = board.owner_id == request.user
        is_member = board.members.filter(id=request.user.id).exists()

        if not (is_owner or is_member):
            raise PermissionDenied("Kein Zugriff auf das Board")

        # Zugewiesenen Assignee auslesen
        assignee = in_serializer.validated_data.get("assignee")

        # Prüfen, ob der Assignee Mitglied des Boards ist
        if assignee:
            is_owner = board.owner_id == assignee
            is_member = board.members.filter(id=assignee.id).exists()

            if not (is_owner or is_member):
                raise PermissionDenied(
                    "Der Assignee ist weder Eigentümer noch Mitglied des Boards!"
                )

        reviewer = in_serializer.validated_data.get("reviewer")

        if reviewer:
            is_owner = board.owner_id == reviewer
            is_member = board.members.filter(id=reviewer.id).exists()

            if not (is_owner or is_member):
                raise PermissionDenied(
                    "Der Reviewer ist weder Eigentümer noch Mitglied des Boards!"
                )

        task = in_serializer.save(created_by=request.user)
        out_serializer = TaskSerializer(task)
        return Response(data=out_serializer.data, status=201)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        board = task.board

        is_member = board.members.filter(id=request.user.id).exists()

        if not is_member:
            raise PermissionDenied(
                "Sie sind kein Mitglied des Boards, Berechtigung fehlt!"
            )

        serializer = TaskSerializer(task, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        new_board = serializer.validated_data.get("board")

        if new_board is not None and new_board != board:
            raise ValidationError(
                "Ein Task darf nicht auf ein anderes Board verschoben werden!"
            )

        assignee = serializer.validated_data.get("assignee")

        if assignee is not None:
            is_assignee_member = board.members.filter(id=assignee.id).exists()

            if not is_assignee_member:
                raise ValidationError(
                    {"assignee_id": "Der Assignee ist kein Mitglied des Boards!"}
                )

        reviewer = serializer.validated_data.get("reviewer")

        if reviewer is not None:
            is_reviewer_member = board.members.filter(id=reviewer.id).exists()

            if not is_reviewer_member:
                raise ValidationError(
                    {"reviewer_id": "Der Reviewer ist kein Mitglied des Boards!"}
                )

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        board = task.board

        is_owner = board.owner_id == request.user

        is_creator = hasattr(task, "created_by") and task.created_by == request.user

        if not (is_owner or is_creator):
            raise PermissionDenied(
                "Nur der Task-Ersteller oder Board-Eigentümer darf diesen Task löschen!"
            )

        task.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        comments = Comment.objects.filter(task=task).order_by("created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        in_serializer = CommentSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)

        comment = in_serializer.save(task=task, author=request.user)

        out_serializer = CommentSerializer(comment)

        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class TaskCommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, comment_id):
        taskcomment = get_object_or_404(Comment, id=comment_id, task_id=task_id)

        if taskcomment.author != request.user:
            raise PermissionDenied("Nur der Autor darf diesen Kommentar löschen!")

        taskcomment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
