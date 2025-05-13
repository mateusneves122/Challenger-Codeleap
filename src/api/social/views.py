from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from api.user.models import User
from .models import Follow
from .serializers.serializers import FollowSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="Follow a user",
    description="Allows the authenticated user to follow another user specified by their ID. No request body is needed.",
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='The ID of the user to follow.',
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH
        ),
        OpenApiParameter(
            name='Authorization',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description='Bearer authentication token. Format: "Bearer &lt;your_token&gt;"',
            examples=[OpenApiExample(name='Example Bearer Token', value='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1NzEwNjgzLCJpYXQiOjE3MTU3MDcwODMsImp0aSI6ImV4YW1wbGUiLCJ1c2VyX2lkIjoxfQ.exampletokenstring')],
        )
    ],
    request=None,
    responses={
        201: OpenApiResponse(
            response=FollowSerializer,
            description="Successfully followed the user."
        ),
        400: OpenApiResponse(
            description="Bad request (e.g., trying to follow self, or already following this user).",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        404: OpenApiResponse(
            description="User to follow not found.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        500: OpenApiResponse(
            description="An unexpected error occurred while trying to follow.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        )
    },
    tags=['Follows']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    follower_user = request.user

    if follower_user == user_to_follow:
        return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        follow_relation = Follow.objects.create(follower=follower_user, following=user_to_follow)
        serializer = FollowSerializer(follow_relation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": "An unexpected error occurred while trying to follow."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(
    summary="Unfollow a user",
    description="Allows the authenticated user to unfollow another user specified by their ID. No request body is needed.",
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='The ID of the user to unfollow.',
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH
        ),
        OpenApiParameter(
            name='Authorization',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description='Bearer authentication token. Format: "Bearer &lt;your_token&gt;"',
            examples=[OpenApiExample(name='Example Bearer Token', value='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1NzEwNjgzLCJpYXQiOjE3MTU3MDcwODMsImp0aSI6ImV4YW1wbGUiLCJ1c2VyX2lkIjoxfQ.exampletokenstring')],
        )
    ],
    request=None,
    responses={
        204: OpenApiResponse(
            description="",
            response=None
        ),
        400: OpenApiResponse(
            description="Bad request (e.g., you were not following this user).",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        404: OpenApiResponse(
            description="User to unfollow not found.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        )
    },
    tags=['Follows']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    follower_user = request.user

    deleted_count, _ = Follow.objects.filter(follower=follower_user, following=user_to_unfollow).delete()

    if deleted_count == 0:
        return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_204_NO_CONTENT)