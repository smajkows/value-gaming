from google.cloud import ndb

client = ndb.Client()


class NdbBraintreePlan(ndb.PolyModel):
    braintree_id = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    created_at = ndb.DateProperty(required=True)
    description = ndb.StringProperty(required=True)
    price = ndb.FloatProperty(required=True)
    cancel_date = ndb.DateProperty()
    followers_allowed = ndb.IntegerProperty(default=1)


class NdbUser(ndb.PolyModel):
    firebase_id = ndb.StringProperty()
    screen_name = ndb.StringProperty()
    linked_accounts = ndb.KeyProperty(repeated=True)
    followed_accounts = ndb.KeyProperty(repeated=True)
    braintree_plan = ndb.KeyProperty(default=ndb.Key(NdbBraintreePlan, 'free_plan'))  # the user's current plan they are subscribed to
    subscription = ndb.KeyProperty()

    def check_subscription_status(self):
        if self.subscription:
            user_current_sub = self.subscription.get()
            if user_current_sub:
                plan = user_current_sub.plan.get()
                if plan:
                    # when a subscription is put check that the user's current subscription is not getting more follows than
                    # is allowed
                    if len(self.followed_accounts) >= plan.followers_allowed:
                        self.followed_accounts = self.followed_accounts[:int(plan.followers_allowed)]
                        self.put()
        return



class NdbBraintreeSubscription(ndb.PolyModel):
    plan = ndb.KeyProperty(required=True)  # the plan that the user purchased/canceled
    user = ndb.KeyProperty(required=True)  # user who the sub was purchased by
    subscription_id = ndb.StringProperty(required=True)

    def _post_put_hook(self, future):
        user = self.user.get()
        if user:
            user.check_subscription_status()
        return
