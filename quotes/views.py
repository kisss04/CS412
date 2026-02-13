#from django.shortcuts import render

# Create your views here.

#def quote(request):
#    """View for displaying a quote."""
 #   return render(request, 'quotes/quote.html')

#def show_all(request):
#    """View for showing all quotes."""
#    return render(request, 'quotes/show_all.html')

#def about(request):
 #   """View for the about page."""
#    return render(request, 'quotes/about.html')

from django.shortcuts import render
import random

quotes = [
    "You Don't Need a License to Drive a Sandwich.",
    "I Don't Need It. I Don't Need It. I DEFINITELY Don't Need It... I NEED IT!",
    "Is Mayonnaise an Instrument?",
]

images = [
    "https://i.ytimg.com/vi/9qVn-X4gsHk/maxresdefault.jpg",
    "https://i.ytimg.com/vi/UxYkB3BE5HE/maxresdefault.jpg",
    "https://i.imgflip.com/yytnx.jpg?a491760",
]

def quote(request):
    context = {
        "quote": random.choice(quotes),
        "image": random.choice(images),
    }
    return render(request, "quotes/quote.html", context)

def show_all(request):
    context = {
        "quotes": quotes,
        "images": images,
    }
    return render(request, "quotes/show_all.html", context)

def about(request):
    return render(request, "quotes/about.html")
