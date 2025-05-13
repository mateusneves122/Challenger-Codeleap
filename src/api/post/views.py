from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from .serializers.serializers import PostSerializer
from .models import Post
from api.user.models import User

from .utils import METHOD_HANDLERS
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@extend_schema(
    summary="Create a new post",
    description="Creates a new post for the authenticated user. The 'content' field is required.",
    request=PostSerializer,
    parameters=[
        OpenApiParameter(
            name='Authorization',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description='Bearer authentication token. Format: "Bearer &lt;seu_token&gt;"',
            examples=[OpenApiExample(name='Example', value='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')], # Opcional: Adicionar um exemplo
        )
    ],
    responses={
        201: OpenApiResponse(
            response=PostSerializer,
            description="Post created successfully."
        ),
        400: OpenApiResponse(
            description="Invalid data provided (e.g., missing 'content').",
            examples=[
                OpenApiExample(
                    name="ValidationErrorExample",
                    value={"content": ["This field is required."]}
                )
            ]
        ),
        500: OpenApiResponse(description="An unexpected error occurred while creating the post.")
    },
    tags=['Posts']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():

        try:
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": "An unexpected error occurred while creating the post."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="List posts by a specific user",
    description="Retrieves all non-deleted posts created by a specific user, ordered by creation date (newest first).",
    parameters=[
        OpenApiParameter(
            name='user_id',
            description='The ID of the user whose posts are to be retrieved.',
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH
        ),
        OpenApiParameter(
            name='Authorization',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description='Bearer authentication token. Format: "Bearer &lt;seu_token&gt;"',
            examples=[OpenApiExample(name='Example', value='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')], # Opcional: Adicionar um exemplo
        )
    ],
    responses={
        200: OpenApiResponse(
            response=PostSerializer(many=True), # Indica que é uma lista de posts
            description="A list of posts by the specified user."
        ),
        400: OpenApiResponse(description="Invalid user ID format."),
        404: OpenApiResponse(description="User not found.")
    },
    tags=['Posts']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_posts(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"detail": "Invalid user ID format."}, status=status.HTTP_400_BAD_REQUEST)

    posts = Post.objects.filter(user=user, deleted_at__isnull=True).order_by('-created_at')

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='post_id',
            description='The ID of the post to operate on.',
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH
        ),
        OpenApiParameter(
            name='Authorization',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description='Bearer authentication token. Format: "Bearer &lt;seu_token&gt;"',
            examples=[OpenApiExample(name='Example', value='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')], # Opcional: Adicionar um exemplo
        )
    ],
    tags=['Posts']
)

@extend_schema(
    methods=['GET'],
    summary="View a specific post",
    description="Retrieves the details of an existing post by its ID.",
    responses={
        200: OpenApiResponse(response=PostSerializer, description="Detalhes do post."),
        404: OpenApiResponse(description="Post não encontrado.", response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}),
        400: OpenApiResponse(description="ID do post inválido.", response={'type': 'object', 'properties': {'detail': {'type': 'string'}}})
    }
)

@extend_schema(
    methods=['PATCH'],
    summary="Update a specific post",
    description="Updates some fields of an existing publication. Only the provided fields will be updated..",
    request=PostSerializer,
    responses={
        200: OpenApiResponse(response=PostSerializer, description="Post updated successfully."),
        400: OpenApiResponse(description="Invalid data.", response={'type': 'object', 'properties': {'detail': {'type': 'string'}}}), # Adicione mais detalhes se tiver um serializer de erro
        404: OpenApiResponse(description="Post not found.", response={'type': 'object', 'properties': {'detail': {'type': 'string'}}})
    }
)

@extend_schema(
    methods=['DELETE'],
    summary="Delete a specific post",
    description="Remove an existing post from the system.",
    responses={
        204: OpenApiResponse(description=""),
        404: OpenApiResponse(description="Post not found.", response={'type': 'object', 'properties': {'detail': {'type': 'string'}}})
    }
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def post_detail_operations(request, post_id: int):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
    except Post.DoesNotExist:
        return Response({"detail": "Post not found or has been deleted."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"detail": "Invalid post ID format."}, status=status.HTTP_400_BAD_REQUEST)

    handler = METHOD_HANDLERS.get(request.method)
    if handler:
        return handler(request, post)
    else:
        return Response({"detail": f"Method \"{request.method}\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)