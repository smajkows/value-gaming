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
                 projected_total, moneyline_plus_odds, moneyline_minus_odds, spread_line, spread_plus_odds,
                 spread_minus_odds, over_under_line, over_under_O_odds, over_under_U_odds, sport_id, league_id,
                 subcategory_id):
        self.home_team = home_team
        self.away_team = away_team
        self.time = time
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.period = period
        self.source = source
        self.event_id = event_id
        self.projected_total = projected_total
        self.moneyline_plus_odds = moneyline_plus_odds
        self.moneyline_minus_odds = moneyline_minus_odds
        self.spread_line = spread_line
        self.spread_plus_odds = spread_plus_odds
        self.spread_minus_odds = spread_minus_odds
        self.over_under_line = over_under_line
        self.over_under_O_odds = over_under_O_odds
        self.over_under_U_odds = over_under_U_odds
        self.sport_id = sport_id,
        self.league_id = league_id,
        self.subcategory_id = subcategory_id

    def to_dict(self, parse_time=True):
        result_dict = {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'time': self.time,
            'home_team_score': self.home_team_score,
            'away_team_score': self.away_team_score,
            'period': self.period,
            'source': self.source,
            'event_id': self.event_id,
            'projected_total': self.projected_total,
            'moneyline_plus_odds': self.moneyline_plus_odds,
            'moneyline_minus_odds': self.moneyline_minus_odds,
            'spread_line': self.spread_line,
            'spread_plus_odds': self.spread_plus_odds,
            'spread_minus_odds': self.spread_minus_odds,
            'over_under_line': self.over_under_line,
            'over_under_O_odds': self.over_under_O_odds,
            'over_under_U_odds': self.over_under_U_odds,
            'sport_id': self.sport_id[0],  # these are tuples first element is the right int, idk why
            'league_id': self.league_id[0],
            'subcategory_id': self.subcategory_id
        }
        if parse_time:
            split_time = self.time.rsplit(":")
            result_dict['time'] = (int(split_time[0]) * 60) + int(split_time[1]),  # convert minutes:seconds to seconds
        return result_dict


class LiveGameDataDraftkings(LiveGameData):
    source = 'Draftkings'
    collection = u'College_Basketball_Drafkings_LiveGames'

    def __init__(self, home_team, away_team, time, home_team_score, away_team_score, period, source, event_id,
                 projected_total, moneyline_plus_odds, moneyline_minus_odds, spread_line, spread_plus_odds,
                 spread_minus_odds, over_under_line, over_under_O_odds, over_under_U_odds, sport_id, league_id,
                 subcategory_id):
        super().__init__(home_team, away_team, time, home_team_score, away_team_score, period, source, event_id,
                 projected_total, moneyline_plus_odds, moneyline_minus_odds, spread_line, spread_plus_odds,
                 spread_minus_odds, over_under_line, over_under_O_odds, over_under_U_odds, sport_id, league_id,
                 subcategory_id)

    def populate_and_save(self):
        obj_dict = self.to_dict()
        db.collection('{}_{}'.format(self.collection, obj_dict.get('league_id'))).add(obj_dict)
