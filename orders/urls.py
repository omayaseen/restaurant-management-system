from django.urls import path
from .views import (
    add_to_cart, view_cart, checkout, payment, payment_verify, payment_failed,
    order_confirmation, my_orders, order_details, cancel_order, manage_orders,
    update_order_status, increase_quantity, decrease_quantity, remove_from_cart
)

urlpatterns = [
     path(
        'add/<int:menu_id>/',add_to_cart,name='add_to_cart'),
        path('cart/',view_cart,name='view_cart'),
        path('checkout/',checkout,name='checkout'),
        path('checkout/payment/',payment,name='payment'),
        path('checkout/payment/verify/',payment_verify,name='payment_verify'),
        path('checkout/payment/failed/',payment_failed,name='payment_failed'),
        path('order-confirmation/<int:order_id>/',order_confirmation,name='order_confirmation'),
        path('my-orders/', my_orders, name='my_orders'),
        path('order/<int:order_id>/', order_details, name='order_details'),
        path('cancel/<int:order_id>/',cancel_order,name='cancel_order'),
        path('manage/', manage_orders,name='manage_orders'),
        path('update-status/<int:order_id>/',update_order_status,name='update_order_status'),
        path('increase/<int:menu_id>/',increase_quantity,name='increase_quantity'),
        path('decrease/<int:menu_id>/',decrease_quantity,name='decrease_quantity'),
        path('remove/<int:menu_id>/',remove_from_cart,name='remove_from_cart'),

]
