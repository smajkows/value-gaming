from google.cloud import ndb


class NdbUser(ndb.PolyModel):
    firebase_id = ndb.StringProperty()
    screen_name = ndb.StringProperty()
    linked_accounts = ndb.KeyProperty(repeated=True)
    followed_accounts = ndb.KeyProperty(repeated=True)


