from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="first_name", read_only=True)
    dateJoined = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "fullName",
            "email",
            "dateJoined",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    fullName = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )
    confirmPassword = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists.",
            )

        return email

    def validate(self, attrs):
        full_name = attrs["fullName"].strip()
        email = attrs["email"]
        password = attrs["password"]
        confirm_password = attrs["confirmPassword"]

        if not full_name:
            raise serializers.ValidationError(
                {"fullName": "Full name is required."},
            )

        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirmPassword": (
                        "Password confirmation does not match."
                    ),
                },
            )

        temporary_user = User(
            username=email,
            email=email,
            first_name=full_name,
        )

        try:
            validate_password(password, user=temporary_user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)},
            ) from error

        attrs["fullName"] = full_name
        return attrs

    def create(self, validated_data):
        full_name = validated_data.pop("fullName")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        validated_data.pop("confirmPassword")

        try:
            with transaction.atomic():
                return User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=full_name,
                    password=password,
                )
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    "email": (
                        "An account with this email already exists."
                    ),
                },
            ) from error


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]

        user = User.objects.filter(email__iexact=email).first()

        if (
            user is None
            or not user.check_password(password)
            or not user.is_active
        ):
            raise AuthenticationFailed("Invalid email or password.")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }
