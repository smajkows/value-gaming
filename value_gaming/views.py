from django.http import HttpResponse
from django.template import loader
from django.views import View
from value_gaming.Draftkings.LiveGameScraper import LiveGameDataScraper
import json

def write_data_to_firebase_collection(request):
    """Log the request payload."""
    payload = request.get_data(as_json=True)

    return

def landing(request):
    template = loader.get_template('react.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    template = loader.get_template('react.html')
    context = {}
    return HttpResponse(template.render(context, request))


class OverUnderHandler(View):
    template = 'react.html'

    def get(self, request):
        template = loader.get_template(self.template)
        context = {}
        return HttpResponse(template.render(context, request))


class OverUnderJSONHandler(View):

    def get(self, request):
        data = LiveGameDataScraper(url='https://sportsbook.draftkings.com/leagues/basketball/3230960?category=game-lines&subcategory=game').scrape()
        context = [data[x] for x in data.keys()]
        return HttpResponse(json.dumps(context))