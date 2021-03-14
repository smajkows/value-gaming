from django.contrib import admin
from django.urls import path

from value_gaming.views import OverUnderJSONHandler, login, OverUnderHandler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login),
    path('overunder', OverUnderHandler.as_view()),
    path('overunder_value', OverUnderJSONHandler.as_view())
]
