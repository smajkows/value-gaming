from django.contrib import admin
from django.urls import path

from value_gaming.views import OverUnderJSONHandler, landing, BaseReactHandler, write_data_to_firebase_collection, \
    pull_draftkings, PastResultsHandler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing),
    path('overunder', BaseReactHandler.as_view()),
    path('past', BaseReactHandler.as_view()),
    path('overunder_value', OverUnderJSONHandler.as_view()),
    path('empty', landing),
    path('save_draftkings_data', write_data_to_firebase_collection),
    path('pull_and_save_draftkings_data', pull_draftkings),
    path('past_results', PastResultsHandler.as_view())
]
