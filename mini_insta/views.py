from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from .models import Photo, Post, Profile, Follow, Like
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse
from .forms import CreateProfileForm


class LogoutConfirmationView(TemplateView):
    template_name = "mini_insta/logged_out.html"


class AuthRequiredMixin(LoginRequiredMixin):
    login_url = "/mini_insta/login/"


class ProfileListView(ListView):
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        posts = profile.get_all_posts()

        for post in posts:
            post.liked_by_user = False
            if self.request.user.is_authenticated:
                post.liked_by_user = post.like_set.filter(
                    profile=self.request.user.profile
                ).exists()

        context["posts"] = posts
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"



@login_required(login_url='/mini_insta/login/')
def add_post(request):

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        caption = request.POST.get("caption", "")
        files = request.FILES.getlist("files")

        post = Post.objects.create(profile=profile, caption=caption)

        for f in files:
            Photo.objects.create(post=post, image_file=f)

        return redirect("mini_insta:show_profile", pk=profile.pk)

    return render(request,"mini_insta/add_post.html")


@login_required(login_url='/mini_insta/login/')
def edit_profile(request):

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        profile.display_name = request.POST.get("display_name", profile.display_name)
        profile.profile_image_url = request.POST.get(
            "profile_image_url", profile.profile_image_url
        )
        profile.bio_text = request.POST.get("bio_text", profile.bio_text)

        profile.save()

        return redirect("mini_insta:show_profile", pk=profile.pk)

    return render(
        request,
        "mini_insta/edit_profile.html",
        {"profile": profile},
    )


@login_required(login_url='/mini_insta/login/')
def edit_post(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    photos = post.get_all_photos()

    if request.method == "POST":
        caption = request.POST.get("caption", "").strip()
        post.caption = caption
        post.save()

        files = request.FILES.getlist("files")
        for f in files:
            Photo.objects.create(post=post, image_file=f)

        image_url = request.POST.get("image_url", "").strip()
        if image_url:
            first_photo = photos.first()
            if first_photo and not first_photo.image_file:
                first_photo.image_url = image_url
                first_photo.save()
            elif not first_photo:
                Photo.objects.create(post=post, image_url=image_url)

        return redirect("mini_insta:show_profile", pk=post.profile.pk)

    first_photo = photos.first()
    image_url = first_photo.image_url if first_photo else ""

    return render(
        request,
        "mini_insta/edit_post.html",
        {"post": post, "image_url": image_url},
    )



@login_required(login_url='/mini_insta/login/')
def delete_post(request, pk: int):
    post = get_object_or_404(Post, pk=pk)
    profile_pk = post.profile.pk

    if request.method == "POST":
        post.delete()
        return redirect("mini_insta:show_profile", pk=profile_pk)

    return render(
        request,
        "mini_insta/confirm_delete_post.html",
        {"post": post},
    )


class CreateProfileView(CreateView):

    model = Profile
    form_class = CreateProfileForm
    template_name = "mini_insta/create_profile_form.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["user_form"] = UserCreationForm()

        return context

    def form_valid(self, form):

        user_form = UserCreationForm(self.request.POST)

        if user_form.is_valid():

            user = user_form.save()

            login(
                self.request,
                user,
                backend='django.contrib.auth.backends.ModelBackend'
            )

            form.instance.user = user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mini_insta:show_profile', kwargs={'pk': self.object.pk})


@login_required(login_url='/mini_insta/login/')
def follow_profile(request, pk):

    me = Profile.objects.get(user=request.user)
    other = Profile.objects.get(pk=pk)

    if me != other:
        Follow.objects.create(follower=me, following=other)

    return redirect('mini_insta:show_profile', pk=pk)


@login_required(login_url='/mini_insta/login/')
def like_post(request, pk):

    profile = Profile.objects.get(user=request.user)
    post = Post.objects.get(pk=pk)

    if post.profile != profile:
        Like.objects.create(profile=profile, post=post)

    return redirect('mini_insta:show_profile', pk=post.profile.pk)

from django.contrib.auth.decorators import login_required

@login_required(login_url='/mini_insta/login/')
def my_profile(request):

    profile = Profile.objects.get(user=request.user)

    return redirect("mini_insta:show_profile", pk=profile.pk)

@login_required(login_url='/mini_insta/login/')
def delete_follow_profile(request, pk):

    me = Profile.objects.get(user=request.user)
    other = Profile.objects.get(pk=pk)

    Follow.objects.filter(follower=me, following=other).delete()

    return redirect("mini_insta:show_profile", pk=pk)

@login_required(login_url='/mini_insta/login/')
def delete_like_post(request, pk):

    profile = Profile.objects.get(user=request.user)
    post = Post.objects.get(pk=pk)

    Like.objects.filter(profile=profile, post=post).delete()

    return redirect("mini_insta:show_profile", pk=post.profile.pk)


def login_view(request):
    return render(request, 'mini_insta/login.html')