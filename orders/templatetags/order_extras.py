from django import template

register = template.Library()


@register.filter
def order_total(order):
    """
    Display-only helper: returns the grand total for a single Order by
    summing (quantity x menu price) across its OrderItems.

    This does not change any business logic - it mirrors the exact same
    calculation orders/views.py's order_details() view already performs.
    It exists so templates (my_orders.html, manage_orders.html) can show
    an order's total without needing an .annotate() added to the
    my_orders()/manage_orders() views, keeping orders/views.py untouched
    during this UI-only pass.
    """
    total = 0
    for item in order.orderitem_set.all():
        total += item.quantity * item.menu_item.price
    return total


@register.filter
def line_subtotal(order_item):
    """
    Display-only helper: returns quantity x unit price for a single
    OrderItem, so a per-line subtotal can be shown without any template
    arithmetic filters or view changes.
    """
    return order_item.quantity * order_item.menu_item.price
