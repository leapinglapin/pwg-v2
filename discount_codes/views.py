from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from discount_codes.models import DiscountCode, CodeUsage


# Create your views here.


def apply_code(request, code):
    potential_codes = DiscountCode.objects.filter(code=code.lower())
    print(potential_codes)
    cart = request.cart
    if potential_codes.exists():
        next_page = request.GET.get("next")

        code = potential_codes.first()
        user = None
        if request.user.is_authenticated:
            user = request.user
        CodeUsage.objects.create(code=code, cart_id=cart.id, user=user)
        if code.validate_code_for_cart(cart):
            pass  # Validating the code saves it to the cart.
        else:
            next_page = reverse('view_cart')  # redirect user to page where they can see error message

        if request.method == "POST":
            return HttpResponse(status=200)
        if next_page is None:
            next_page = reverse('shop')
        return HttpResponseRedirect(next_page)
    cart.discount_code = None
    cart.discount_code_message = None
    cart.save()  # Clear code if we can't find the discount.
    return HttpResponse(status=400)
