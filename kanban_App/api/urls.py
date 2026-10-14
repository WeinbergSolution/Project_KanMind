from django.urls import path
from .views import BoardView, DetailBoardView

urlpatterns = [
    path("boards/", BoardView.as_view()),
    path("boards/<int:board_id>/", DetailBoardView.as_view()),
]
