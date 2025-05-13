from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers.user_model_serializers import UserSerializer
from .models import User
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import METHOD_HANDLERS

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema(
    summary="Create a new user",
    description="Registers a new user in the system. Email must be unique.",
    request=UserSerializer,
    responses={
        201: OpenApiResponse(description="User created successfully!!", examples=[
            OpenApiExample(
                name="Test",
                value={"message": "User created successfully!"}
            )
        ]),
        400: OpenApiResponse(description="Invalid data provided.")
    },
    tags=['Users']
)
@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([AllowAny])
def post_user(request):
    data = request.data
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='The ID of the user to operate on.',
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
    tags=['Users']
)

@extend_schema(
    methods=['GET'],
    summary="View a specific user",
    description="Retrieves the details of an existing user by their ID.",
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description="User details retrieved successfully."
        ),
        400: OpenApiResponse(
            description="Invalid user ID format.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        404: OpenApiResponse(
            description="User not found.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
    }
)

@extend_schema(
    methods=['PATCH'],
    summary="Update a specific user",
    description="Updates some fields of an existing user. Only the provided fields will be updated.",
    request=UserSerializer,
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description="User updated successfully."
        ),
        400: OpenApiResponse(
            description="Invalid data provided for update.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        404: OpenApiResponse(
            description="User not found.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
    }
)

@extend_schema(
    methods=['DELETE'],
    summary="Delete a specific user",
    description="Removes an existing user from the system.",
    responses={
        204: OpenApiResponse(
            description="User deleted successfully.",
            response=None
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
        404: OpenApiResponse(
            description="User not found.",
            response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}
        ),
    }
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def user_detail_operations(request, user_id: int):
    try:
        user = User.objects.get(id=user_id, deleted_at__isnull=True)
    except User.DoesNotExist:
        return Response({"detail": "User not found or has been deleted."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"detail": "Invalid user ID format."}, status=status.HTTP_400_BAD_REQUEST)

    handler = METHOD_HANDLERS.get(request.method)
    if handler:
        return handler(request, user)
    else:
        return Response({"detail": f"Method \"{request.method}\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
