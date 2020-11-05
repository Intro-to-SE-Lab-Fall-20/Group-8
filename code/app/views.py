from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .forms import UserRegistrationForm, ComposeForm
from .models import Recipient, Sender, Email, CustomUser


@login_required
@require_http_methods(['GET'])
def view_email(request, email_uid):
    """
    Handles serving individual email pages.
    """

    # TODO: make it so that not just any user can view any email as long as they know the UID

    # fetch the requested email from the DB
    email = Email.objects.get(uid=email_uid)

    # get respective sender
    sender = email.sender_email.get()

    # get respective recipients
    recipients = ', '.join([recipient.user.email for recipient in email.recipient_set.all()])

    return render(request, 'view_email.html', {
        'user': request.user,
        'email': email,
        'sender': sender,
        'to': recipients,
        'attachments': [attach for attach in email.attachment_set.all()]
    })


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
        'user': request.user,
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
        'user': request.user,
        'folder': 'inbox',
        'emails': emails
    })


@login_required
@require_http_methods(['GET'])
def search(request):
    """
    Handles searching for emails.
    """

    # get query from GET data
    query = request.GET['query']

    # check if the user has given a valid query
    if not query:
        messages.error(request, "Invalid search query!")
        return redirect('/')

    # setup
    emails = {}
    sender_results = Sender.objects.none()
    recipient_results = Recipient.objects.none()

    # query DB for matching sent emails
    senders = Sender.objects.filter(user=request.user)
    if query in request.user.email:
        # if the user's query is for their own email, add sent emails
        sender_results = sender_results | senders
    sender_results = sender_results | senders.filter(email__body__contains=query)
    sender_results = sender_results | senders.filter(email__subject__contains=query)

    # find any sent emails whose recipients match the query
    for sender in senders:
        recipient_results = recipient_results | sender.email.recipient_set.filter(user__email__contains=query)

    # query DB for matching recipients
    recipients = Recipient.objects.filter(user=request.user)
    if query in request.user.email:
        # if the user's query is for their own email, add sent emails
        recipient_results = recipient_results | recipients
    recipient_results = recipient_results | Recipient.objects.filter(user=request.user, email__body__contains=query)
    recipient_results = recipient_results | Recipient.objects.filter(user=request.user, email__subject__contains=query)

    # find any sent emails whose recipients match the query
    for recipient in recipients:
        sender_results = sender_results | recipient.email.sender_email.all().filter(user__email__contains=query)

    # add together matching sender results
    for sender in sender_results:
        emails[sender.email.uid] = {
            'subject': sender.email.subject,
            'body': sender.email.body,
            'from': sender.user.email,
            'to': ', '.join([recipient.user.email for recipient in sender.email.recipient_set.all()]),
        }

    # add together matching recipient results
    for recipient in recipient_results:
        if emails.get(recipient.email.uid):
            # this email has already been added, skip it
            continue
        emails[recipient.email.uid] = {
            'uid': recipient.email.uid,
            'subject': recipient.email.subject,
            'body': recipient.email.body,
            'from': recipient.email.sender_email.get().user.email,
            'to': recipient.user.email
        }

    # render and return any results
    return render(request, 'search.html', {
        'user': request.user,
        'emails': emails
    })


@login_required
@require_http_methods(['GET', 'POST'])
def compose(request):
    """
    Serves the compose page. Creates emails when users finish composing.
    """

    # TODO: make it so that not just any user can create an email as any user they want

    if request.method == 'POST':
        form = ComposeForm(request.POST, request.FILES)
        if form.is_valid():
            # create email instance and respective relations
            form.create_email_and_relations(request.FILES)

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
        form = ComposeForm(initial={
            'sender': request.user.email
        })

    return render(request, 'compose.html', {
        'user': request.user,
        'form': form
    })


@login_required
@require_http_methods(['GET', 'POST'])
def forward(request, email_uid=None):
    """
    Serves the forward page. Creates emails when users finish composing.
    """

    # TODO: make it so that not just any user can create an email as any user they want
    # TODO: make it so that not just any user can forward any email they want, regardless of permission

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
        email = Email.objects.get(uid=email_uid) if email_uid is not None else None
        if email is not None:
            form = ComposeForm(initial={
                'sender': request.user.email,
                'body': email.body,
                'is_forward': True,
            })
        else:
            messages.error(request, f"Email for UID {email_uid} not found!")
            return redirect('/')

    return render(request, 'forward.html', {
        'user': request.user,
        'form': form,
    })


@login_required
@require_http_methods(['GET'])
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
            if user.failed_attempts >= 3:
                messages.warning(request, "User account is locked")

            else:
                # if the user's info is legit, log them in
                auth_login(request, user)

                # set session expiry if remember-me check box was not checked
                if not remember:
                    request.session.set_expiry(0)

                # redirect to inbox
                messages.success(request, f"Welcome back {request.user.username}!")
                return redirect('inbox')

        else:
            try:
                # gets username if user exists increments failed_attempts column and saves user
                user = CustomUser.objects.get(username=username)
                user.failed_attempts += 1
                user.save()

            except CustomUser.DoesNotExist:
                # continues if no user with that username exists
                pass

            # user's info is bad, notify them
            messages.warning(request, "Invalid username or password.")

    else:
        # check if the user is already logged in
        if request.user.is_authenticated:
            return redirect('inbox')

    # serve page to user normally
    return render(request, 'login.html', {})
