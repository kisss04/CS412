from rest_framework import serializers

from .models import Photo, Post, Profile


class PhotoSerializer(serializers.ModelSerializer):
    """Picture URL suitable for mobile clients (absolute when request in context)."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "url", "timestamp"]

    def get_url(self, obj: Photo) -> str | None:
        raw = obj.get_image_url()
        if not raw:
            return None
        s = str(raw)
        if s.startswith("http://") or s.startswith("https://"):
            return s
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(s)
        return s


class PostSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "profile", "timestamp", "caption", "photos", "primary_image"]

    def get_primary_image(self, obj: Post) -> str | None:
        first = obj.get_all_photos().first()
        if not first:
            return None
        payload = PhotoSerializer(first, context=self.context).data
        return dict(payload).get("url")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
