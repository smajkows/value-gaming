import braintree
from env_util import get_braintree_env_variables

BT_ENVIRONMENT, BT_MERCHANT_ID, BT_PUBLIC_KEY, BT_PRIVATE_KEY = get_braintree_env_variables()


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=BT_ENVIRONMENT,
        merchant_id=BT_MERCHANT_ID,
        public_key=BT_PUBLIC_KEY,
        private_key=BT_PRIVATE_KEY
    )
)

def get_plans():
    return gateway.plan.all()

def generate_client_token(customer_id=None):
    options = {}
    customer = gateway.customer.find(customer_id)
    if customer:
        options = {"customer_id": customer.id}
    token = gateway.client_token.generate(options)
    return token

def transact(options):
    return gateway.transaction.sale(options)

def create_subscription(options):
    return gateway.subscription.create(options)

def find_subscription(sub_id):
    return gateway.subscription.find(sub_id)

def cancel_subscription(sub_id):
    return gateway.subscription.cancel(sub_id)

def customer_create(options):
    return gateway.customer.create(options)

def customer_find(customer_id):
    return gateway.customer.find(customer_id)

def payment_method(options):
    return gateway.payment_method.create(options)

def find_transaction(id):
    return gateway.transaction.find(id)
