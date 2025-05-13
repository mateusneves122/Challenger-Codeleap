from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from ..models import User
import hashlib

class UserSerializer(serializers.ModelSerializer):
    name = serializers.RegexField(
        regex=r'^[A-Za-zÀ-ÖØ-öø-ÿ ]+$',
        max_length=100,
        min_length=2,
        error_messages={'invalid': 'Name invalid.'},
        help_text='Only letters and spaces',
    )

    email = serializers.EmailField(
        max_length=100,
        min_length=2,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Email already in use'
            )
        ]
    )

    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        max_length=20,
        min_length=6,
        error_messages={
            'min_length': 'Password must be at least 6 characters long.',
            'max_length': 'Password cannot be longer than 20 characters.'
        },
        required=True
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def create(self, data):
        password = data.pop('password')
        data['password_hash'] = hashlib.md5(password.encode()).hexdigest()
        user = User.objects.create(**data)
        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password')
        if password:
            instance.password_hash = hashlib.md5(password.encode()).hexdigest()
        instance.save()
        return instance