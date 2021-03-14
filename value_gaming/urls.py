from django.contrib import admin
from django.urls import path

from value_gaming.views import OverUnderJSONHandler, landing, OverUnderHandler, write_data_to_firebase_collection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing),
    path('overunder', OverUnderHandler.as_view()),
    path('overunder_value', OverUnderJSONHandler.as_view()),
    path('empty', landing),
    path('save_draftkings_data', write_data_to_firebase_collection)
]
