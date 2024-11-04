from rest_framework import serializers

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