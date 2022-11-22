import traceback

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from partner.models import get_partner_or_401
from shop.models import CustomChargeItem
from subscriptions.forms import UserDefaultAddressForm
from .forms import *
from .serializers import *


@csrf_exempt
def json_cart(request):
    response = CartSerializer(request.cart).data
    response['buttonItems'] = []
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            item_ids = data['buttonItems']
            for item in Item.objects.filter(id__in=item_ids):
                if isinstance(item, InventoryItem) and item.use_linked_inventory:
                    sq_item = item.squareinventoryitem_set.first()
                    sq_item.update_local_stock()
                response['buttonItems'].append(ItemSerializer(item, context={'cart': request.cart}).data)
        except KeyError:
            pass
    return JsonResponse(response)


@csrf_exempt
def add_to_cart(request, item_id, quantity=1):
    try:
        item = get_object_or_404(Item, id=item_id)
        line, _ = request.cart.add_item(item, quantity)
        if (isinstance(item, DigitalItem) or isinstance(item, PackItem)) \
                and item.pay_what_you_want and request.method == 'POST':
            print(request.body)
            body = json.loads(request.body)
            user_price = Money(Decimal(body['price']), "USD")
            if user_price >= item.price:
                try:
                    line.price_per_unit_override = user_price
                    print("Saved item at pwyw price!")
                    line.save()
                except KeyError:
                    pass
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
    return HttpResponse(status=400)


def remove_from_cart(request, item_id):
    try:
        request.cart.remove_from_cart(item_id)
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
    return HttpResponse(status=400)


def update_quantity(request, item_id, quantity):
    try:
        request.cart.update_quantity(item_id=item_id, quantity=quantity)
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)


def view_cart(request):
    return TemplateResponse(request, "checkout/view_cart.html")


def checkout_start(request):
    request.cart.freeze()
    context = {
        'next_view': request.cart.next_checkout_view(view=Cart.V_START, user=request.user),
    }
    return TemplateResponse(request, "checkout/checkout_start.html", context=context)


def checkout_delivery_method(request):
    '''
    This view allows the user to select a delivery method (in store pickup or shipping)
    and if in-store, which store to pick up from.
    :param request:
    :return:
    '''
    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse('checkout_start'))
    if not request.cart.is_account_set():
        return HttpResponseRedirect(reverse('checkout_login'))

    form = PickupForm(instance=request.cart)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PickupForm(request.POST, instance=request.cart)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            next_view = request.cart.next_checkout_view(view=Cart.V_DELIVERY_METHOD, user=request.user)

            return HttpResponseRedirect(reverse(next_view))

    context = {
        'form': form,
    }
    return TemplateResponse(request, "checkout/checkout_pickup_in_store.html", context=context)


def checkout_login(request):
    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse('checkout_start'))
    form = EmailForm(instance=request.cart)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EmailForm(request.POST, instance=request.cart)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            cart = request.cart
            code = cart.discount_code
            if code:
                code.validate_code_for_cart(cart)
            # redirect to a new URL:
            next_view = request.cart.next_checkout_view(view=Cart.V_LOGIN, user=request.user)

            return HttpResponseRedirect(reverse(next_view))

    context = {
        'form': form,
    }
    return TemplateResponse(request, "checkout/checkout_login.html", context=context)


def checkout_billing_addr(request):
    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse('checkout_start'))
    if not request.cart.is_account_set():
        return HttpResponseRedirect(reverse('checkout_login'))
    if not request.cart.is_shipping_set():
        return HttpResponseRedirect(reverse(Cart.V_DELIVERY_METHOD))

    billing_form = BillingAddressForm(instance=request.cart.billing_address)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        billing_form = BillingAddressForm(data=request.POST, instance=request.cart.billing_address)

        # check whether it's valid:
        if billing_form.is_valid():
            # process the data in form.cleaned_data as required
            request.cart.billing_address = billing_form.save()
            request.cart.tax_error = False
            request.cart.save()
            # redirect to a new URL:
            next_view = request.cart.next_checkout_view(view=Cart.V_BILLING_ADDRESS, user=request.user)

            return HttpResponseRedirect(reverse(next_view))

    context = {
        'billing_form': billing_form,
    }
    return TemplateResponse(request, "checkout/checkout_billing_addr.html", context=context)


def checkout_payment_method(request):
    '''
    This form asks the users for their payment method, and the store to pay in.
    :param request:
    :return: redirects to done
    '''
    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse('checkout_start'))
    if not request.cart.is_account_set():
        return HttpResponseRedirect(reverse('checkout_login'))
    if not request.cart.is_shipping_set():
        return HttpResponseRedirect(reverse(Cart.V_DELIVERY_METHOD))

    payment_form = PaymentMethodForm(instance=request.cart)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        payment_form = PaymentMethodForm(request.POST, instance=request.cart)

        # check whether it's valid:
        if payment_form.is_valid():
            # process the data in form.cleaned_data as required
            payment_form.save()
            # redirect to a new URL:
            next_view = request.cart.next_checkout_view(view=Cart.V_PAYMENT_METHOD, user=request.user)
            return HttpResponseRedirect(reverse(next_view))

    context = {
        'payment_form': payment_form,
    }
    return TemplateResponse(request, "checkout/checkout_payment_method.html", context=context)


def checkout_pay_online(request):
    '''
    This form allows the user to pay online via credit card
    :param request:
    :return:
    '''

    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse(Cart.V_START))
    if not request.cart.is_account_set():
        return HttpResponseRedirect(reverse(Cart.V_LOGIN))
    if not request.cart.is_shipping_set():
        return HttpResponseRedirect(reverse(Cart.V_DELIVERY_METHOD))
    if not request.cart.is_payment_method_set():
        return HttpResponseRedirect(reverse(Cart.V_PAYMENT_METHOD))
    if not request.cart.can_get_tax():
        return HttpResponseRedirect(reverse(Cart.V_BILLING_ADDRESS))

    request.cart.final_ship = request.cart.get_shipping()
    request.cart.final_tax = request.cart.get_tax(final=True)
    request.cart.final_total = request.cart.get_final_less_tax() + request.cart.final_tax
    request.cart.save()

    context = {
        'final_tax': request.cart.final_tax,
        'final_total': request.cart.final_total,
    }
    return TemplateResponse(request, "checkout/checkout_pay_online.html", context=context)


def checkout_shipping_address(request):
    '''
    This form asks the user their shipping address.
    :param request:
    :return:
    '''
    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse('checkout_start'))
    if not request.cart.is_account_set():
        return HttpResponseRedirect(reverse('checkout_login'))
    form = ShippingAddressForm(instance=request.cart.shipping_address)

    if request.method == 'POST':
        print(request.POST)
        # create a form instance and populate it with data from the request:
        form = ShippingAddressForm(data=request.POST, instance=request.cart.shipping_address)
        print(form.is_bound)
        # check whether it's valid:
        if form.is_valid():
            print("Form valid")
            # process the data in form.cleaned_data as required
            request.cart.shipping_address = form.save()
            request.cart.tax_error = False
            request.cart.save()
            # redirect to a new URL:
            next_view = request.cart.next_checkout_view(view=Cart.V_SHIPPING_ADDR, user=request.user)

            return HttpResponseRedirect(reverse(next_view))
        else:
            print("Form invalid")
            for field in form:
                print("Field Error:", field.name, field.errors)
            print(form.errors)

    context = {
        'form': form,
    }
    return TemplateResponse(request, "checkout/checkout_delivery.html", context=context)


def checkout_done(request):
    print(request.cart)
    if not request.cart.is_frozen:
        return HttpResponseRedirect(reverse(Cart.V_START))
    if not request.cart.is_account_set():
        return HttpResponseRedirect(reverse(Cart.V_LOGIN))
    if not request.cart.is_shipping_set():
        return HttpResponseRedirect(reverse(Cart.V_DELIVERY_METHOD))
    if not request.cart.is_payment_set():
        return HttpResponseRedirect(reverse(Cart.V_PAYMENT_METHOD))
    if not request.cart.is_billing_addr_required() and request.cart.billing_address:
        return HttpResponseRedirect(reverse(Cart.V_BILLING_ADDRESS))

    request.cart.submit()
    print(request.cart)
    context = {'order_id': request.cart.id}
    return TemplateResponse(request, "checkout/checkout_done.html", context=context)


def create_stripe_payment(request):
    if not request.cart.is_frozen:
        return HttpResponse(403)
    if request.method == 'POST':
        if request.user.is_authenticated:
            customer_id = StripeCustomerId.objects.get_customer_id(user=request.user)
        else:
            customer_id = None
        try:
            amount = request.cart.final_total.amount
            amount_cents = int(amount * 100)
            existing_intents = request.cart.stripepaymentintent_set.filter(cancelled=False, cart=request.cart)
            if existing_intents.count() > 1:
                for intent_db in existing_intents:
                    intent_db.cancel()
            if existing_intents.count() == 1:
                intent_db = existing_intents.first()
                intent = stripe.PaymentIntent.retrieve(intent_db.id)
                if int(intent_db.amount_to_pay.amount * 100) != amount_cents:
                    intent.modify(intent_db.id, metadata={"amount": amount_cents})
            else:
                intent = stripe.PaymentIntent.create(
                    customer=customer_id,
                    setup_future_usage='off_session',
                    amount=amount_cents,
                    currency='usd',
                    description="CGT Cart Number: " + str(request.cart.id),
                )
                intent_db = request.cart.stripepaymentintent_set.create(id=intent.stripe_id,
                                                                        amount_to_pay=amount)
            return JsonResponse({
                'clientSecret': intent['client_secret'],
                'publishableAPIKey': settings.STRIPE_PUBLIC_KEY,
            })
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return HttpResponse(status=403)
    return HttpResponse(status=500)


@login_required
def past_orders(request):
    orders = Cart.submitted.filter(owner=request.user).order_by('date_submitted')
    context = {'past_orders': orders}
    return TemplateResponse(request, "checkout/past_orders.html", context=context)


def past_order_details(request, cart_id):
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        if past_cart.owner and past_cart.owner != request.user and not request.user.is_staff:
            return HttpResponse(status=403)
        context = {'past_cart': past_cart}
        return TemplateResponse(request, "checkout/order_details.html", context=context)
    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(e)
        return HttpResponse(status=400)

    # Handle the event
    print(event.type)
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        payment_intent_object = StripePaymentIntent.objects.get(id=payment_intent.id)
        payment_intent_object.try_mark_captured()
        print('PaymentIntent was successful!')

    elif event.type == 'payment_method.attached':
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        print('PaymentMethod was attached to a Customer!')
    # ... handle other event types
    elif event.type == 'charge.succeeded':
        payment_intent_id = event.data.object.payment_intent  # contains a stripe.PaymentIntent
        charge = event.data.object  # contains a stripe.Charge
        payment_intent_object = StripePaymentIntent.objects.get(id=payment_intent_id)
        payment_intent_object.try_mark_captured()
    else:
        # Unexpected event type
        return HttpResponse(status=400)

    return HttpResponse(status=200)


@login_required
def partner_orders(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug=partner_slug)

    lines = CheckoutLine.objects.filter(item__partner=partner)
    orders = Cart.submitted.filter(lines__in=lines) \
             | Cart.submitted.filter(payment_partner=partner, payment_method=Cart.PAY_IN_STORE) \
             | Cart.submitted.filter(pickup_partner=partner, delivery_method=Cart.PICKUP_ALL)
    orders = orders.distinct()

    form = FiltersForm()

    # https://medium.com/apollo-data-solutions-blog/django-initial-values-for-a-bound-form-fde7b363f79e
    if request.method == 'GET':
        if len(request.GET):  # If there's actually data, use that data.
            form = FiltersForm(request.GET)
        orders = form.get_orders(orders)

    orders = orders.order_by('-date_submitted')
    paginator = Paginator(orders, 10)
    page_number = int(request.GET.get('page_number', 1))
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'filters_form': form,
        'page_number': int(page_number),
        'num_total': orders.count(),
        'partner': partner,
    }
    return TemplateResponse(request, "checkout/partner_orders.html", context=context)


@login_required
def partner_order_details(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    form = TrackingInfoForm(instance=request.cart)
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        print(past_cart)
        context = {'past_cart': past_cart, 'partner': partner, 'form': form}

        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = TrackingInfoForm(request.POST, instance=past_cart)

            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                past_cart = form.save()
                past_cart.mark_shipped()
                print(past_cart)

        return TemplateResponse(request, "checkout/partner_order_details.html", context=context)
    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@login_required
def partner_order_printout(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        print(past_cart)
        context = {'past_cart': past_cart, 'partner': partner, }
        return TemplateResponse(request, "checkout/partner_order_printout.html", context=context)
    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@login_required
def partner_order_mark_paid(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        if past_cart.payment_partner.id is not partner.id:
            return HttpResponse(status=403)
        past_cart.pay()
        return HttpResponseRedirect(
            reverse('partner_order_details', kwargs={'partner_slug': partner_slug, 'cart_id': cart_id}))
    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@login_required
def partner_order_mark_completed(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        if past_cart.pickup_partner.id != partner.id:
            return HttpResponse(status=403)
        if past_cart.status == "Paid":
            past_cart.status = Cart.COMPLETED
            past_cart.save()
        return HttpResponseRedirect(
            reverse('partner_order_details', kwargs={'partner_slug': partner_slug, 'cart_id': cart_id}))
    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@login_required
def partner_order_ready_for_pickup(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug=partner_slug)
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        if past_cart.pickup_partner.id != partner.id:
            return HttpResponse(status=403)
        past_cart.mark_ready_for_pickup()
        return HttpResponseRedirect(
            reverse('partner_order_details', kwargs={'partner_slug': partner_slug, 'cart_id': cart_id}))
    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@login_required
def past_order_mark_cancelled(request, cart_id, partner_slug=None):
    try:
        past_cart = Cart.submitted.get(id=cart_id)
        if partner_slug:
            get_partner_or_401(request, partner_slug=partner_slug)
        elif request.user != past_cart.owner:
            return HttpResponse(status=403)
        past_cart.cancel()
        if partner_slug:
            return HttpResponseRedirect(
                reverse('partner_order_details', kwargs={'partner_slug': partner_slug, 'cart_id': cart_id}))
        else:
            return HttpResponseRedirect(
                reverse('past_order_details', kwargs={'cart_id': cart_id}))

    except Cart.DoesNotExist:
        return HttpResponse(status=404)


@login_required
def saved_cards(request):
    cards = None
    customer = None
    if hasattr(request.user, 'stripe_id'):
        pass
    else:
        StripeCustomerId.objects.create(user=customer, id=stripe.Customer.create())

    cards = stripe.PaymentMethod.list(
        customer=request.user.stripe_id.id,
        type="card",
    )
    intent = stripe.SetupIntent.create(
        customer=request.user.stripe_id.id,
    )
    context = {
        'cards': cards,
        'intent': intent,
        'publishableAPIKey': settings.STRIPE_PUBLIC_KEY,

    }

    return TemplateResponse(request, "account/saved_cards.html", context=context)


@login_required
def remove_card(request, card_id):
    if hasattr(request.user, 'stripe_id'):
        cards = stripe.PaymentMethod.list(
            customer=request.user.stripe_id.id,
            type="card",
        )
        for card in cards.data:
            if card.id == card_id:
                stripe.PaymentMethod.detach(
                    card_id
                )

    return HttpResponseRedirect(reverse('saved_cards'))


def default_address(request):
    address = None
    if hasattr(request.user, 'default_address'):
        address = request.user.default_address
    form = UserDefaultAddressForm(instance=address)
    if request.method == 'POST':
        form = UserDefaultAddressForm(instance=address, data=request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

    context = {
        'form': form,
        'address': address,
    }
    return TemplateResponse(request, "account/billing_address.html", context=context)


def pos(request, partner_slug, cart_id=None):
    partner = get_partner_or_401(request, partner_slug)
    context = {
        'partner': partner,
        'props': get_pos_props(partner, cart_id),
    }
    return TemplateResponse(request, "checkout/pos.html", context=context)


def pos_create_cart(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.create(at_pos=True, payment_partner=partner, payment_method=Cart.PAY_IN_STORE,
                               pickup_partner=partner, delivery_method=Cart.PICKUP_ALL, site=partner.site)

    return JsonResponse({'id': cart.id})


def pos_add_item(request, partner_slug, cart_id, barcode):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.get(id=cart_id)
    if cart.is_paid or cart.is_cancelled:
        return HttpResponseNotFound
    product = Product.objects.get(barcode=barcode)

    items = InventoryItem.objects.filter(product=product)
    if partner:
        items = items.filter(partner=partner)
    items = items.order_by('price')
    in_stock = items.filter(current_inventory__gt=0)
    if in_stock.exists():
        cart.add_item(in_stock.first())
    else:
        cart.add_item(items.last())

    return HttpResponse(status=200)


def pos_set_owner(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug)
    cart = get_object_or_404(Cart, id=cart_id)
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        email = body['email']
        print(email)
        try:
            user = User.objects.get(email=email)
            cart.owner = user
            print("Set Owner")
        except Exception:

            cart.email = email
            print("Set Email instead of owner")

        cart.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def pos_add_custom(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug)
    cart = get_object_or_404(Cart, id=cart_id)
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        product, _ = Product.objects.get_or_create(name="Custom Item or Service")
        price = Money(body['price'], 'USD')
        custom_charge_item = CustomChargeItem.objects.create(partner=partner, product=product,
                                                             price=price, default_price=price,
                                                             description=body['description'])
        custom_charge_item.save()

        # Add item to  cart
        cart.add_item(custom_charge_item)
        HttpResponse(status=200)
    return HttpResponse(status=400)


def pos_pay_cash(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.get(id=cart_id)
    if cart.payment_partner != partner:
        return HttpResponse(403)

    if cart.status != cart.SUBMITTED:
        cart.submit()
    amount = cart.final_total.amount
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        amount = body['amount']

    print(amount)
    if amount is not None:
        cart.pay_amount(amount, cash=True)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


def pos_create_stripe_payment(request, partner_slug, cart_id):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.get(id=cart_id)

    if cart.payment_partner != partner:
        return HttpResponse(status=403)

    if cart.status != cart.SUBMITTED:
        cart.submit()

    customer_id = None
    if cart.owner:
        customer_id = StripeCustomerId.objects.get_customer_id(user=cart.owner)

    amount = cart.final_total.amount
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        amount = body['amount']

    intent = stripe.PaymentIntent.create(
        customer=customer_id,
        payment_method_types=['card_present'],
        capture_method='manual',
        amount=int(amount * 100),
        currency='usd',
        description="CGT Cart Number: " + str(request.cart.id),
    )

    cart.stripepaymentintent_set.create(id=intent.stripe_id, amount_to_pay=amount)
    return JsonResponse({
        'client_secret': intent['client_secret'],
        'publishableAPIKey': settings.STRIPE_PUBLIC_KEY,
    })


def stripe_terminal_connection_token(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    connection_token = stripe.terminal.ConnectionToken.create()
    return JsonResponse({
        'secret': connection_token.secret
    })


def stripe_capture(request, partner_slug, cart_id=None):
    partner = get_partner_or_401(request, partner_slug)
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        intent = stripe.PaymentIntent.capture(
            body['id']
        )
        print("Payment intent received")
        payment_intent_object = StripePaymentIntent.objects.get(id=intent.id)
        payment_intent_object.try_mark_captured()
        return JsonResponse({'intent': intent})
    return HttpResponse(status=400)


def partner_cart_endpoint(request, partner_slug, cart_id=None):
    partner = get_partner_or_401(request, partner_slug)
    return JsonResponse(get_pos_props(partner, cart_id))


def partner_update_quantity(request, cart_id, partner_slug, item_id, quantity):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.get(id=cart_id)
    if cart.is_submitted:
        return HttpResponse(status=400)
    try:
        cart.update_quantity(item_id=item_id, quantity=quantity)
        return HttpResponse(status=200)
    except Exception as e:
        return HttpResponse(status=400)


def partner_update_line(request, cart_id, partner_slug, item_id):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.get(id=cart_id)
    if request.method == "POST":
        print('post')
        try:
            line = cart.lines.get(item_id=item_id)
            body = json.loads(request.body.decode('utf-8'))
            print(body)

            try:
                line.quantity = body['quantity']
                print("Updating quantity")
            except KeyError:
                pass
            try:
                line.price_per_unit_override = Money(Decimal(body['price']), "USD")
                print("Updating price")
            except KeyError:
                pass
            line.save()
            return HttpResponse(status=200)
        except Exception as e:
            print(e)
            return HttpResponse(status=400)
    return HttpResponse(status=400)


def partner_remove_line(request, cart_id, partner_slug, item_id):
    partner = get_partner_or_401(request, partner_slug)
    cart = Cart.objects.get(id=cart_id)
    if cart.is_submitted:
        return HttpResponse(status=400)
    try:
        cart.remove_from_cart(item_id)
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
    return HttpResponse(status=400)


@staff_member_required
def all_orders_tax(request):
    orders = Cart.submitted.all()

    form = FiltersForm()

    # https://medium.com/apollo-data-solutions-blog/django-initial-values-for-a-bound-form-fde7b363f79e
    if request.method == 'GET':
        if len(request.GET):  # If there's actually data, use that data.
            form = FiltersForm(request.GET)
        orders = form.get_orders()

    orders = orders.order_by('-date_submitted').reverse()
    paginator = Paginator(orders, 10)
    page_number = int(request.GET.get('page_number', 1))
    page = paginator.get_page(page_number)

    context = {
        'page': page,
        'filters_form': form,
        'page_number': int(page_number),
        'num_total': orders.count(),
    }
    return TemplateResponse(request, "all_orders_tax.html", context=context)
