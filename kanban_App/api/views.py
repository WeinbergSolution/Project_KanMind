from rest_framework import viewsets
from .serializers import BoardSerializer, TaskSerializer
from kanban_App.models import Board, Task


class BoardViewSet(viewsets.ModelViewSet):

    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
