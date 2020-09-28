from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .forms import UserRegistrationForm, ComposeForm
from .models import Recipient, Sender


@login_required
@require_http_methods(['GET', 'POST'])
def outbox(request):
    """
    Serves the user's outbox, or sent messages.
    """

    # get all of the emails that the user has sent
    emails = []
    senders = Sender.objects.filter(user=request.user)
    for sender in senders:
        if sender.is_draft:
            continue    # skip this email since it hasn't been sent yet (still a draft)

        email = sender.email
        emails.append({
            'uid': email.uid,
            'subject': email.subject,
            'from': email.sender_email.all()[0].user.email,
            'to': ', '.join([recipient.user.email for recipient in email.recipient_set.all()]),
            'body': email.body
        })

    return render(request, 'inbox.html', {
        'folder': 'outbox',
        'emails': emails
    })


@login_required
@require_http_methods(['GET', 'POST'])
def inbox(request):
    """
    Home page of Simple Email. Serves the user's inbox.
    """

    # get all emails received by the user that have been sent
    emails = []
    recipients = Recipient.objects.filter(user=request.user)
    for recipient in recipients:
        if not recipient.is_sent:
            continue    # skip this email since it hasn't been sent yet (still a draft)

        email = recipient.email
        emails.append({
            'uid': email.uid,
            'subject': email.subject,
            'from': email.sender_email.all()[0].user.email,
            'to': ', '.join([recipient.user.email for recipient in email.recipient_set.all()]),
            'body': email.body
        })

    return render(request, 'inbox.html', {
        'folder': 'inbox',
        'emails': emails
    })


@login_required
@require_http_methods(['GET', 'POST'])
def compose(request):
    """
    Serves the compose page. Creates emails when users finish composing.
    """

    if request.method == 'POST':
        form = ComposeForm(request.POST)
        if form.is_valid():
            # create email instance and respective relations
            form.create_email_and_relations()

            # notify user and redirect to inbox
            messages.success(request, "Message sent!")
            return redirect('/')

        else:
            # compose is bad, notify user
            for error, data in form.errors.items():
                if error == 'subject':
                    messages.error(request, 'Invalid subject: subject cannot be empty!')
                    continue

                elif error == '__all__':
                    if 'recipient' in data[0]:
                        messages.error(request, 'Invalid recipients: one of your recipients was not found!')
                        continue

                messages.error(request, data[0])

    else:
        form = ComposeForm()

    return render(request, 'compose.html', {'form': form})


@login_required
def logout(request):
    """
    Logout view for Simple Email.
    Logs a user out and notifies redirects them to login page.
    """

    messages.success(request, f"See ya later {request.user.username}!")
    auth_logout(request)

    return redirect('/login')


@require_http_methods(["GET", "POST"])
def register(request):
    """
    Register page for new users of Simple Email.
    """

    if request.method == "POST":
        # validate user input
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # save form to create user
            user = form.save()

            # log the user in
            auth_login(request, user)

            # redirect to homepage (inbox)
            messages.success(request, f"Welcome {request.user.username}!")
            return redirect('inbox')

        else:
            # user info is bad, notify them
            for error, data in form.errors.items():
                messages.error(request, data[0])

    else:
        # check if the user is already logged in
        if request.user.is_authenticated:
            return redirect('inbox')

        # create new form for user to register with
        form = UserRegistrationForm()

    return render(request, 'register.html', {"form": form})


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
            messages.success(request, f"Welcome back {request.user.username}!")
            return redirect('inbox')

        else:
            # user's info is bad, notify them
            messages.warning(request, "Invalid username or password.")

    else:
        # check if the user is already logged in
        if request.user.is_authenticated:
            return redirect('inbox')

    # serve page to user normally
    return render(request, 'login.html', {})
