from django.urls import path

from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('compose', views.compose, name='compose'),
    path('<str:folder>', views.inbox, name='inbox')
]
