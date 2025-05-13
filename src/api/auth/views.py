from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers.auth_serializers import EmailTokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser

from drf_spectacular.utils import extend_schema,OpenApiResponse

@extend_schema(
    summary="Obtain Authentication Tokens",
    description="Authenticates a user with credentials provided in the request body (as defined by EmailTokenObtainSerializer) and returns new access and refresh tokens.",
    request=EmailTokenObtainSerializer,
    responses={
        200: OpenApiResponse(
            description="Authentication successful. Access and refresh tokens provided.",
            response={'type': 'object', 'properties': {
                'user_id': {'type': 'integer', 'description': 'ID of the authenticated user'},
                'access_token': {'type': 'string', 'description': 'Access token for API access'},
                'refresh_token': {'type': 'string', 'description': 'Refresh token to obtain new access tokens'}
            }}
        ),
        400: OpenApiResponse(
            description="Invalid credentials or bad request (e.g., missing fields, incorrect password). Error details might be provided in the response body.",
            response={'type': 'object', 'properties': {
                'field_name': {'type': 'array', 'items': {'type': 'string'}},
                'non_field_errors': {'type': 'array', 'items': {'type': 'string'}},
                'detail': {'type': 'string'}
            }}
        )
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def post_auth(request):
    serializer = EmailTokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)

    return Response({
        'user_id': user.id,
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }, status=status.HTTP_200_OK)
