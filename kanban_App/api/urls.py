from django.urls import path

from .views import (
    BoardView,
    DetailBoardView,
    EmailCheckView,
    UserTaskView,
    TaskView,
    TaskDetailView,
    TaskCommentView,
    TaskCommentDetailView,
)

urlpatterns = [
    path("boards/", BoardView.as_view()),
    path("boards/<int:board_id>/", DetailBoardView.as_view()),
    path("email-check/", EmailCheckView.as_view()),
    path(
        "tasks/assigned-to-me/", UserTaskView.as_view(), {"task_type": "assigned-to-me"}
    ),
    path("tasks/reviewing/", UserTaskView.as_view(), {"task_type": "reviewing"}),
    path("tasks/", TaskView.as_view()),
    path("tasks/<int:task_id>/", TaskDetailView.as_view()),
    path("tasks/<int:task_id>/comments/", TaskCommentView.as_view()),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        TaskCommentDetailView.as_view(),
    ),
]
