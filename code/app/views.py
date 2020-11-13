from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import get_hasher
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


from .forms import UserRegistrationForm, ComposeForm, UserResetForm, NoteForm
from .models import Recipient, Sender, Email, CustomUser, Note


def verify_email_auth(func, *args, **kwargs):
    """
    Decorator function to check if a user is logged in to the
    Email client before granting access to a page.
    """

    def checker(*args, **kwargs):
        request = args[0]   # should be first pos arg
        if request is not None:
            email_session = request.session.get('email_session', None)
            if email_session:
                # user is logged in, continue to view
                return func(*args, **kwargs)
            else:
                # user is not logged in, warn them
                messages.warning(request, "Please sign-in to continue.")

        return redirect('/email_login')

    return checker

@login_required
@verify_email_auth
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
@verify_email_auth
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
@verify_email_auth
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
@verify_email_auth
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
@verify_email_auth
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
@verify_email_auth
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
@verify_email_auth
@require_http_methods(['GET'])
def email_logout(request):
    """
    Logs a user out of the Simple Email app.
    """

    request.session['email_session'] = False

    return redirect("/")


@login_required
@require_http_methods(['GET'])
def logout(request):
    """
    Logout view for Simple Email.
    Logs a user out and notifies redirects them to login page.
    """

    messages.success(request, f"See ya later {request.user.username}!")
    auth_logout(request)

    # clear any existing session data
    request.session.flush()

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
            return redirect('/')

        else:
            # user info is bad, notify them
            for error, data in form.errors.items():
                messages.error(request, data[0])

    else:
        # check if the user is already logged in
        if request.user.is_authenticated:
            return redirect('/')

        # create new form for user to register with
        form = UserRegistrationForm()

    return render(request, 'register.html', {"form": form})


@require_http_methods(["GET", "POST"])
def reset_password(request):
    """
    Resets the password for the email of the user that is logged into the master user
    """

    if request.method == "POST":
        # validate user input
        form = UserResetForm(request.POST)
        if form.is_valid():
            # save form to create user
            form.update_password()

            # redirect to homepage (inbox)
            messages.success(request, f" {request.user.username}'s Password was reset!")
            return redirect('/inbox')

        else:
            # user info is bad, notify them
            for error, data in form.errors.items():
                messages.error(request, data[0])

    else:
        # check if the user is already logged in
        if request.user.is_authenticated:
            # return redirect('/')
            pass

        # create new form for user to register with
        form = UserResetForm()

    return render(request, 'reset_password.html', {"form": form, "user": request.user})


@require_http_methods(["GET"])
@login_required
def splash(request):
    """
    Splash page for choosing which app to use.
    """

    return render(request, 'splash.html', {})


@login_required
@require_http_methods(["GET", "POST"])
def email_login(request):
    """
    Handles logging in users to access Simple Email app.
    """

    if request.method == 'POST':
        # debug - auth user upon form submission
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = CustomUser.objects.get(email=email)
            hasher = get_hasher('default')
            is_correct = hasher.verify(password, user.email_password)

            if is_correct:
                request.session["email_session"] = True
                return redirect('/inbox')
            else:
                messages.warning(request, "Invalid email or password.")

        except CustomUser.DoesNotExist:
            messages.warning(request, "Invalid email or password.")

    else:
        if request.session.get("email_session", None):
            # redirect user to inbox if user is already signed into Email
            return redirect('/inbox')

    return render(request, 'email_login.html', {})


@require_http_methods(["GET", "POST"])
def master_login(request):
    """
    Login page for entire site. This servers as a "master" login page to grant access
    to email and notes apps.
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
                return redirect('splash')

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
            return redirect('splash')

    # serve page to user normally
    return render(request, 'login.html', {})


@login_required
def note_compose(request):
    """
    Serves the Notes page. Creates emails when users finish composing.
    """

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Note Saved!")
            return redirect('/note_box')

        else:
            # compose is bad, notify user
            for error, data in form.errors.items():
                if error == 'title':
                    messages.error(request, 'Invalid title: Title cannot be empty!')
                    continue

                messages.error(request, data[0])

    else:
        form = NoteForm(initial={
            'title': 'Untitled Note',
            'user': request.user.username
        })

    return render(request, 'notes_compose.html', {
        'user': request.user,
        'form': form
    })


@login_required
def note_box(request):
    """
    Home page of Simple Note. Serves the user's Notes.
    """

    # get all emails received by the user that have been sent
    notes = Note.objects.all().filter(user=request.user)

    return render(request, 'notes_inbox.html', {
        'user': request.user,
        'notes': notes
    })


@login_required
def view_note(request, note_uid):
    """
    Handles serving individual note pages.
    """

    # fetch the requested email from the DB
    note = Note.objects.get(uid=note_uid)

    return render(request, 'view_notes.html', {
        'user': request.user,
        'note': note
    })


