from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow, Photo, Post, Profile
from .serializers import PostSerializer, ProfileSerializer


def _mini_insta_authentication():
    """Task 1: set MINI_INSTA_API_REQUIRE_AUTH False for open API. Task 3: True + token."""
    if getattr(settings, "MINI_INSTA_API_REQUIRE_AUTH", True):
        return [TokenAuthentication]
    return []


def _mini_insta_permission():
    if getattr(settings, "MINI_INSTA_API_REQUIRE_AUTH", True):
        return [IsAuthenticated]
    return [AllowAny]


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            profile = Profile.objects.get(user=user)
            return Response(
                {
                    "token": token.key,
                    "profile_id": profile.id,
                }
            )
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class ProfileListView(APIView):
    authentication_classes = _mini_insta_authentication()
    permission_classes = _mini_insta_permission()

    def get(self, request):
        profiles = Profile.objects.all()
        return Response(ProfileSerializer(profiles, many=True).data)


class ProfileDetailView(APIView):
    authentication_classes = _mini_insta_authentication()
    permission_classes = _mini_insta_permission()

    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        return Response(ProfileSerializer(profile).data)


class ProfilePostsView(APIView):
    authentication_classes = _mini_insta_authentication()
    permission_classes = _mini_insta_permission()

    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
        posts = Post.objects.filter(profile=profile).order_by("-timestamp")
        return Response(
            PostSerializer(posts, many=True, context={"request": request}).data
        )


class FeedView(APIView):
    authentication_classes = _mini_insta_authentication()
    permission_classes = _mini_insta_permission()

    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        following_ids = Follow.objects.filter(follower=profile).values_list(
            "following", flat=True
        )
        posts = Post.objects.filter(profile__id__in=following_ids).order_by("-timestamp")
        return Response(
            PostSerializer(posts, many=True, context={"request": request}).data
        )


class PostCreateView(APIView):
    authentication_classes = _mini_insta_authentication()
    permission_classes = _mini_insta_permission()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        profile_id = request.data.get("profile")
        if profile_id is None:
            return Response({"error": "profile is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = Profile.objects.get(pk=profile_id)
        except (Profile.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid profile"}, status=status.HTTP_400_BAD_REQUEST)

        if getattr(settings, "MINI_INSTA_API_REQUIRE_AUTH", True) and request.user.is_authenticated:
            if profile.user_id != request.user.id:
                return Response(
                    {"error": "You may only create posts for your own profile."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        caption = request.data.get("caption", "") or ""
        post = Post.objects.create(profile=profile, caption=caption)

        # Match web add_post: support `image` (mobile) or multiple `files` (browser-style)
        for f in request.FILES.getlist("files"):
            Photo.objects.create(post=post, image_file=f)
        single = request.FILES.get("image")
        if single:
            Photo.objects.create(post=post, image_file=single)

        return Response(
            PostSerializer(post, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
