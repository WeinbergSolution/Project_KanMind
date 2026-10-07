from django.contrib import admin

# Register your models here.
from kanban_App.models import Board, Task, Comment


@admin.register(Board)
class AdminBoard(admin.ModelAdmin):
    pass


@admin.register(Task)
class AdminTask(admin.ModelAdmin):
    pass


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    pass
