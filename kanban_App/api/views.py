from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from kanban_App.api.serializers import (
    BoardSerializer,
    DetailBoardSerializer,
    UserSerializer,
)
from rest_framework.response import Response
from django.db.models import Q
from kanban_App.models import Board
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
