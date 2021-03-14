import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': 'value-gaming',
})

db = firestore.client()


class LiveGameData(object):
    def __init__(self, home_team, away_team, time, home_team_score, away_team_score, period, source, event_id,
                 projected_total):
        self.home_team = home_team
        self.away_team = away_team
        self.time = time
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.period = period
        self.source = source
        self.event_id = event_id
        self.projected_total = projected_total

    def to_dict(self):
        result_dict = {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'time': self.time,  # TODO: change this to seconds left
            'home_team_score': self.home_team_score,
            'away_team_score': self.away_team_score,
            'period': self.period,
            'source': self.source,
            'event_id': self.event_id,
            'projected_total': self.projected_total
        }
        return result_dict


class LiveGameDataDraftkings(LiveGameData):
    source = 'Draftkings'
    collection = u'College_Basketball_Drafkings_LiveGames'

    def __init__(self, home_team, away_team, time, home_team_score, away_team_score, period, source, event_id,
                 projected_total):
        super().__init__(home_team, away_team, time, home_team_score, away_team_score, period, source, event_id,
                         projected_total)

    def populate_and_save(self):
        db.collection(self.collection).add(self.to_dict())