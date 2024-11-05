from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.core.validators import validate_email

from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["PATCH"]:
            fields = {"name": fields["name"]}
        return fields





class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            validate_email,
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        password2 = validated_data["password2"]
        email = validated_data["email"]
        if password != password2:
            raise serializers.ValidationError({"password": "The passwords do not match."})
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
