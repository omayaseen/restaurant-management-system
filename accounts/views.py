from django.shortcuts import render,redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.


def home_redirect(request):
    return redirect('login')
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
                    return redirect('admin_dashboard')
                else:
                    return redirect('customer_dashboard')
    
    else:
        form = LoginForm()

    return render(request,'accounts/login.html',{'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_dashboard(request):

    return render(
        request,
        'accounts/admin_dashboard.html'
    )


@login_required
def staff_dashboard(request):

    return render(
        request,
        'accounts/staff_dashboard.html'
    )


@login_required
def customer_dashboard(request):

    return render(
        request,
        'accounts/customer_dashboard.html'
    )




