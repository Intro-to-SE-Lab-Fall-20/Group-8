from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
def inbox(request):
    """
    Home page of Simple Email. Serves the user's inbox.
    """

    return render(request, 'inbox.html', {})


@login_required
def logout(request):
    """
    Logout view for Simple Email.
    Logs a user out and notifies redirects them to login page.
    """

    auth_logout(request)
    messages.success(request, "Successfully logged out!")

    return redirect('/login')


@require_http_methods(["GET", "POST"])
def login(request):
    """
    Login page for Simple Email.
    If this is a GET request, user is loading the login page.
    If this is a POST request, user is trying to login.
    """

    if request.method == "POST":
        # validate user info
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember', False)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # if the user's info is legit, log them in
            auth_login(request, user)

            # set session expiry if remember-me check box was not checked
            if not remember:
                request.session.set_expiry(0)

            # redirect to inbox
            return redirect('inbox')

        else:
            # user's info is bad, notify them
            messages.warning(request, "Invalid username or password.")
            return redirect('/login')

    else:
        # check if the user is already logged in
        if request.user.is_authenticated:
            return redirect('inbox')

    # serve page to user normally
    return render(request, 'login.html', {})
