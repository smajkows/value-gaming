from django.http import HttpResponse
from django.template import loader
from django.views import View
from value_gaming.Draftkings.LiveGameScraper import LiveGameDataScraper
import json
from value_gaming.models.game_events import LiveGameDataDraftkings
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore


db = firestore.client()

@csrf_exempt
def write_data_to_firebase_collection(request):
    """Log the request payload."""
    payload = json.loads(request.body)
    for key, item in payload.items():
        print(item)
        if item.get('home_team_score'):
            # only save the live games right now since this is specfically for Livegame data and non-live game
            # data doesnt need to be stored on every load since there are no scores being populated which is whats
            # needed for training data
            live_data = LiveGameDataDraftkings(
                home_team=item.get('home_team'),
                away_team=item.get('away_team'),
                time=item.get('time'),
                home_team_score=item.get('home_team_score'),
                away_team_score=item.get('away_team_score'),
                period=item.get('period'),
                source='Draftkings',
                event_id=item.get('event_id'),
                projected_total=None,
                moneyline_plus_odds=item.get('moneyline_plus').get('odds') if item.get('moneyline_plus') else None,
                moneyline_minus_odds=item.get('moneyline_minus').get('odds') if item.get('moneyline_minus') else None,
                spread_line=float(item.get('spread_plus').get('line')) if item.get('spread_plus') else None,
                spread_plus_odds=float(item.get('spread_plus').get('odds')) if item.get('spread_plus') else None,
                spread_minus_odds=float(item.get('spread_minus').get('odds')) if item.get('spread_minus') else None,
                over_under_line=float(item.get('U').get('line')) if item.get('U') else None,
                over_under_O_odds=float(item.get('O').get('odds')) if item.get('O') else None,
                over_under_U_odds=float(item.get('U').get('odds')) if item.get('U') else None,
                sport_id=item.get('sport_id'),
                league_id=item.get('league_id'),
                subcategory_id=item.get('subcategory_id')
            )
            live_data.populate_and_save()
    return HttpResponse(json.dumps('Done'))

@csrf_exempt
def parse_raw_data(data):
    parsed_data = []
    for key in data.keys():
        item = data[key]
        if item.get('home_team_score'):
            live_data = LiveGameDataDraftkings(
                home_team=item.get('home_team'),
                away_team=item.get('away_team'),
                time=item.get('time'),
                home_team_score=item.get('home_team_score'),
                away_team_score=item.get('away_team_score'),
                period=item.get('period'),
                source='Draftkings',
                event_id=item.get('event_id'),
                projected_total=None,
                moneyline_plus_odds=item.get('moneyline_plus').get('odds') if item.get('moneyline_plus') else None,
                moneyline_minus_odds=item.get('moneyline_minus').get('odds') if item.get('moneyline_minus') else None,
                spread_line=float(item.get('spread_plus').get('line')) if item.get('spread_plus') else None,
                spread_plus_odds=float(item.get('spread_plus').get('odds')) if item.get('spread_plus') else None,
                spread_minus_odds=float(item.get('spread_minus').get('odds')) if item.get('spread_minus') else None,
                over_under_line=float(item.get('U').get('line')) if item.get('U') else None,
                over_under_O_odds=float(item.get('O').get('odds')) if item.get('O') else None,
                over_under_U_odds=float(item.get('U').get('odds')) if item.get('U') else None,
                sport_id=item.get('sport_id'),
                league_id=item.get('league_id'),
                subcategory_id=item.get('subcategory_id')
            )
            parsed_data.append(live_data.to_dict(parse_time=False))
    return parsed_data


def landing(request):
    template = loader.get_template('react.html')
    context = {}
    return HttpResponse(template.render(context, request))


def login(request):
    template = loader.get_template('react.html')
    context = {}
    return HttpResponse(template.render(context, request))


class BaseReactHandler(View):
    template = 'react.html'

    def get(self, request):
        template = loader.get_template(self.template)
        context = {}
        return HttpResponse(template.render(context, request))


class OverUnderJSONHandler(View):

    def get(self, request):
        data = LiveGameDataScraper(
            url='https://sportsbook.draftkings.com/leagues/basketball/103?category=game-lines&subcategory=game').scrape()
        context = parse_raw_data(data)
        #context = [data[x] for x in data.keys()]
        print(context)
        return HttpResponse(json.dumps({'bets': context}))


class PastResultsHandler(View):

    def get(self, request):
        game_list = []
        games = db.collection(u'College_Basketball_Drafkings_LiveGames_103').limit(5).stream()
        for game in games:
            game_list.append(game.to_dict())
        return HttpResponse(json.dumps({'recent_games': game_list}))


def pull_draftkings(request):
    for league_id in ['103', '3230960']:
        data = LiveGameDataScraper(
            url='https://sportsbook.draftkings.com/leagues/basketball/{}?category=game-lines&subcategory=game'
                .format(league_id)).scrape()
    return HttpResponse(json.dumps('polled'))