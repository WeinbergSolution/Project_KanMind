from rest_framework.permissions import BasePermission


class IsBoardMemberOrOwner(BasePermission):
    """
    Allow access to board owners and members.
    """

    message = "You must be a board member or owner to perform this action."

    def has_object_permission(self, request, view, obj):
        board = obj.board if hasattr(obj, "board") else obj
        is_owner = board.owner_id == request.user
        is_member = board.members.filter(id=request.user.id).exists()
        return is_owner or is_member


class IsTaskCreatorOrBoardOwner(BasePermission):
    """
    Allow task deletion by the creator or board owner.
    """

    message = "Only the task creator or board owner can delete this task."

    def has_object_permission(self, request, view, obj):
        is_creator = obj.created_by == request.user
        is_owner = obj.board.owner_id == request.user
        return is_creator or is_owner
