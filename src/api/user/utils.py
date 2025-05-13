from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers.user_model_serializers import UserSerializer

def handle_get_user(request, user):
    serializer = UserSerializer(user)
    return Response(serializer.data)


def handle_patch_user(request, user):
    if user != request.user:
        return Response({"detail": "You do not have permission to edit this profile."}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def handle_delete_user(request, user):
    if user != request.user:
        return Response({"detail": "You do not have permission to delete this profile."}, status=status.HTTP_403_FORBIDDEN)

    if user.deleted_at is not None:
        return Response({"detail": "User already deleted."}, status=status.HTTP_400_BAD_REQUEST)

    user.deleted_at = timezone.now()
    user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


METHOD_HANDLERS = {
    'GET': handle_get_user,
    'PATCH': handle_patch_user,
    'DELETE': handle_delete_user,
}