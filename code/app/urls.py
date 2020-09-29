from django.urls import path

from . import views

urlpatterns = [
    # folder views (inbox, outbox, etc.)
    path('', views.inbox, name='inbox'),
    path('outbox', views.outbox, name='outbox'),

    # compose
    path('compose', views.compose, name='compose'),

    # search
    path('search/', views.search, name='search'),

    # user auth
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
]
