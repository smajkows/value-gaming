"""moon_landing_3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path

from moon_landing_3.views import landing, login, AuthHandler, AuthCallbackHandler, datastore_test_page, HomePageHandler,\
    DailyAccountPoll, LeaderboardPageHandler, AccountPageHandler, ReactApp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('react/', ReactApp.as_view()),
    path('home', HomePageHandler.as_view()),
    path('', landing),
    path('login/', login),
    path('datastore-tester', datastore_test_page),
    path('auth/<str:platform>/', AuthHandler.as_view()),
    path('callback/<str:platform>', AuthCallbackHandler.as_view()),
    path('daily/account_poll', DailyAccountPoll.as_view()),
    path('leaderboard', LeaderboardPageHandler.as_view()),
    path('account/page/<str:account_id>', AccountPageHandler.as_view())
]
