from django.urls import path
from .views import menu_list,add_menu,edit_menu,delete_menu


urlpatterns = [
    path('', menu_list, name='menu_list'),
    path('add/', add_menu, name='add_menu'),
    path('edit/<int:id>/',edit_menu,name='edit_menu'),
    path('delete/<int:id>/',delete_menu,name='delete_menu'),
]