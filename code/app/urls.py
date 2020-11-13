from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # splash page
    path('', views.splash, name='splash'),

    # folder views (inbox, outbox, etc.)
    path('inbox', views.inbox, name='inbox'),
    path('outbox', views.outbox, name='outbox'),

    # view email
    path('view/<str:email_uid>', views.view_email, name='view_email'),

    # compose and forward
    path('compose', views.compose, name='compose'),
    path('forward', views.forward, name='forward'),
    path('forward/<str:email_uid>', views.forward, name='forward'),

    # search
    path('search/', views.search, name='search'),

    # master auth
    path('login', views.master_login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('reset_password', views.reset_password, name= 'reset_password'),

    # email auth
    path('email_login', views.email_login, name='email_login'),
    path('email_logout', views.email_logout, name='email_logout'),
]

# media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)