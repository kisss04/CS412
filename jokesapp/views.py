from django.shortcuts import render, get_object_or_404
from .models import Joke, Picture
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import JokeSerializer, PictureSerializer

def index(request):
    joke = random.choice(list(Joke.objects.all()))
    picture = random.choice(list(Picture.objects.all()))
    return render(request, 'jokesapp/index.html', {'joke': joke, 'picture': picture})


def jokes(request):
    return render(request, 'jokesapp/jokes.html', {'jokes': Joke.objects.all()})


def joke_detail(request, pk):
    joke = get_object_or_404(Joke, pk=pk)
    return render(request, 'jokesapp/joke_detail.html', {'joke': joke})


def pictures(request):
    return render(request, 'jokesapp/pictures.html', {'pictures': Picture.objects.all()})


def picture_detail(request, pk):
    picture = get_object_or_404(Picture, pk=pk)
    return render(request, 'jokesapp/picture_detail.html', {'picture': picture})




from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import JokeSerializer, PictureSerializer

@api_view(['GET'])
def api_random_joke(request):
    joke = random.choice(Joke.objects.all())
    return Response(JokeSerializer(joke).data)

@api_view(['GET'])
def api_all_jokes(request):
    jokes = Joke.objects.all()
    return Response(JokeSerializer(jokes, many=True).data)

@api_view(['GET', 'POST'])
def api_joke_detail(request, pk=None):
    if request.method == 'GET':
        joke = get_object_or_404(Joke, pk=pk)
        return Response(JokeSerializer(joke).data)

    if request.method == 'POST':
        serializer = JokeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

@api_view(['GET'])
def api_random_picture(request):
    picture = random.choice(Picture.objects.all())
    return Response(PictureSerializer(picture).data)

@api_view(['GET'])
def api_all_pictures(request):
    pictures = Picture.objects.all()
    return Response(PictureSerializer(pictures, many=True).data)

@api_view(['GET'])
def api_picture_detail(request, pk):
    picture = get_object_or_404(Picture, pk=pk)
    return Response(PictureSerializer(picture).data)