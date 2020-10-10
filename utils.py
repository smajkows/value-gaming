import os


def get_braintree_url():
    domain = os.getenv("BRAINTREE_MODULE_URL", None)
    if not domain:
        domain = 'http://127.0.0.1:4567'
    return domain