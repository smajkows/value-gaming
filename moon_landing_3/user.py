from google.cloud import ndb

client = ndb.Client()


class NdbBraintreePlan(ndb.PolyModel):
    braintree_id = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    created_at = ndb.DateProperty(required=True)
    description = ndb.StringProperty(required=True)
    price = ndb.FloatProperty(required=True)
    cancel_date = ndb.DateProperty()
    followers_allowed = ndb.FloatProperty(default=1)


with client.context():
    class NdbUser(ndb.PolyModel):
        firebase_id = ndb.StringProperty()
        screen_name = ndb.StringProperty()
        linked_accounts = ndb.KeyProperty(repeated=True)
        followed_accounts = ndb.KeyProperty(repeated=True)
        braintree_plan = ndb.KeyProperty(default=ndb.Key(NdbBraintreePlan, 'free_plan'))  # the user's current plan they are subscribed to
        subscription = ndb.KeyProperty()


class NdbBraintreeSubscription(ndb.PolyModel):
    plan = ndb.KeyProperty(required=True)  # the plan that the user purchased/canceled
    user = ndb.KeyProperty(required=True)  # user who the sub was purchased by
    subscription_id = ndb.StringProperty(required=True)

    def _post_put_hook(self, future):
        user = self.user.get()
        user_current_sub = user.subscription.get()
        plan = user_current_sub.plan.get()
        # when a subscription is put check that the user's current subscription is not getting more follows than
        # is allowed
        if len(user.followed_accounts) >= plan.followers_allowed:
            user.followed_accounts = user.followed_accounts[:plan.followers_allowed]
            user.put()
        return