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

class LiveGameDataScraper(object):
    def __init__(self, url):
        self.url = url

    def scrape(self):
        response = requests.get(self.url)
        event_data = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        event_cells = soup.find_all("a", {"class": "event-cell-link"})
        for event in event_cells:
            event_id = event.get('href')
            if not event_id in event_data:
                event_data[event_id] = {'event_id': event_id, 'home_team_score': None, 'away_team_score': None,
                                        'time': None, 'period': None, 'value': None}
            team_name = event.find("span", {"class": "event-cell__name"})
            team_string = 'away_team'
            if 'away_team' in event_data[event_id]:
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
        task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': tasks_v2.HttpMethod.POST,
                'relative_uri': '/save_draftkings_data'
            }
        }
        if event_data is not None:
            if isinstance(event_data, dict):
                # Convert dict to JSON string
                payload = json.dumps(event_data)
                # specify http content-type to application/json
                task["app_engine_http_request"]["headers"] = {"Content-type": "application/json",
                                                              "'X-CSRFToken'": ""}
            # The API expects a payload of type bytes.
            converted_payload = payload.encode()

            # Add the payload to the request.
            task['app_engine_http_request']['body'] = converted_payload
            print(converted_payload)
        response = client.create_task(parent=parent, task=task)
        return event_data
