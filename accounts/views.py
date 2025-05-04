from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

from .forms import CustomUserCreationForm


def register(request):
    """
    Handle user registration. On POST, validate the form, create the user,
    log them in, send success message and email notification, and redirect to homepage.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # ✅ Show success message to the user
            messages.success(request, "Account created successfully! 🎉")

            # ✉️ Send email notification to your Gmail
            send_mail(
                subject="🔔 New User Registered",
                message=(
                    f"A new user has just registered:\n\n"
                    f"Username: {user.username}\n"
                    f"Email: {user.email or 'No email provided'}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
                fail_silently=True
            )

            return redirect('home')
        else:
            # 🐞 Debugging output
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Custom login view that authenticates users and redirects based on their type.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect('/admin/')  
            else:
                return redirect('home') 
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})
