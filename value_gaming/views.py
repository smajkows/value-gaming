from django.http import HttpResponse
from django.template import loader
from django.views import View
import json


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
        context = {

        }
        return HttpResponse(template.render(context, request))


class OverUnderJSONHandler(View):

    def get(self, request):

        context = [
            {'home_team': 'Mavericks', 'away_team': 'Pistons', 'value': 100, 'name': 'NBA Dallas @ Detroit'},
            {'home_team': 'Lakers', 'away_team': 'Bulls', 'value': 80, 'name': 'NBA LA @ Chicago'}
        ]
        print(context)
        return HttpResponse(json.dumps(context))