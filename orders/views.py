import json

import razorpay
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from menu.models import Menu
from .models import Order, OrderItem
from .forms import CheckoutForm


def _get_valid_cart_items(request):
    """
    Reads the session cart and builds the list of items to display/checkout.

    Any menu item that no longer exists in the database (deleted after it
    was added to the cart) is dropped from the session cart here, so both
    the cart page and the checkout page always work from a "clean" cart.
    Returns (cart_items, total).
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    stale_found = False

    for menu_id in list(cart.keys()):

        quantity = cart[menu_id]

        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            del cart[menu_id]
            stale_found = True
            continue

        subtotal = menu.price * quantity
        total += subtotal
        cart_items.append(
            {
                'menu': menu,
                'quantity': quantity,
                'subtotal': subtotal
            }
        )

    if stale_found:
        request.session['cart'] = cart
        request.session.modified = True
        messages.warning(
            request,
            "Some items in your cart are no longer available and were removed."
        )

    return cart_items, total


def _get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def add_to_cart(request, menu_id):

    menu = get_object_or_404(Menu, id=menu_id)

    if not menu.available:
        messages.error(
            request,
            f"{menu.name} is currently unavailable and cannot be added to the cart."
        )
        return redirect('menu_list')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        cart[str(menu_id)] += quantity
    else:
        cart[str(menu_id)] = quantity

    request.session['cart'] = cart

    return redirect('menu_list')


@login_required
@require_POST
def increase_quantity(request, menu_id):

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        cart[str(menu_id)] += 1

    request.session['cart'] = cart

    return redirect('view_cart')


@login_required
@require_POST
def decrease_quantity(request, menu_id):

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:

        cart[str(menu_id)] -= 1

        if cart[str(menu_id)] <= 0:
            del cart[str(menu_id)]

    request.session['cart'] = cart

    return redirect('view_cart')


@login_required
@require_POST
def remove_from_cart(request, menu_id):

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        del cart[str(menu_id)]

    request.session['cart'] = cart

    return redirect('view_cart')


@login_required
def view_cart(request):

    cart_items, total = _get_valid_cart_items(request)

    return render(
        request,
        'orders/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


@login_required
def checkout(request):
    """
    STEP 1 - Professional Checkout.

    This view ONLY collects and validates delivery/contact details.
    It does NOT create an Order or OrderItem rows, and it does NOT
    touch the session cart (the cart stays exactly as it is).

    On a valid submission, the cleaned form data is stashed in the
    session under 'checkout_info' and the user is sent on to the
    payment page. The actual Order is only created once payment
    succeeds - see payment_verify() below.
    """

    cart_items, total = _get_valid_cart_items(request)

    if not cart_items:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('view_cart')

    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():

            # Only plain, JSON-serialisable data goes into the session.
            request.session['checkout_info'] = form.cleaned_data
            request.session.modified = True

            return redirect('payment')

    else:

        form = CheckoutForm(
            initial={
                'full_name': request.user.get_full_name() or request.user.username
            }
        )

    return render(
        request,
        'orders/checkout.html',
        {
            'form': form,
            'cart_items': cart_items,
            'total': total,
        }
    )


@login_required
def payment(request):
    """
    STEP 2 - Payment Integration.

    Shows the order summary and a "Pay Now" button backed by Razorpay
    Checkout, running in TEST MODE (no real money moves). This view only
    creates a Razorpay-side order (so Checkout knows what to charge) - it
    does NOT create our own Order/OrderItem rows. Those are only created
    in payment_verify(), after Razorpay confirms the payment.
    """

    checkout_info = request.session.get('checkout_info')
    cart_items, total = _get_valid_cart_items(request)

    if not checkout_info or not cart_items:
        messages.warning(request, "Please complete the checkout form before proceeding to payment.")
        return redirect('checkout')

    razorpay_order = None
    gateway_error = None

    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        gateway_error = (
            "Payment gateway is not configured. Set the RAZORPAY_KEY_ID and "
            "RAZORPAY_KEY_SECRET environment variables (Razorpay TEST mode "
            "keys) and restart the server to enable payment."
        )
    else:
        try:
            client = _get_razorpay_client()
            # Razorpay expects the amount in the smallest currency unit -
            # paise for INR - and as an integer.
            amount_in_paise = int(total * 100)
            razorpay_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1,
            })
            # Remembered so payment_verify() can confirm the payment being
            # verified actually belongs to this checkout session.
            request.session['razorpay_order_id'] = razorpay_order['id']
            request.session.modified = True
        except Exception:
            gateway_error = "Could not reach the payment gateway right now. Please try again in a moment."

    return render(
        request,
        'orders/payment.html',
        {
            'checkout_info': checkout_info,
            'cart_items': cart_items,
            'total': total,
            'razorpay_order': razorpay_order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'gateway_error': gateway_error,
        }
    )


@login_required
@require_POST
def payment_verify(request):
    """
    STEP 2 - called by JavaScript (fetch) from the payment page once
    Razorpay Checkout reports a successful payment in the browser.

    This is the ONLY place in the whole project where a "paid" Order is
    created. Before creating anything, it:

      1. Checks whether an Order already exists for this Razorpay order id
         (handles the browser re-sending the same success response - no
         duplicate order is created).
      2. Confirms the order id being verified matches the one we created
         for this checkout session.
      3. Cryptographically verifies the payment signature with Razorpay's
         SDK, using our secret key - this is what actually proves the
         payment is genuine, not just a client-side claim of "success".

    Only if all three pass does it create the Order + OrderItems, and only
    then does it clear the cart and checkout session data.
    """

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'redirect_url': reverse('payment_failed') + '?reason=bad_request'})

    razorpay_order_id = data.get('razorpay_order_id', '')
    razorpay_payment_id = data.get('razorpay_payment_id', '')
    razorpay_signature = data.get('razorpay_signature', '')

    if not razorpay_order_id:
        return JsonResponse({'ok': False, 'redirect_url': reverse('payment_failed') + '?reason=bad_request'})

    # 1. Idempotency check - if we already created an Order for this
    #    Razorpay order id, just send the user back to it. This is checked
    #    BEFORE anything else so a repeated/duplicate success request always
    #    lands on the existing confirmation page instead of failing.
    existing_order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
    if existing_order:
        return JsonResponse({'ok': True, 'redirect_url': reverse('order_confirmation', args=[existing_order.id])})

    # 2. This Razorpay order id must be the one we created for this
    #    checkout session - not one copied from somewhere else.
    expected_order_id = request.session.get('razorpay_order_id')
    if razorpay_order_id != expected_order_id:
        return JsonResponse({'ok': False, 'redirect_url': reverse('payment_failed') + '?reason=order_mismatch'})

    # 3. Verify the payment is genuine using Razorpay's signature check.
    client = _get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'ok': False, 'redirect_url': reverse('payment_failed') + '?reason=invalid_signature'})

    checkout_info = request.session.get('checkout_info')
    cart_items, total = _get_valid_cart_items(request)

    if not checkout_info or not cart_items:
        return JsonResponse({'ok': False, 'redirect_url': reverse('payment_failed') + '?reason=cart_changed'})

    try:
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                status='pending',
                full_name=checkout_info['full_name'],
                phone=checkout_info['phone'],
                delivery_address=checkout_info['delivery_address'],
                notes=checkout_info.get('notes') or '',
                payment_status='paid',
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=item['menu'],
                    quantity=item['quantity'],
                )
    except IntegrityError:
        # Extremely unlikely race: two requests for the same payment both
        # passed the idempotency check above at almost the same instant.
        # The unique constraint on razorpay_order_id is the backstop here.
        existing_order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if existing_order:
            request.session['cart'] = {}
            request.session.pop('checkout_info', None)
            request.session.pop('razorpay_order_id', None)
            request.session.modified = True
            return JsonResponse({'ok': True, 'redirect_url': reverse('order_confirmation', args=[existing_order.id])})
        return JsonResponse({'ok': False, 'redirect_url': reverse('payment_failed') + '?reason=order_conflict'})

    # Only now that the Order + OrderItems safely exist do we clear the
    # cart and the checkout session data.
    request.session['cart'] = {}
    request.session.pop('checkout_info', None)
    request.session.pop('razorpay_order_id', None)
    request.session.modified = True

    return JsonResponse({'ok': True, 'redirect_url': reverse('order_confirmation', args=[order.id])})


@login_required
def payment_failed(request):
    """
    STEP 2 - shown when payment fails, is cancelled, or can't be verified.
    The cart and checkout details are never touched on this path, so the
    customer can simply retry without re-entering anything.
    """

    reason_messages = {
        'cancelled': "You closed the payment window before completing payment.",
        'failed': "The payment gateway reported that this payment failed.",
        'invalid_signature': "We couldn't verify this payment. No charge was recorded on our side.",
        'order_mismatch': "This payment session has expired. Please try again.",
        'cart_changed': "Your cart changed before payment finished. Please review your cart and try again.",
        'order_conflict': "There was a conflict processing this payment. Please check My Orders before retrying.",
        'bad_request': "Something went wrong while processing the payment response.",
    }

    reason = request.GET.get('reason', '')
    message = reason_messages.get(reason, "Payment was not completed.")

    return render(request, 'orders/payment_failed.html', {'message': message})


@login_required
def order_confirmation(request, order_id):
    """
    STEP 2 - the professional confirmation page shown right after a
    successful payment. Also reachable later from My Orders if the
    customer wants to look at a paid order again.
    """

    order = get_object_or_404(Order, id=order_id, customer=request.user)

    items = []
    total = 0

    for order_item in order.orderitem_set.all():
        subtotal = order_item.menu_item.price * order_item.quantity
        total += subtotal
        items.append(
            {
                'name': order_item.menu_item.name,
                'quantity': order_item.quantity,
                'price': order_item.menu_item.price,
                'subtotal': subtotal,
            }
        )

    return render(
        request,
        'orders/order_confirmation.html',
        {
            'order': order,
            'items': items,
            'total': total,
        }
    )


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).order_by('-id')

    return render(
        request,
        'orders/my_orders.html',
        {
            'orders': orders
        }
    )


@login_required
def order_details(request, order_id):

    # Admins and staff can look at any order (needed for the "View" button
    # on the admin dashboard's Recent Orders list and the staff dashboard's
    # Orders to Process list); everyone else can only ever see their own
    # order - this matches the access rule already used by
    # my_orders()/cancel_order() above.
    if request.user.role in ('admin', 'staff'):
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, customer=request.user)

    items = order.orderitem_set.all()

    total = 0

    for item in items:
        total += item.menu_item.price * item.quantity

    return render(
        request,
        'orders/order_details.html',
        {
            'order': order,
            'items': items,
            'total': total
        }
    )


@login_required
@require_POST
def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()

    return redirect('my_orders')


@login_required
def manage_orders(request):

    # Both admins and staff manage day-to-day orders (this is what the
    # staff dashboard's "Manage Orders" quick-action button links to, added
    # in Step 5); only customers are redirected away.
    if request.user.role not in ('admin', 'staff'):
        return redirect('customer_dashboard')

    orders = Order.objects.all().order_by('-id')

    return render(
        request,
        'orders/manage_orders.html',
        {
            'orders': orders,
            'status_choices': Order.STATUS_CHOICES,
        }
    )


@login_required
@require_POST
def update_order_status(request, order_id):

    # Kept in sync with manage_orders() above - staff can update order
    # status from the same page admins use.
    if request.user.role not in ('admin', 'staff'):
        return redirect('customer_dashboard')

    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    valid_statuses = dict(Order.STATUS_CHOICES)
    if new_status in valid_statuses:
        order.status = new_status
        order.save()

    return redirect('manage_orders')
