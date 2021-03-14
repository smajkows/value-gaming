from django.contrib import admin
from django.urls import path

from value_gaming.views import OverUnderJSONHandler, landing, login, OverUnderHandler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing),
    path('overunder', OverUnderHandler.as_view()),
    path('overunder_value', OverUnderJSONHandler.as_view()),
    path('empty', landing)
]
