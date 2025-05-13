from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from api.user.models import User
import hashlib

class EmailTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    default_error_messages = {
        'no_active_account': _('Nenhuma conta ativa encontrada com as credenciais fornecidas.')
    }

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
            expected_password_hash = hashlib.md5(password.encode()).hexdigest()
            if user.password_hash != expected_password_hash:
                raise serializers.ValidationError(
                    self.error_messages['no_active_account'],
                    code='authorization',
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['no_active_account'],
                code='authorization',
            )

        attrs['user'] = user
        return attrs