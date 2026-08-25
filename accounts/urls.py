from django.urls import path
from .views import register_view, login_view, logout_view, admin_dashboard, staff_dashboard, customer_dashboard, home_view


urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout_view/',logout_view, name='logout'),
    path('admin-dashboard/',admin_dashboard,name='admin_dashboard'),
    path('staff-dashboard/',staff_dashboard,name='staff_dashboard'),
    path('customer-dashboard/',customer_dashboard,name='customer_dashboard'),
]