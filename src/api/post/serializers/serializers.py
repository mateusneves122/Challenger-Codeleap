from rest_framework import serializers
from ..models import Post
from api.user.models import User

class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class PostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(
        error_messages={
            'required': 'The content field is required. Please provide the post content.',
            'blank': 'The content cannot be blank.',
        }
    )

    title = serializers.CharField(
        max_length=100,
        error_messages={
            'required': 'The title field is required. Please provide a title for the post.',
            'blank': 'The title cannot be blank.',
            'max_length': 'The title cannot be longer than {max_length} characters.'
        }
    )

    image_url = serializers.URLField(
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid': 'The provided image URL is not valid. Please enter a URL in the correct format (e.g., http://example.com/image.jpg).',
            'max_length': 'The image URL cannot be longer than {max_length} characters.'
        }
    )

    user = PostAuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image_url', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']