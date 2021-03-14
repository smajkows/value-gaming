import requests
from bs4 import BeautifulSoup


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
            team_string = 'home_team'
            if 'home_team' in event_data[event_id]:
                team_string = 'away_team'
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
        return event_data
