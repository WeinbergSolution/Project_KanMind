from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """Allow access to board owners and members."""

    message = "You must be a board member or owner to perform this action."

    def has_object_permission(self, request, view, obj):
        """Check whether the user owns or belongs to the board."""
        if hasattr(obj, "board"):
            board = obj.board
        elif hasattr(obj, "task"):
            board = obj.task.board
        else:
            board = obj

        is_owner = board.owner_id == request.user
        is_member = board.members.filter(id=request.user.id).exists()
        return is_owner or is_member


class IsBoardOwner(BasePermission):
    """Allow access only to the board owner."""

    message = "Only the board owner can perform this action."

    def has_object_permission(self, request, view, obj):
        """Check whether the user owns the board."""
        return obj.owner_id == request.user


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Allow task deletion by its creator or the board owner."""

    message = "Only the task creator or board owner can delete this task."

    def has_object_permission(self, request, view, obj):
        """Check whether the user created the task or owns its board."""
        is_creator = obj.created_by == request.user
        is_owner = obj.board.owner_id == request.user
        return is_creator or is_owner


class IsCommentAuthor(BasePermission):
    """Allow comment deletion only by its author."""

    message = "Only the comment author can delete this comment."

    def has_object_permission(self, request, view, obj):
        """Check whether the user authored the comment."""
        return obj.author == request.user
