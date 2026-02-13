from django.shortcuts import render


def main(request):
    """Main restaurant page."""
    return render(request, "restaurant/main.html")


#def order(request):
#    """Order form page."""
#    return render(request, "restaurant/order.html")


def confirmation(request):
    """Order confirmation page."""
    return render(request, "restaurant/confirmation.html")


import random

def order(request):
    # Daily special (randomly pick one)
    specials = [
        {"name": "Spicy Chicken Wrap", "price": 7, "description": "Extra spicy today!"},
        {"name": "Hot Sauce Surprise", "price": 6, "description": "You bet your ass it's hot sauce"},
        {"name": "Veggie Deluxe", "price": 5, "description": "Loaded with fresh veggies!"}
    ]
    daily_special = random.choice(specials)
    
    context = {
        "daily_special": daily_special
    }
    return render(request, 'restaurant/order.html', context)
