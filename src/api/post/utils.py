from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .serializers.serializers import PostSerializer


def handle_get_post(request, post):
    serializer = PostSerializer(post)
    return Response(serializer.data)

def handle_patch_post(request, post):
    if post.user != request.user:
        return Response({"detail": "You do not have permission to edit this post."}, status=status.HTTP_403_FORBIDDEN)

    serializer = PostSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "An unexpected error occurred while updating the post."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def handle_delete_post(request, post):
    if post.user != request.user:
        return Response({"detail": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)

    post.deleted_at = timezone.now()
    post.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


METHOD_HANDLERS = {
    'GET': handle_get_post,
    'PATCH': handle_patch_post,
    'DELETE': handle_delete_post,
 }