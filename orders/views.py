from django.shortcuts import redirect
from menu.models import Menu
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import Order,OrderItem
from django.contrib.auth.decorators import login_required


# Create your views here.

def add_to_cart(request, menu_id):

    quantity = int(
        request.POST.get('quantity', 1)
    )

    cart = request.session.get(
        'cart',
        {}
    )

    if str(menu_id) in cart:

        cart[str(menu_id)] += quantity

    else:

        cart[str(menu_id)] = quantity

    request.session['cart'] = cart

    return redirect('menu_list')




def increase_quantity(request, menu_id):

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        cart[str(menu_id)] += 1

    request.session['cart'] = cart

    return redirect('view_cart')


def decrease_quantity(request, menu_id):

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:

        cart[str(menu_id)] -= 1

        if cart[str(menu_id)] <= 0:
            del cart[str(menu_id)]

    request.session['cart'] = cart

    return redirect('view_cart')


def remove_from_cart(request, menu_id):

    cart = request.session.get('cart', {})

    if str(menu_id) in cart:
        del cart[str(menu_id)]

    request.session['cart'] = cart

    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get(
        'cart',
        {}
    )
    cart_items = []
    total = 0
    for menu_id,quantity in cart.items():
        menu = Menu.objects.get(
            id=menu_id
        )
        subtotal = menu.price * quantity
        total += subtotal
        cart_items.append(
            {
                'menu': menu,
                'quantity': quantity,
                'subtotal': subtotal
            }
        )
    return render(request,'orders/cart.html',{'cart_items': cart_items,'total': total}
    )

def checkout(request):

    order = Order.objects.create(
        customer=request.user,
        status='pending'
    )
    cart = request.session.get('cart', {})
    for menu_id, quantity in cart.items():
        menu = Menu.objects.get(id=int(menu_id))
        OrderItem.objects.create(
            order=order,
            menu_item=menu,
            quantity=quantity
        )
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('view_cart')

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

    order = Order.objects.get(
        id=order_id,
        customer=request.user
    )

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
def cancel_order(request, order_id):

    order = Order.objects.get(
        id=order_id,
        customer=request.user
    )

    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()

    return redirect('my_orders')

@login_required
def manage_orders(request):

    if request.user.role != 'admin':
        return redirect('customer_dashboard')

    orders = Order.objects.all().order_by('-id')

    return render(
        request,
        'orders/manage_orders.html',
        {
            'orders': orders
        }
    )

@login_required
def update_order_status(request, order_id):

    if request.user.role != 'admin':
        return redirect('customer_dashboard')

    order = Order.objects.get(id=order_id)

    if request.method == 'POST':

        new_status = request.POST.get('status')

        order.status = new_status

        order.save()

    return redirect('manage_orders')
