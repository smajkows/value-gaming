from google.cloud import ndb


class NdbUser(ndb.PolyModel):
    firebase_id = ndb.StringProperty()
    screen_name = ndb.StringProperty()
    linked_accounts = ndb.KeyProperty(repeated=True)
    followed_accounts = ndb.KeyProperty(repeated=True)
    braintree_plan = ndb.KeyProperty()  # the user's current plan they are subscribed to


class NdbBraintreePlan(ndb.PolyModel):
    braintree_id = ndb.StringProperty(required=True)
    creation_date = ndb.DateProperty(required=True)
    price = ndb.FloatProperty(required=True)
    cancel_date = ndb.DateProperty()


class NdbPlanAction(ndb.PolyModel):
    plan = ndb.KeyProperty(required=True)  # the plan that the user purchased/canceled
    user = ndb.KeyProperty(required=True)  # user who made the purchase/cancelation
    price = ndb.FloatProperty(required=True)  # monthly price at the time of purchase
    action = ndb.StringProperty(required=True, choices=['purchase', 'cancel'])
    date = ndb.DateProperty(required=True)  # the date the action occurred
