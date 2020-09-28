from django.urls import path

from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('outbox', views.outbox, name='outbox'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('compose', views.compose, name='compose')
]
