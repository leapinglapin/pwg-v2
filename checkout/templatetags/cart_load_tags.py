from django import template

register = template.Library()


@register.inclusion_tag('checkout/snippets/cart_preload_redux.html')
def preload_cart_into_redux_store(cart):
    return {
        'cart': cart
    }
