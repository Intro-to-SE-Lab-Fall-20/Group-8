from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # folder views (inbox, outbox, etc.)
    path('', views.inbox, name='inbox'),
    path('outbox', views.outbox, name='outbox'),

    # view email
    path('view/<str:email_uid>', views.view_email, name='view_email'),

    # compose and forward
    path('compose', views.compose, name='compose'),
    path('forward', views.forward, name='forward'),
    path('forward/<str:email_uid>', views.forward, name='forward'),

    # search
    path('search/', views.search, name='search'),

    # user auth
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
]

# media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)