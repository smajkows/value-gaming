import requests
from bs4 import BeautifulSoup
from google.cloud import tasks_v2
import json

# Create a client.
client = tasks_v2.CloudTasksClient()

# TODO(developer): Uncomment these lines and replace with your values.
project = 'value-gaming'
queue = 'firebase-writes'
location = 'us-central1'
# Construct the fully qualified queue name.
parent = client.queue_path(project, location, queue)

ENUM = {'+': 'plus', '-': 'minus'}


class LiveGameDataScraper(object):
    def __init__(self, url):
        self.url = url
        self.event_data = {}

    def scrape_outcomes(self, soup):
        event_data = self.event_data
        outcome_cells = soup.find_all("div", {"class": "sportsbook-outcome-cell"})
        for outcome in outcome_cells:
            outcome_body = outcome.find("div", {"class": "sportsbook-outcome-cell__body"})
            body_dict = json.loads(outcome_body.get("data-tracking"))
            print(body_dict)
            event_id = body_dict.get('eventId')
            event_data[event_id]['sport_id'] = body_dict.get('sportName')
            event_data[event_id]['league_id'] = body_dict.get('leagueName')
            event_data[event_id]['subcategory_id'] = body_dict.get('subcategoryId')
            if not event_id in event_data:
                print('event_id {}. type {}'.format(event_id, type(event_id)))
                print('new event id when scraping outcomes. wont process data for this event')
                continue
            label = outcome.find("span", {"class": "sportsbook-outcome-cell__label"})
            line_cell = outcome.find("span", {"class": "sportsbook-outcome-cell__line"})
            label_text = self.parse_label(label, line_cell)
            line = getattr(line_cell, 'text') if line_cell else None
            line_odds_cell = outcome.find("span", {"class": "sportsbook-odds"})
            line_odds = getattr(line_odds_cell, 'text') if line_odds_cell else None

            if label_text == 'spread' and line:
                label_text = '{}_{}'.format(label_text, ENUM[line[0]])
            if label_text == 'moneyline':
                label_text = '{}_{}'.format(label_text, ENUM[line_odds[0]])

            event_data[event_id][label_text] = {'line': line, 'odds': line_odds}
        return event_data

    def parse_label(self, label, line_cell):
        if not (label or line_cell):
            # if both the label and label container are missing its the moneyline
            return 'moneyline'

        if not label:
            return 'spread'

        return label.text

    def scrape(self):
        response = requests.get(self.url)
        event_data = self.event_data
        soup = BeautifulSoup(response.text, 'html.parser')
        event_cells = soup.find_all("a", {"class": "event-cell-link"})
        for event in event_cells:
            event_id = event.get('href')
            event_id = int(event_id.rsplit("/")[-1])
            if not event_id in event_data:
                event_data[event_id] = {'event_id': event_id, 'home_team_score': None, 'away_team_score': None,
                                        'time': None, 'period': None, 'value': None}
            team_name = event.find("span", {"class": "event-cell__name"})
            team_string = 'away_team'
            if 'away_team' in event_data[event_id].keys():
                team_string = 'home_team'
            event_data[event_id][team_string] = team_name.text
            score_string = '{}_score'.format(team_string)
            is_live = event.find("span", {"class": "sportsbook__icon--live"})
            if is_live:
                team_score = event.find("span", {"class": "event-cell__score"})
                event_data[event_id][score_string] = team_score.text
                time = event.find("span", {"class": "event-cell__time"})
                event_data[event_id]['time'] = time.text
                period = event.find("span", {"class": "event-cell__period"})
                event_data[event_id]['period'] = period.text

        event_data = self.scrape_outcomes(soup)

        task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': tasks_v2.HttpMethod.POST,
                'relative_uri': '/save_draftkings_data'
            }
        }
        if event_data is not None:
            payload = json.dumps(event_data)
            # specify http content-type to application/json
            task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
            # The API expects a payload of type bytes.
            converted_payload = payload.encode()
            # Add the payload to the request.
            task['app_engine_http_request']['body'] = converted_payload
        response = client.create_task(parent=parent, task=task)
        return event_data
