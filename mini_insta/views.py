from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .models import Photo, Post, Profile


class ProfileListView(ListView):
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

class PostDetailView(DetailView):
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"
    
def add_post(request, pk: int):
    profile = get_object_or_404(Profile, pk=pk)

    if request.method == "POST":
        caption = request.POST.get("caption", "").strip()
        files = request.FILES.getlist("files")  # uploaded images

        post = Post.objects.create(profile=profile, caption=caption)

        # Add uploaded files
        for f in files:
            Photo.objects.create(post=post, image_file=f)

        # Also handle image_url for backwards compatibility
        image_url = request.POST.get("image_url", "").strip()
        if image_url:
            Photo.objects.create(post=post, image_url=image_url)

        return redirect("show_profile", pk=profile.pk)

    return render(
        request,
        "mini_insta/add_post.html",
        {"profile": profile},
    )


def edit_profile(request, pk: int):
    profile = get_object_or_404(Profile, pk=pk)
    if request.method == "POST":
        profile.display_name = request.POST.get("display_name", profile.display_name)
        profile.profile_image_url = request.POST.get(
            "profile_image_url", profile.profile_image_url
        )
        profile.bio_text = request.POST.get("bio_text", profile.bio_text)
        profile.save()
        return redirect("show_profile", pk=profile.pk)

    return render(
        request,
        "mini_insta/edit_profile.html",
        {"profile": profile},
    )


def edit_post(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    photos = post.get_all_photos()

    if request.method == "POST":
        caption = request.POST.get("caption", "").strip()
        post.caption = caption
        post.save()

        # Handle uploaded files
        files = request.FILES.getlist("files")
        for f in files:
            Photo.objects.create(post=post, image_file=f)

        # Handle image_url input (for old posts)
        image_url = request.POST.get("image_url", "").strip()
        if image_url:
            first_photo = photos.first()
            if first_photo and not first_photo.image_file:
                first_photo.image_url = image_url
                first_photo.save()
            elif not first_photo:
                Photo.objects.create(post=post, image_url=image_url)

        return redirect("show_profile", pk=post.profile.pk)

    first_photo = photos.first()
    image_url = first_photo.image_url if first_photo else ""

    return render(
        request,
        "mini_insta/edit_post.html",
        {"post": post, "image_url": image_url},
    )


def delete_post(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    profile_pk = post.profile.pk

    if request.method == "POST":
        post.delete()
        return redirect("show_profile", pk=profile_pk)

    return render(
        request,
        "mini_insta/confirm_delete_post.html",
        {"post": post},
    )