from rest_framework import serializers
from .models import LandingScreenshot

class LandingScreenshotSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = LandingScreenshot
        fields = ['key', 'title', 'image_url', 'alt_text', 'sort_order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
