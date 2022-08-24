from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout_user'),
    path('register', views.register, name='register'),
    path('activate-user/<uidb64>/<token>', views.activate_user, name='activate'),
]
