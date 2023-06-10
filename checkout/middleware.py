from django.contrib import messages
from django.core.signing import BadSignature, Signer
from django.utils.functional import SimpleLazyObject, empty
from django.utils.translation import gettext_lazy as _

from .models import *


class CartMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Keep track of cookies that need to be deleted (which can only be done
        # when we're processing the response instance).
        request.cookies_to_delete = []

        # We lazily load the cart so use a private variable to hold the
        # cached instance.
        request._cart_cache = None

        def load_full_cart():
            """
            Return the cart after applying offers.
            """
            cart = self.get_cart(request)

            return cart

        def load_cart_hash():
            """
            Load the cart and return the cart hash
            Note that we don't apply offers or check that every line has a
            stockrecord here.
            """
            cart = self.get_cart(request)
            if cart.id:
                return self.get_cart_hash(cart.id)

        # Use Django's SimpleLazyObject to only perform the loading work
        # when the attribute is accessed.
        request.cart = SimpleLazyObject(load_full_cart)
        request.cart_hash = SimpleLazyObject(load_cart_hash)

        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        # Delete any surplus cookies
        cookies_to_delete = getattr(request, 'cookies_to_delete', [])
        for cookie_key in cookies_to_delete:
            response.delete_cookie(cookie_key)

        if not hasattr(request, 'cart'):
            return response

        # If the cart was never initialized we can safely return
        if (isinstance(request.cart, SimpleLazyObject)
                and request.cart._wrapped is empty):
            return response
        cookie_key = self.get_cookie_key()
        # Check if we need to set a cookie. If the cookies is already available
        # but is set in the cookies_to_delete list then we need to re-set it.
        has_cart_cookie = (
                cookie_key in request.COOKIES
                and cookie_key not in cookies_to_delete)
        # If a cart has had products added to it, but the user is anonymous
        # then we need to assign it to a cookie
        if (request.cart.id and not request.user.is_authenticated
                and not has_cart_cookie):
            cookie = self.get_cart_hash(request.cart.id)
            response.set_cookie(
                cookie_key, cookie,
                max_age=settings.CART_COOKIE_LIFETIME,
                secure=settings.CART_COOKIE_SECURE, httponly=True)
        return response

    @staticmethod
    def get_cookie_key():
        """
        Returns the cookie name to use for storing a cookie cart.
        The method serves as a useful hook in multi-site scenarios where
        different carts might be needed.
        """
        return settings.CART_COOKIE_OPEN

    # Cannot be a staticmethod
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            if response.context_data is None:
                response.context_data = {}
            if 'cart' not in response.context_data:
                response.context_data['cart'] = request.cart
            else:
                # Occasionally, a view will want to pass an alternative cart
                # to be rendered.  This can happen as part of checkout
                # processes where the submitted cart is frozen when the
                # customer is redirected to another site (eg PayPal).  When the
                # customer returns and we want to show the order preview
                # template, we need to ensure that the frozen cart gets
                # rendered (not request.cart).  We still keep a reference to
                # the request cart (just in case).
                response.context_data['request_cart'] = request.cart
        return response

    # Helper methods

    def get_cart(self, request):
        """
        Return the open cart for this request
        """
        if request._cart_cache is not None:
            return request._cart_cache

        site = request.site
        num_carts_merged = 0
        manager = Cart.open
        cookie_key = self.get_cookie_key()
        cookie_cart = self.get_cookie_cart(cookie_key, request, manager)
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Signed-in user: if they have a cookie cart too, it means
            # that they have just signed in, and we need to merge their cookie
            # cart into their user cart, then delete the cookie.
            try:
                cart, __ = manager.get_or_create(owner=request.user, site=site)
            except Cart.MultipleObjectsReturned:
                # Not sure quite how we end up here with multiple carts.
                # We merge them and create a fresh one
                old_carts = list(manager.filter(owner=request.user, site=site))
                cart = old_carts[0]
                for other_cart in old_carts[1:]:
                    self.merge_carts(cart, other_cart)
                    num_carts_merged += 1

            # Assign user onto cart to prevent further SQL queries when
            # cart.owner is accessed.
            cart.owner = request.user

            if cookie_cart:
                self.merge_carts(cart, cookie_cart)
                num_carts_merged += 1
                request.cookies_to_delete.append(cookie_key)

        elif cookie_cart:
            # Anonymous user with a cart tied to the cookie
            cart = cookie_cart
        else:
            # Anonymous user with no cart - instantiate a new cart
            # instance.  No need to save yet.
            cart = Cart(site=site)

        # Cache cart instance for the duration of this request
        request._cart_cache = cart

        if num_carts_merged > 0:
            messages.add_message(request, messages.WARNING,
                                 _("We have merged a cart from a previous session. Its contents "
                                   "might have changed."))
        return cart

    @staticmethod
    def merge_carts(new, old):
        """
        Merge one cart into another.
        This is its own method to allow it to be overridden
        """
        new.merge(old, add_quantities=True)

    @staticmethod
    def get_cookie_cart(cookie_key, request, manager):
        """
        Looks for a cart which is referenced by a cookie.
        If a cookie key is found with no matching cart, then we add
        it to the list to be deleted.
        """
        cart = None
        if cookie_key in request.COOKIES:
            cart_hash = request.COOKIES[cookie_key]
            try:
                cart_id = Signer().unsign(cart_hash)
                cart = manager.get(pk=cart_id, owner=None, site=request.site)
            except (BadSignature, Cart.DoesNotExist):
                request.cookies_to_delete.append(cookie_key)
        return cart

    @staticmethod
    def get_cart_hash(cart_id):
        return Signer().sign(cart_id)
