from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q, DecimalField
from django.db.models.functions import Coalesce

from orders.models import Order, OrderItem
from menu.models import Menu

# Create your views here.


def home_view(request):
    """
    Public restaurant landing page (Step 4).

    Anyone can view this page (no @login_required) - it replaces the old
    home_redirect(), which just bounced every visitor straight to the login
    page and gave the project no real "front door". Featured items and the
    category list are both pulled from the database/model here so the
    template contains no hardcoded menu data.
    """
    featured_items = Menu.objects.filter(available=True).order_by('-id')[:6]
    categories = Menu.CATEGORY_CHOICES

    return render(
        request,
        'accounts/home.html',
        {
            'featured_items': featured_items,
            'categories': categories,
        }
    )
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        
    else:
        form = RegisterForm()

    return render(request,'accounts/register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(
                request,
                username=username,
                password=password
            )
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.role == 'staff':
                    return redirect('staff_dashboard')
                else:
                    # Customers land on the existing home page (Step 13) -
                    # it is already more attractive than the customer
                    # dashboard and the navbar already covers Menu/Cart/My
                    # Orders, so the dashboard is redundant as a landing
                    # page. The customer_dashboard view/URL/template are
                    # left in place (still directly reachable) - only the
                    # post-login destination changes here.
                    return redirect('home')
    
    else:
        form = LoginForm()

    return render(request,'accounts/login.html',{'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_dashboard(request):
    """
    Professional admin dashboard (Step 3).

    Every number shown here is calculated with the Django ORM below -
    nothing is hardcoded and no business logic lives in the template,
    which only receives already-computed values to display.
    """

    if request.user.role != 'admin':
        return redirect('customer_dashboard')

    # --- Order status counts -------------------------------------------
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    preparing_orders = Order.objects.filter(status='preparing').count()
    ready_orders = Order.objects.filter(status='ready').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    money_field = DecimalField(max_digits=10, decimal_places=2)

    # --- Total revenue ---------------------------------------------------
    # Revenue = sum of (quantity x menu price) across every OrderItem that
    # belongs to a successfully PAID order. Orders are only ever created
    # after payment succeeds (Step 2), so filtering on payment_status='paid'
    # here mainly protects against counting old test orders (created before
    # payment integration existed) as if they were real revenue.
    total_revenue = OrderItem.objects.filter(
        order__payment_status='paid'
    ).aggregate(
        revenue=Coalesce(
            Sum(F('quantity') * F('menu_item__price'), output_field=money_field),
            0,
            output_field=money_field
        )
    )['revenue']

    # --- Recent orders -----------------------------------------------
    # order_total is calculated per-order with an annotation (one ORM
    # query, no Python loop) instead of being computed in the template.
    recent_orders = (
        Order.objects
        .select_related('customer')
        .annotate(
            order_total=Coalesce(
                Sum(
                    F('orderitem__quantity') * F('orderitem__menu_item__price'),
                    output_field=money_field
                ),
                0,
                output_field=money_field
            )
        )
        .order_by('-id')[:5]
    )

    # --- Popular menu items --------------------------------------------
    # Top 5 menu items by total quantity sold across paid orders.
    popular_items = (
        Menu.objects
        .annotate(
            total_quantity=Coalesce(
                Sum(
                    'orderitem__quantity',
                    filter=Q(orderitem__order__payment_status='paid')
                ),
                0
            )
        )
        .filter(total_quantity__gt=0)
        .order_by('-total_quantity')[:5]
    )

    return render(
        request,
        'accounts/admin_dashboard.html',
        {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'preparing_orders': preparing_orders,
            'ready_orders': ready_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders,
            'popular_items': popular_items,
        }
    )


@login_required
def staff_dashboard(request):
    """
    Professional staff dashboard (Step 5).

    Staff need a working view of the kitchen/delivery queue, not the
    business stats (revenue, popular items) that belong on the admin
    dashboard - so this view only ever computes order-status information,
    and admin_dashboard above remains the only place revenue is shown.
    All counts/queries are done here with the ORM; the template just
    displays the numbers and rows it is given.
    """

    # Staff must never see the admin dashboard - only admins may.
    if request.user.role != 'staff':
        return redirect('customer_dashboard')

    # --- Order status counts -------------------------------------------
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    preparing_orders = Order.objects.filter(status='preparing').count()
    ready_orders = Order.objects.filter(status='ready').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    money_field = DecimalField(max_digits=10, decimal_places=2)

    # --- Orders to process ----------------------------------------------
    # Every order still somewhere in the kitchen/delivery workflow (i.e.
    # not yet delivered or cancelled), newest first. Capped at the 10 most
    # recent so the dashboard stays a quick-glance queue rather than a full
    # order history - the existing "Manage Orders" page already lists
    # every order for when staff need the complete list.
    orders_to_process = (
        Order.objects
        .filter(status__in=['pending', 'confirmed', 'preparing', 'ready'])
        .select_related('customer')
        .annotate(
            order_total=Coalesce(
                Sum(
                    F('orderitem__quantity') * F('orderitem__menu_item__price'),
                    output_field=money_field
                ),
                0,
                output_field=money_field
            )
        )
        .order_by('-id')[:10]
    )

    return render(
        request,
        'accounts/staff_dashboard.html',
        {
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'preparing_orders': preparing_orders,
            'ready_orders': ready_orders,
            'delivered_orders': delivered_orders,
            'orders_to_process': orders_to_process,
        }
    )


@login_required
def customer_dashboard(request):

    return render(
        request,
        'accounts/customer_dashboard.html'
    )
