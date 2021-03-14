from django.http import HttpResponse
from django.template import loader
from django.views import View
from value_gaming.Draftkings.LiveGameScraper import LiveGameDataScraper
import json
from value_gaming.models.game_events import LiveGameDataDraftkings
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def write_data_to_firebase_collection(request):
    """Log the request payload."""
    payload = json.loads(request.body)
    for key, item in payload.items():
        live_data = LiveGameDataDraftkings(
                    home_team=item.get('home_team'),
                    away_team=item.get('away_team'),
                    time=item.get('time'),
                    home_team_score=item.get('home_team_score'),
                    away_team_score=item.get('away_team_score'),
                    period=item.get('period'),
                    source='Draftkings',
                    event_id=item.get('event_id'),
                    projected_total=None
                )
        live_data.populate_and_save()
    return HttpResponse(json.dumps('Done'))


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