"""time_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path, include
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    # The home page is cached for 1 hour since it doesn't change that often
    path(
        '',
        cache_page(0 * 60, key_prefix='project_home')(HomeView.as_view()),
        name='home'
    ),
    path('admin/', admin.site.urls),

    # The lines below must be put above path('accounts/', include('django.contrib.auth.urls')),
    # Otherwise the built-in password reset process will not be overwritten
    path('accounts/password_reset/', PasswordResetFormView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/',
         views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_done'),
    path('accounts/login/', views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),

    # Define the following built-in account authentication urls:
    # accounts/login/ [name='login']
    # accounts/logout/ [name='logout']
    # accounts/password_change/ [name='password_change']
    # accounts/password_change/done/ [name='password_change_done']
    # accounts/password_reset/ [name='password_reset']
    # accounts/password_reset/done/ [name='password_reset_done']
    # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # accounts/reset/done/ [name='password_reset_complete']
    path('accounts/', include('django.contrib.auth.urls')),

    # The thank-you page is cached forever since it doesn't change at all
    path(
        'thank_you/',
        cache_page(None, key_prefix='thank_you')(ThankYouView.as_view()),
        name='thank_you'
    ),
    path('registration/', RegistrationFormView.as_view(), name='registration'),
    path('update_user/<int:pk>/', UserUpdateView.as_view(), name='update_user'),

    # The classic tracker app
    path('classic_tracker/', include('classic_tracker.urls'), name='classic_tracker'),

    # Django debug toolbar
    path('__debug__/', include('debug_toolbar.urls')),
]

handler404 = NotFoundView.as_view()
