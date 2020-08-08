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
from django.views.decorators.csrf import csrf_exempt

from moon_landing_3.views import landing, login, AuthHandler, AuthCallbackHandler, datastore_test_page, HomePageHandler,\
    DailyAccountPoll, LeaderboardPageHandler, LeaderboardPageHandler2, AccountPageHandler, AccountDataHandler,\
    HomePageJson, PlaidToken, PlaidAccountCreation, PlaidTransactionWebhook, ChangeUsername, FollowAccountHandler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login),
    path('follow/account', FollowAccountHandler.as_view()),
    path('change/username', ChangeUsername.as_view()),
    path('item/plaid/webhook', csrf_exempt(PlaidTransactionWebhook.as_view())),
    path('account_creation', PlaidAccountCreation.as_view()),
    path('plaid/token', PlaidToken.as_view()),
    path('login/', login),
    path('home', HomePageHandler.as_view()),
    path('home_accounts/', HomePageJson.as_view()),
    path('login/', login),
    path('datastore-tester', datastore_test_page),
    path('auth/<str:platform>/', AuthHandler.as_view()),
    path('callback/<str:platform>', AuthCallbackHandler.as_view()),
    path('daily/account_poll', DailyAccountPoll.as_view()),
    path('leaderboard', LeaderboardPageHandler.as_view()),
    path('account_data/<str:account_id>', AccountDataHandler.as_view()),
    path('leaderboard2', LeaderboardPageHandler2.as_view()),
    path('account/page/<str:account_id>', AccountPageHandler.as_view())
]
