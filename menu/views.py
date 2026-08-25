from django.shortcuts import render
from .models import Menu
from .forms import MenuForm
from django.shortcuts import redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# Create your views here.

def menu_list(request):

    search = request.GET.get('search')
    category = request.GET.get('category')

    menus = Menu.objects.all()

    if search:
        menus = menus.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    if category:
        menus = menus.filter(category=category)

    return render(
        request,
        'menu/menu_list.html',
        {
            'menus': menus
        }
    )

@login_required
def add_menu(request):

    if request.user.role != 'admin':
        return HttpResponse("Access Denied")

    if request.method == 'POST':

        form = MenuForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            return redirect('menu_list')

    else:
        form = MenuForm()

    return render(
        request,
        'menu/add_menu.html',
        {
            'form': form
        }
    )

@login_required
def edit_menu(request, id):

    if request.user.role != 'admin':
        return HttpResponse("Access Denied")

    menu = get_object_or_404(
        Menu,
        id=id
    )

    if request.method == 'POST':

        form = MenuForm(
            request.POST,
            request.FILES,
            instance=menu
        )

        if form.is_valid():
            form.save()
            return redirect('menu_list')

    else:

        form = MenuForm(
            instance=menu
        )

    return render(
        request,
        'menu/edit_menu.html',
        {
            'form': form
        }
    )


@login_required
def delete_menu(request, id):

    if request.user.role != 'admin':

        return HttpResponse(
            "Access Denied"
        )

    menu = get_object_or_404(
        Menu,
        id=id
    )

    if request.method == 'POST':
        menu.delete()
        return redirect('menu_list')

    return render(request,'menu/delete_menu.html',{'menu': menu})
